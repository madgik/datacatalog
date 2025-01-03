import * as d3 from 'd3';
import { HierarchyPointNode, HierarchyPointLink } from 'd3-hierarchy';

export function createTidyTree(
  providedPath:any,
  data: any,
  container: HTMLElement,
  onBreadcrumbUpdate: (path: string[]) => void,
  highlightedNode: any = null
): void {
  const originalData = JSON.parse(JSON.stringify(data)); // Save the original data
  const tooltip = d3.select(container).select('#tooltip');
  console.log('Tooltip:', tooltip);
  console.log('Tooltip Node:', tooltip.node());

  const showTooltip = (_event: MouseEvent, d: any) => {
    console.log('Tooltip triggered for node:', d.data);

    tooltip
      .html(() => {
        let tooltipContent = `<strong>Name:</strong> ${d.data.name || "N/A"}`;

        tooltipContent += d.data.code ? `<br><strong>Code:</strong> ${d.data.code}` : "";
        if (d.data.code) console.log('Code:', d.data.code); // Log code

        if (d.data.variableCount) {
          tooltipContent += `<br><strong>Variable Count:</strong> ${d.data.variableCount}`;
        } else {
          tooltipContent += d.data.description
            ? `<br><strong>Description:</strong> ${d.data.description}`
            : "";
          if (d.data.description) console.log('Description:', d.data.description); // Log description

          tooltipContent += d.data.type
            ? `<br><strong>Type:</strong> ${d.data.type}`
            : "";
          if (d.data.type) console.log('Type:', d.data.type); // Log type

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
        if (d.data.min) console.log('Min:', d.data.min); // Log min value

        tooltipContent += d.data.max ? `<br><strong>Max:</strong> ${d.data.max}` : "";
        if (d.data.max) console.log('Max:', d.data.max); // Log max value

        tooltipContent += d.data.units ? `<br><strong>Units:</strong> ${d.data.units}` : "";
        if (d.data.units) console.log('Units:', d.data.units); // Log units

        tooltipContent += d.data.methodology
          ? `<br><strong>Methodology:</strong> ${d.data.methodology}`
          : "";
        if (d.data.methodology) console.log('Methodology:', d.data.methodology); // Log methodology

        return tooltipContent;
      })
      .style("visibility", "visible")
      .style("top", `${_event.pageY + 10}px`)
      .style("left", `${_event.pageX + 10}px`);

    console.log('Tooltip position:', {
      top: `${_event.pageY + 10}px`,
      left: `${_event.pageX + 10}px`
    });
  };

const hideTooltip = () => {
  console.log('Tooltip hidden');
  tooltip.style("visibility", "hidden");
};



  // Add fullscreenchange event listener
  document.addEventListener('fullscreenchange', () => {
    const isFullScreen = document.fullscreenElement !== null;
    const fullScreenMultiplier = isFullScreen ? 1.25 : 1;

    // Update tree rendering to account for full-screen dimensions
    renderTree(data, fullScreenMultiplier);
  });

  const calculateMaxDepth = (node: any): number => {
    let maxDepth = 0;
    node.each((d: any) => {
      maxDepth = Math.max(maxDepth, d.depth);
    });
    return maxDepth - node.depth;
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

  // Render the tree
  const renderTree = (rootData: any, scaleMultiplier: number = 1) => {

    container.innerHTML = ''; // Clear existing visualization


    const baseWidth = 2500 * scaleMultiplier;
    const baseHeight = 1000 * scaleMultiplier;
    const dx = 10 * scaleMultiplier;
    const dy = baseWidth / 8;

    const root = d3.hierarchy(rootData);
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
    adjustedOffsetX = adjustedOffsetX - 700 * scaleMultiplier + dynamicWidth / 2.5

    const paddingX = 5, paddingY = 5;
    const verticalOffset = (2 * baseHeight - dynamicHeight)/ 8;

    // Ensure the offset is non-negative (only for smaller diagrams)
    const adjustedPaddingY = Math.max(paddingY, verticalOffset);
    const viewBoxWidth = dynamicWidth + paddingX * 2;
    const viewBoxHeight = dynamicHeight + paddingY * 2;

    const svg = d3.create('svg')
      .attr('width', baseWidth)
      .attr('height', dynamicHeight)
      .attr('viewBox', `${y0 - paddingX} ${x0 - paddingY} ${viewBoxWidth} ${viewBoxHeight}`)
      .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif;')

    const g = svg.append('g')
      .attr('transform', `translate(${adjustedOffsetX}, ${adjustedPaddingY})`);

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
        // Hide tooltip on double-click
        tooltip.style("visibility", "hidden");

        if (originalData === d.data) {
          console.log("Double-clicked node is already the current root, doing nothing.");
          return;
        }

        const newAvailableDepths = calculateMaxDepth(d);

        if (newAvailableDepths <= 0) {
          console.log("Double-clicked node has no depth, breadcrumb unchanged.");
          return;
        }

        providedPath.pop();
        const path = [...providedPath, ...getPathFromOriginalRootToNode(d.data)];
        onBreadcrumbUpdate(path);
        renderTree(d.data);
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
      }
      return calculateMaxDepth(d) > 0 ? '#007acc' : '#555'; // Other nodes based on depth
    })
    .attr('stroke', d => (highlightedNode && d.data.name === highlightedNode.name ? '#ff0000' : (d.depth === 0 ? '#2e7d32' : null))) // Highlighted stroke red
    .attr('r', d => {
      if (highlightedNode && d.data.name === highlightedNode.name) {
        return 6; // Highlighted node has a bigger radius
      }
      return d.depth === 0 ? 8 : (calculateMaxDepth(d) > 0 ? 5 : 2.5);
    });

    node.append('text')
      .attr('dy', '0.31em')
      .attr('x', d => (d.children ? -6 : 6))
      .attr('text-anchor', d => (d.children ? 'end' : 'start'))
      .text(d => d.data.name)
      .attr('stroke', d => (d.depth === 0 ? '#ffffff' : (d.depth > 0 && calculateMaxDepth(d) > 0 ? 'yellow' : 'white'))) // Root text gets white stroke
      .attr('paint-order', 'stroke')
      .style('font-size', d => (d.depth === 0 ? `${14}px` : (d.depth > 0 && calculateMaxDepth(d) > 0 ? `${12}px` : `${10}px`))) // Root has larger font size
      .style('font-weight', d => (d.depth === 0 ? 'bold' : 'normal')); // Bold font for root

    if (svg.node() !== null) {
      container.appendChild(svg.node() as Node);
    }
  };

  renderTree(data);
}
