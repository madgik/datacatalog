import * as d3 from 'd3';
import { HierarchyPointNode, HierarchyPointLink } from 'd3-hierarchy';

export function createTidyTree(
  providedPath: any,
  data: any,
  container: HTMLElement,
  onBreadcrumbUpdate: (path: string[]) => void,
  onAvailableDepthsUpdate: (newAvailableDepths: number) => void,
  highlightedNode: any = null,
  maxDepth: number | null
): void {
  const originalData = JSON.parse(JSON.stringify(data)); // Save the original data

  const tooltip = d3
    .select("body") // Append to body to avoid SVG clipping
    .append("div")
    .attr("id", "tooltip")
    .style("position", "absolute")
    .style("visibility", "hidden")
    .style("background-color", "rgba(0, 0, 0, 0.7)")
    .style("color", "white")
    .style("padding", "8px")
    .style("border-radius", "4px")
    .style("pointer-events", "none")
    .style("z-index", "1000");

  const showTooltip = (_event: MouseEvent, d: any) => {
    tooltip
      .html(() => {
        let tooltipContent = `<strong>Name:</strong> ${d.data.name || "N/A"}`;
        tooltipContent += d.data.code ? `<br><strong>Code:</strong> ${d.data.code}` : "";

        if (d.data.variableCount) {
          tooltipContent += `<br><strong>Variable Count:</strong> ${d.data.variableCount}`;
        } else {
          tooltipContent += d.data.description
            ? `<br><strong>Description:</strong> ${d.data.description}`
            : "";

          tooltipContent += d.data.type
            ? `<br><strong>Type:</strong> ${d.data.type}`
            : "";

          if (d.data.type === "nominal" && d.data.enumerations) {
            tooltipContent += `
              <p><strong>Enumerations:</strong></p>
              <ul class="enumerations-list">
                ${d.data.enumerations
                .map((enumItem: { label: string }) => `<li>${enumItem.label}</li>`)
                .join("")}
              </ul>
            `;
          }
        }

        tooltipContent += d.data.min ? `<br><strong>Min:</strong> ${d.data.min}` : "";
        tooltipContent += d.data.max ? `<br><strong>Max:</strong> ${d.data.max}` : "";
        tooltipContent += d.data.units ? `<br><strong>Units:</strong> ${d.data.units}` : "";
        tooltipContent += d.data.methodology
          ? `<br><strong>Methodology:</strong> ${d.data.methodology}`
          : "";

        return tooltipContent;
      })
      .style("visibility", "visible")
      .style("top", `${_event.pageY + 10}px`)
      .style("left", `${_event.pageX + 20}px`);
  };

  const hideTooltip = () => {
    console.log('Tooltip hidden');
    tooltip.style("visibility", "hidden");
  };

  const pruneTreeToDepth = (node: any, depth: number, maxDepth: number | null): void => {
    if (maxDepth !== null && depth >= maxDepth) {
      delete node.children;
    } else if (node.children) {
      node.children.forEach((child: any) => pruneTreeToDepth(child, depth + 1, maxDepth));
    }
  };

  const calculateMaxDepth = (node: any): number => {
    let maxDepth = 0;

    // Ensure `node` is a D3 hierarchy node
    const hierarchyNode = d3.hierarchy(node);

    hierarchyNode.each((d: any) => {
      maxDepth = Math.max(maxDepth, d.depth);
    });

    return maxDepth;
  };


  const findNodeInOriginalTree = (originalNode: any, targetNode: any): any => {
    if (originalNode.name === targetNode.name) {
      return originalNode;
    }
    if (originalNode.children) {
      for (const child of originalNode.children) {
        const found = findNodeInOriginalTree(child, targetNode);
        if (found) return found;
      }
    }
    return null;
  };

  const getPathFromOriginalRootToNode = (targetNode: any): string[] => {
    const findPath = (node: any, target: any, path: string[]): boolean => {
      path.push(node.name);
      if (node.name === target.name) {
        return true;
      }
      if (node.children) {
        for (const child of node.children) {
          if (findPath(child, target, path)) {
            return true;
          }
        }
      }
      path.pop();
      return false;
    };

    const path: string[] = [];
    findPath(originalData, targetNode, path);
    return path;
  };

  // Zoom and pan functionalities

  const renderTree = (rootData: any, maxDepth: number | null) => {
    container.innerHTML = ''; // Clear existing visualization

    const baseWidth = 2500;
    const baseHeight = 940;
    const dx = 10;
    const dy = baseWidth / 8;

    const root = d3.hierarchy(rootData);

    if (maxDepth == null) {
      onAvailableDepthsUpdate(calculateMaxDepth(root));
    }

    pruneTreeToDepth(root, 0, maxDepth); // Prune the tree to the max depth
    const tree = d3.tree<HierarchyPointNode<any>>().nodeSize([dx, dy]);

    root.sort((a, b) => d3.ascending(a.data.name, b.data.name));
    tree(root);

    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    root.each((d) => {
      if (typeof d.x === 'number') {
        x0 = Math.min(x0, d.x);
        x1 = Math.max(x1, d.x);
      }
      if (typeof d.y === 'number') {
        y0 = Math.min(y0, d.y);
        y1 = Math.max(y1, d.y);
      }
    });


    const dynamicHeight = Math.max(baseHeight, x1 - x0 + dx * 2 + 100);
    const dynamicWidth = y1 - y0 + dy * 2;
    const offsetFactor = dynamicWidth / baseWidth; // Calculate a ratio based on size
    const leftBias = Math.min(0.25, offsetFactor / 2); // Bias more for larger charts

    const offsetX = (baseWidth - dynamicWidth) / 2 * (1 - leftBias) - y0;


    // Ensure offset doesn't push too far left for large diagrams
    let adjustedOffsetX = Math.max(offsetX, -y0) + 50;
    adjustedOffsetX = adjustedOffsetX - 1000 + dynamicWidth / 2

    const paddingX = 10, paddingY = 10;
    const verticalOffset = (2.5 * baseHeight - dynamicHeight) / 8;

    // Ensure the offset is non-negative (only for smaller diagrams)
    const adjustedPaddingY = Math.max(paddingY, verticalOffset);
    const viewBoxWidth = dynamicWidth + paddingX * 2;
    const viewBoxHeight = dynamicHeight + paddingY * 2;

    const svg = d3.create('svg')
      .attr('width', baseWidth)
      .attr('height', dynamicHeight)
      .attr('viewBox', `${y0 - paddingX} ${x0 - paddingY} ${viewBoxWidth} ${viewBoxHeight}`)
      .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif; cursor: grab;');

    const g = svg.append('g')
      .attr('transform', `translate(${adjustedOffsetX}, ${adjustedPaddingY})`);

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 2]) // Allow zooming between 50% and 200%
      .on('zoom', (event) => g.attr('transform', event.transform));

    svg.call(zoom as any);

    // Render links
    g.append('g')
      .attr('fill', 'none')
      .attr('stroke', '#555')
      .attr('stroke-opacity', 0.4)
      .attr('stroke-width', 1.5)
      .selectAll('path')
      .data(root.links())
      .join('path')
      .attr(
        'd',
        d3.linkHorizontal<HierarchyPointLink<any>, HierarchyPointNode<any>>()
          .x(d => d.y)
          .y(d => d.x) as any
      );

    // Render nodes
    const node = g.append('g')
      .attr('stroke-linejoin', 'round')
      .attr('stroke-width', 3)
      .selectAll('g')
      .data(root.descendants())
      .join('g')
      .attr('transform', d => `translate(${d.y},${d.x})`)
      .style('cursor', 'pointer')
      .on("mouseover", (_event, d) => {
        showTooltip(_event, d);
        // Highlight clicked node
        highlightedNode = d;
        node.select("circle")
          .attr("stroke", null)
          .attr("stroke-width", 5);

        d3.select(_event.currentTarget).select("circle")
          .attr("stroke", "red")
          .attr("stroke-width", 3);
      })
      .on("dblclick", (_event, d) => {
        tooltip.style("visibility", "hidden");

        if (originalData === d.data) {
          console.log("Double-clicked node is already the current root, doing nothing.");
          return;
        }

        const originalSubtree = findNodeInOriginalTree(originalData, d.data);
        if (!originalSubtree) {
          console.error("Could not find the original subtree for the clicked node.");
          return;
        }

        // Use the updated `calculateMaxDepth` function
        const newAvailableDepths = calculateMaxDepth(originalSubtree);

        providedPath.pop();
        const path = [...providedPath, ...getPathFromOriginalRootToNode(d.data)];
        onAvailableDepthsUpdate(newAvailableDepths);
        onBreadcrumbUpdate(path);
        renderTree(d.data, newAvailableDepths);
      })
      .on("mouseleave", () => {
        hideTooltip()
      });

    node.append('circle')
      .attr('fill', d => {
        if (highlightedNode && d.data.name === highlightedNode.name) {
          return 'red'; // Highlight the node in red
        }
        if (d.depth === 0) {
          return '#4caf50'; // Root node gets green color
        } d.data.hasOwnProperty()
        return d.data.hasOwnProperty('variableCount') ? '#007acc' : '#555'; // Other nodes based on depth
      })
      .attr('stroke', d => (highlightedNode && d.data.name === highlightedNode.name ? '#ff0000' : (d.depth === 0 ? '#2e7d32' : null))) // Highlighted stroke red
      .attr('r', d => {
        if (highlightedNode && d.data.name === highlightedNode.name) {
          return 6; // Highlighted node has a bigger radius
        }
        return d.depth === 0 ? 8 : (d.data.hasOwnProperty('variableCount') ? 5 : 2.5);
      });

    node.append('text')
      .attr('dy', '0.31em')
      .attr('x', d => (d.children ? -6 : 6))
      .attr('text-anchor', d => (d.children ? 'end' : 'start'))
      .text(d => d.data.name)
      .attr('stroke', d => (d.depth === 0 ? '#ffffff' : (d.depth > 0 && d.data.hasOwnProperty('variableCount') ? 'yellow' : 'white'))) // Root text gets white stroke
      .attr('paint-order', 'stroke')
      .style('font-size', d => (d.depth === 0 ? `${14}px` : (d.depth > 0 && d.data.hasOwnProperty('variableCount') ? `${12}px` : `${10}px`))) // Root has larger font size
      .style('font-weight', d => (d.depth === 0 ? 'bold' : 'normal')); // Bold font for root

    if (svg.node() !== null) {
      container.appendChild(svg.node() as Node);
    }

  };
  renderTree(data, maxDepth);
}
