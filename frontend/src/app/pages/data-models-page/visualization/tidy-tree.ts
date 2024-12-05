import * as d3 from 'd3';
import { HierarchyPointNode, HierarchyPointLink } from 'd3-hierarchy';

export function createTidyTree(
  data: any,
  container: HTMLElement,
  onNodeClick: (node: any) => void,
  onBreadcrumbUpdate: (path: string[]) => void,
): void {
  const originalData = JSON.parse(JSON.stringify(data)); // Save the original data

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
  const renderTree = (rootData: any) => {
    container.innerHTML = ''; // Clear existing visualization

    const baseWidth = 1500;
    const baseHeight = 500;
    const dx = 10;
    const dy = baseWidth / 7.5;

    const root = d3.hierarchy(rootData);
    const tree = d3.cluster<HierarchyPointNode<any>>().nodeSize([dx, dy]);

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

    const dynamicHeight = Math.max(baseHeight, x1 - x0 + dx * 2);
    const dynamicWidth = y1 - y0 + dy * 2;
    const offsetX = Math.max(0, (baseWidth - dynamicWidth) / 3) - y0;

    const paddingX = 50, paddingY = 20;
    const viewBoxWidth = dynamicWidth + paddingX * 2;
    const viewBoxHeight = dynamicHeight + paddingY * 2;

    const svg = d3.create('svg')
      .attr('width', baseWidth)
      .attr('height', dynamicHeight)
      .attr('viewBox', `${y0 - paddingX} ${x0 - paddingY} ${viewBoxWidth} ${viewBoxHeight}`)
      .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif;');

    const g = svg.append('g')
      .attr('transform', `translate(${offsetX}, ${paddingY})`);

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
      .on('click', (event, d) => {
        onNodeClick(d.data);
      })
      .on('dblclick', (event, d) => {
        const path = getPathFromOriginalRootToNode(d.data);
        onBreadcrumbUpdate(path);
        renderTree(d.data); // Render the subtree as new root
      });

    node.append('circle')
      .attr('filter', d => (d.depth === 0 ? null : (d.depth > 0 && calculateMaxDepth(d) > 1 ? 'url(#glow)' : null))) // No glow for root
      .attr('title', d => `Name: ${d.data.name}\nDepth: ${d.depth}`)
      .attr('fill', d => (d.depth === 0 ? '#4caf50' : (d.depth > 0 && calculateMaxDepth(d) > 1 ? '#007acc' : '#555'))) // Root gets green color
      .attr('stroke', d => (d.depth === 0 ? '#2e7d32' : (d.depth > 0 && calculateMaxDepth(d) > 1 ? '#ffcc00' : null))) // Root gets dark green stroke
      .attr('r', d => (d.depth === 0 ? 8 : (d.depth > 0 && calculateMaxDepth(d) > 1 ? 5 : 2.5))); // Root has a larger radius

    node.append('text')
      .attr('dy', '0.31em')
      .attr('x', d => (d.children ? -6 : 6))
      .attr('text-anchor', d => (d.children ? 'end' : 'start'))
      .text(d => d.data.name)
      .attr('stroke', d => (d.depth === 0 ? '#ffffff' : (d.depth > 0 && calculateMaxDepth(d) > 1 ? 'yellow' : 'white'))) // Root text gets white stroke
      .attr('paint-order', 'stroke')
      .style('font-size', d => (d.depth === 0 ? `${14}px` : (d.depth > 0 && calculateMaxDepth(d) > 1 ? `${12}px` : `${10}px`))) // Root has larger font size
      .style('font-weight', d => (d.depth === 0 ? 'bold' : 'normal')); // Bold font for root

    if (svg.node() !== null) {
      container.appendChild(svg.node() as Node);
    }
  };

  renderTree(data);
}
