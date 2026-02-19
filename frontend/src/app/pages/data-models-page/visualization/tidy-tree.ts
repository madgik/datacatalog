import * as d3 from 'd3';
import { HierarchyPointNode, HierarchyPointLink } from 'd3-hierarchy';

export interface TreeControls {
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
}

export function createTidyTree(
  providedPath: any,
  data: any,
  container: HTMLElement,
  onBreadcrumbUpdate: (path: string[]) => void,
  onAvailableDepthsUpdate: (newAvailableDepths: number) => void,
  highlightedNode: any = null,
  maxDepth: number | null,
  isZoomEnabled: boolean = true,
  onZoomUpdate?: (level: number) => void
): TreeControls {
  const originalData = JSON.parse(JSON.stringify(data)); // Save the original data

  let tooltip: d3.Selection<HTMLDivElement, unknown, null, undefined> | null = null;

  const createTooltipElement = () => {
    tooltip?.remove();
    tooltip = d3
      .select(container)
      .append('div')
      .attr('class', 'chart-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('pointer-events', 'none')
      .style('z-index', '1000');
  };

  const ensureTooltip = () => {
    if (!tooltip) {
      createTooltipElement();
    }
  };

  const positionTooltip = (_event: MouseEvent) => {
    if (!tooltip) return;
    const tooltipNode = tooltip.node() as HTMLDivElement;
    if (!tooltipNode) return;
    const containerRect = container.getBoundingClientRect();
    const tooltipRect = tooltipNode.getBoundingClientRect();

    let left = _event.clientX - containerRect.left + 12;
    let top = _event.clientY - containerRect.top + 12;

    if (left + tooltipRect.width + 12 > containerRect.width) {
      left = Math.max(8, containerRect.width - tooltipRect.width - 12);
    }
    if (top + tooltipRect.height + 12 > containerRect.height) {
      top = Math.max(8, containerRect.height - tooltipRect.height - 12);
    }

    tooltip
      .style("left", `${left}px`)
      .style("top", `${top}px`);
  };

  const showTooltip = (_event: MouseEvent, d: any) => {
    ensureTooltip();
    tooltip!
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
      .style("visibility", "visible");
    positionTooltip(_event);
  };

  const hideTooltip = () => {
    tooltip?.style('visibility', 'hidden');
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

  const tooltipWrapper = () => {
    container.style.position = 'relative';
    createTooltipElement();
  };

  // Color palette from design system - using CSS variables directly for dark mode support
  const colors = {
    rootNode: 'var(--tree-root-color)',
    rootStroke: 'var(--tree-root-stroke)',
    parentNode: 'var(--tree-node-parent)',
    leafNode: 'var(--tree-node-leaf)',
    link: 'var(--tree-link-color)',
    highlight: 'var(--tree-highlight)',
    textMain: 'var(--text-main)',
    textStroke: 'var(--tree-text-stroke)',
  };

  const renderTree = (rootData: any, maxDepth: number | null) => {
    container.innerHTML = ''; // Clear existing visualization
    tooltipWrapper();

    // Layout constants
    const baseWidth = 2500;
    const baseHeight = 940;
    const nodeSpacingVertical = 12; // Space between nodes vertically
    const nodeSpacingHorizontal = baseWidth / 8; // Space between depth levels

    const root = d3.hierarchy(rootData);

    onAvailableDepthsUpdate(calculateMaxDepth(root));

    pruneTreeToDepth(root, 0, maxDepth);
    const tree = d3.tree<HierarchyPointNode<any>>().nodeSize([nodeSpacingVertical, nodeSpacingHorizontal]);

    root.sort((a, b) => d3.ascending(a.data.name, b.data.name));
    tree(root);

    // Calculate bounds
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

    const dynamicHeight = Math.max(baseHeight, x1 - x0 + nodeSpacingVertical * 2 + 100);
    const dynamicWidth = y1 - y0 + nodeSpacingHorizontal * 2;
    const offsetFactor = dynamicWidth / baseWidth;
    const leftBias = Math.min(0.25, offsetFactor / 2);

    const offsetX = (baseWidth - dynamicWidth) / 2 * (1 - leftBias) - y0;
    let adjustedOffsetX = Math.max(offsetX, -y0) + 50;
    adjustedOffsetX = adjustedOffsetX - 1000 + dynamicWidth / 2;

    const paddingX = 20, paddingY = 20;
    const verticalOffset = (2.5 * baseHeight - dynamicHeight) / 8;
    const adjustedPaddingY = Math.max(paddingY, verticalOffset);
    const viewBoxWidth = dynamicWidth + paddingX * 2;
    const viewBoxHeight = dynamicHeight + paddingY * 2;

    const svg = d3.create('svg')
      .attr('width', baseWidth)
      .attr('height', dynamicHeight)
      .attr('viewBox', `${y0 - paddingX} ${x0 - paddingY} ${viewBoxWidth} ${viewBoxHeight}`)
      .attr('style', `max-width: 100%; height: auto; font: 11px 'Inter', system-ui, sans-serif; cursor: grab;`);

    const g = svg.append('g')
      .attr('transform', `translate(${adjustedOffsetX}, ${adjustedPaddingY})`);

    // Clear highlights when clicking background
    svg.on('click', () => {
      g.selectAll('path')
        .attr('stroke', colors.link)
        .attr('stroke-width', 1.5)
        .style('filter', 'none');

      g.selectAll('text')
        .style('font-size', (n: any) => n.depth === 0 ? '18px' : (n.data.hasOwnProperty('variableCount') ? '16px' : '14px'))
        .style('font-weight', (n: any) => n.depth === 0 ? '700' : (n.data.hasOwnProperty('variableCount') ? '600' : '400'));
    });

    let zoomBehavior: d3.ZoomBehavior<SVGSVGElement, unknown> | null = null;
    let svgSelection: d3.Selection<SVGSVGElement, unknown, null, undefined> | null = null;

    if (isZoomEnabled) {
      zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.5, 2])
        .on('zoom', (event) => {
          g.attr('transform', event.transform);
          if (onZoomUpdate) {
            onZoomUpdate(event.transform.k);
          }
        });
      svg.call(zoomBehavior as any);
      svgSelection = svg as any;
    }

    // ... (rest of the rendering logic remains)

    // Render links with smooth curves
    g.append('g')
      .attr('fill', 'none')
      .attr('stroke', colors.link)
      .attr('stroke-width', 1.5)
      .selectAll('path')
      .data(root.links())
      .join('path')
      .attr(
        'd',
        d3.linkHorizontal<HierarchyPointLink<any>, HierarchyPointNode<any>>()
          .x(d => d.y)
          .y(d => d.x) as any
      )
      .style('transition', 'stroke 0.2s ease, filter 0.2s ease')
      .style('cursor', 'pointer');

    // Render nodes
    const node = g.append('g')
      .attr('stroke-linejoin', 'round')
      .attr('stroke-width', 3)
      .selectAll('g')
      .data(root.descendants())
      .join('g')
      .attr('transform', d => `translate(${d.y},${d.x})`)
      .style('cursor', 'pointer')
      .on("click", (_event, d) => {
        // Stop propagation to avoid interfering with other events
        _event.stopPropagation();

        // 1. Reset all links to default state
        g.selectAll('path')
          .attr('stroke', colors.link)
          .attr('stroke-width', 1.5)
          .style('filter', 'none');

        // 2. Reset all text sizes to default
        g.selectAll('text')
          .style('font-size', (n: any) => n.depth === 0 ? '18px' : (n.data.hasOwnProperty('variableCount') ? '16px' : '14px'))
          .style('font-weight', (n: any) => n.depth === 0 ? '700' : (n.data.hasOwnProperty('variableCount') ? '600' : '400'));

        // 3. Highlight links:
        // - Ancestor Path: Links where target is in the ancestor chain (path up to node)
        // - Children Paths: Links where source is the clicked node (paths down to children)
        const ancestors = new Set(d.ancestors());

        g.selectAll('path')
          .filter((link: any) => ancestors.has(link.target) || link.source === d)
          .attr('stroke', colors.parentNode)
          .attr('stroke-width', 2.5)
          .style('filter', `drop-shadow(0 0 4px ${colors.parentNode})`);

        // 4. Highlight Ancestor Text (Make it bigger)
        g.selectAll('text')
          .filter((n: any) => ancestors.has(n))
          .style('font-size', (n: any) => n.depth === 0 ? '22px' : (n.data.hasOwnProperty('variableCount') ? '20px' : '18px'))
          .style('font-weight', '800')
          .style('transition', 'all 0.3s ease');
      })
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
        tooltip?.style("visibility", "hidden");

        if (originalData === d.data) {
          console.log("Double-clicked node is already the current root, doing nothing.");
          return;
        }

        if (!d.data.hasOwnProperty('variableCount')) {
          console.log("Double-clicked node is not a parent, doing nothing.");
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

    // Add node circles with design system colors
    node.append('circle')
      .attr('fill', d => {
        if (highlightedNode && d.data.name === highlightedNode.name) {
          return colors.highlight;
        }
        if (d.depth === 0) {
          return colors.rootNode;
        }
        return d.data.hasOwnProperty('variableCount') ? colors.parentNode : colors.leafNode;
      })
      .attr('stroke', d => {
        if (highlightedNode && d.data.name === highlightedNode.name) {
          return colors.highlight;
        }
        return d.depth === 0 ? colors.rootStroke : 'transparent';
      })
      .attr('stroke-width', d => (d.depth === 0 ? 2 : 0))
      .attr('r', d => {
        if (highlightedNode && d.data.name === highlightedNode.name) {
          return 7;
        }
        return d.depth === 0 ? 9 : (d.data.hasOwnProperty('variableCount') ? 5 : 3);
      })
      .style('transition', 'all 0.15s ease')
      .style('filter', d => d.depth === 0 ? 'drop-shadow(0 2px 4px rgba(16, 185, 129, 0.3))' : 'none');

    // Add node labels with improved typography
    node.append('text')
      .attr('dy', '0.35em')
      .attr('x', d => (d.children ? -10 : 10))
      .attr('text-anchor', d => (d.children ? 'end' : 'start'))
      .text(d => d.data.name)
      .attr('fill', d => d.depth === 0 ? colors.rootNode : colors.textMain)
      .attr('stroke', colors.textStroke)
      .attr('stroke-width', 3)
      .attr('paint-order', 'stroke')
      .style('font-size', d => d.depth === 0 ? '24px' : (d.data.hasOwnProperty('variableCount') ? '16px' : '14px'))
      .style('font-weight', d => d.depth === 0 ? '700' : (d.data.hasOwnProperty('variableCount') ? '600' : '400'))
      .style('letter-spacing', '0.01em');

    if (svg.node() !== null) {
      container.appendChild(svg.node() as Node);
    }

    // Assign to closure variables for control access
    controls.zoomIn = () => {
      if (svgSelection && zoomBehavior) {
        svgSelection.transition().duration(300).call(zoomBehavior.scaleBy as any, 1.2);
      }
    };
    controls.zoomOut = () => {
      if (svgSelection && zoomBehavior) {
        svgSelection.transition().duration(300).call(zoomBehavior.scaleBy as any, 0.8);
      }
    };
    controls.resetZoom = () => {
      if (svgSelection && zoomBehavior) {
        svgSelection.transition().duration(750).call(zoomBehavior.transform as any, d3.zoomIdentity);
      }
    };

  };

  // Controls object that will be populated by renderTree
  const controls: TreeControls = {
    zoomIn: () => { },
    zoomOut: () => { },
    resetZoom: () => { }
  };

  renderTree(data, maxDepth);
  return controls;
}
