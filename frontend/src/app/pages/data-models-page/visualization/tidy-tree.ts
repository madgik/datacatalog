import * as d3 from 'd3';
import { HierarchyPointNode, HierarchyPointLink } from 'd3-hierarchy';

export function createTidyTree(data: any, container: HTMLElement, onNodeClick: (node: any) => void): void {
  const baseWidth = 1500; // Fixed width
  const baseHeight = 780; // Base height
  const dx = 10; // Vertical node spacing
  const dy = baseWidth / 5; // Horizontal node spacing

  // Prepare the tree layout
  const root = d3.hierarchy(data);
  const tree = d3.cluster<HierarchyPointNode<any>>().nodeSize([dx, dy]);

  root.sort((a, b) => d3.ascending(a.data.name, b.data.name));
  tree(root);

  // Calculate dynamic height based on the tree structure
  let x0 = Infinity;
  let x1 = -x0;

  root.each((d) => {
    if (typeof d.x === 'number') {
      x0 = Math.min(x0, d.x);
      x1 = Math.max(x1, d.x);
    }
  });

  const dynamicHeight = Math.max(baseHeight, x1 - x0 + dx * 2); // Ensure at least baseHeight

  // Create an SVG element
  const svg = d3.create('svg')
    .attr('width', baseWidth)
    .attr('height', dynamicHeight)
    .attr('viewBox', [-dy / 3, x0 - dx, baseWidth, dynamicHeight])
    .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif;');

  // The main group that will be zoomed and panned
  const g = svg.append('g');

  // Define zoom behavior
  const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 4]) // Define zoom scale limits
    .on('zoom', (event) => {
      g.attr('transform', event.transform); // Apply zoom and pan transformations
    });

  // Apply zoom behavior to the SVG, with an explicit cast to `any`
  svg.call(zoomBehavior as any);

  // Render the links
  g.append('g')
    .attr('fill', 'none')
    .attr('stroke', '#555')
    .attr('stroke-opacity', 0.4)
    .attr('stroke-width', 1.5)
    .selectAll('path')
    .data(root.links())
    .join('path')
    .attr('d', d3.linkHorizontal<HierarchyPointLink<any>, HierarchyPointNode<any>>()
      .x(d => d.y)
      .y(d => d.x) as any);

  // Render the nodes
  const node = g.append('g')
    .attr('stroke-linejoin', 'round')
    .attr('stroke-width', 3)
    .selectAll('g')
    .data(root.descendants())
    .join('g')
    .attr('transform', d => `translate(${d.y},${d.x})`)
    .style('cursor', 'pointer')
    .on('click', (event, d) => {
      onNodeClick(d.data); // Handle node click
    });

  node.append('circle')
    .attr('fill', d => d.children ? '#555' : '#999')
    .attr('r', 2.5);

  node.append('text')
    .attr('dy', '0.31em')
    .attr('x', d => d.children ? -6 : 6)
    .attr('text-anchor', d => d.children ? 'end' : 'start')
    .text(d => d.data.name)
    .attr('stroke', 'white')
    .attr('paint-order', 'stroke');

  // Append the SVG to the container
  if (svg.node() !== null) {
    container.appendChild(svg.node() as Node);
  }
}
