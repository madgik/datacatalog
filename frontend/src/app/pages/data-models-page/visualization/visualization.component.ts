import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges, ElementRef, OnInit } from '@angular/core';
import { createSunburst } from './zoomable-sunburst';
import { createTidyTree } from './tidy-tree';
import { FormsModule } from '@angular/forms';
import { ErrorService } from '../services/error.service';
import { NgForOf } from '@angular/common';
import {createZoomableCirclePacking} from "./zoomable circle-packing";

@Component({
  selector: 'app-visualization',
  templateUrl: './visualization.component.html',
  styleUrls: ['./visualization.component.css'],
  standalone: true,
  imports: [FormsModule, NgForOf],
})
export class VisualizationComponent implements OnInit, OnChanges {
  @Input() visualizationType = 'TidyTree';
  @Input() d3Data: any;
  @Output() selectedNodeChange = new EventEmitter<any>();

  maxDepth: string = '2';
  error: string | null = null; // Holds the current error message
  groupList: string[] = []; // List of available groups
  selectedGroup: string | null = null; // Selected group

  constructor(private elementRef: ElementRef, private errorService: ErrorService) {
    // Subscribe to the error service
    this.errorService.error$.subscribe((message) => {
      this.error = message; // Update the local error property
    });
  }

  ngOnInit(): void {
    if (this.d3Data) {
      this.initializeVisualization();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['d3Data'] && this.d3Data) {
      this.errorService.clearError();
      this.initializeVisualization();
    }
  }

  initializeVisualization(): void {
    this.groupList = this.extractGroups(this.d3Data); // Populate group list
    this.selectedGroup = this.groupList[0]; // Set root group as default
    this.updateMaxDepthOptions(this.d3Data); // Set max depth based on root group
    this.renderChart();
  }

  onVisualizationTypeChange(event: any): void {
    this.visualizationType = event.target.value;
    this.renderChart();
  }

  onMaxDepthChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.maxDepth = target.value;
    this.renderChart();
  }

  onGroupChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.selectedGroup = target.value;

    // Find the selected group and calculate its max depth
    const selectedGroupData = this.findGroup(this.d3Data, this.selectedGroup);
    if (selectedGroupData) {
      this.updateMaxDepthOptions(selectedGroupData);
    }
    this.maxDepth = "2";
    this.renderChart();
  }

  renderChart(): void {
    const container = this.elementRef.nativeElement.querySelector('#chart');
    if (!container) {
      this.error = 'Chart container is not available.';
      return;
    }
    container.innerHTML = ''; // Clear previous chart

    if (!this.d3Data) {
      this.error = 'No data available for visualization.';
      return;
    }

    let visualizationData = this.d3Data;

    // Start from the selected group if specified
    if (this.selectedGroup) {
      visualizationData = this.findGroup(this.d3Data, this.selectedGroup);
      if (!visualizationData) {
        this.error = 'Selected group not found in the data.';
        return;
      }
    }


    // Limit tree depth if applicable
    if (this.maxDepth !== 'max') {
      const maxDepthValue = parseInt(this.maxDepth, 10);
      visualizationData = this.limitTreeDepth(visualizationData, maxDepthValue);
    }
    console.log(visualizationData)
    const handleNodeClick = (node: any) => {
      this.selectedNodeChange.emit(node);
    };

    try {
      switch (this.visualizationType) {
        case 'ZoomableCirclePacking':
          createZoomableCirclePacking(visualizationData, container, handleNodeClick);
          break;
        case 'ZoomableSunburst':
          createSunburst(visualizationData, container, handleNodeClick);
          break;
        case 'TidyTree':
          createTidyTree(visualizationData, container, handleNodeClick);
          break;
        default:
          this.error = 'Unknown visualization type.';
      }
    } catch (e) {
      this.error =
        e instanceof Error
          ? `An error occurred while rendering the chart: ${e.message}`
          : 'An unknown error occurred while rendering the chart.';
    }
  }

  extractGroups(data: any, currentPath: string = ''): string[] {
  const groups: string[] = [];

  const traverse = (node: any, path: string) => {
    const fullPath = path ? `${path}/${node.name}` : node.name;

    // Only include the path if the node has children
    if (node.children && node.children.length > 0) {
      groups.push(fullPath);
      node.children.forEach((child: any) => traverse(child, fullPath));
    }
  };

  // Traverse the tree starting from the root
  traverse(data, currentPath);

  // Add the root group explicitly only if it is not already in the list
  if (!groups.includes(data.name)) {
    groups.unshift(data.name);
  }

  return groups;
}


  findGroup(data: any, groupPath: string): any {
    const pathParts = groupPath.split('/');

    const findByPath = (node: any, parts: string[]): any => {
      if (!node || parts.length === 0) {
        return node; // Return the node if we've traversed the full path
      }

      const [current, ...remaining] = parts;

      // If the current part matches, continue traversing
      if (node.name === current) {
        if (remaining.length === 0) {
          return node; // We've found the target node
        }

        // Traverse children
        const child = node.children?.find((child: any) => child.name === remaining[0]);
        return findByPath(child, remaining);
      }

      return null; // Path doesn't match
    };

    return findByPath(data, pathParts);
  }

  limitTreeDepth(data: any, maxDepth: number): any {
    const prune = (node: any, depth: number): any => {
      if (depth > maxDepth) {
        return undefined;
      }
      if (!node.children || node.children.length === 0) {
        return node;
      }
      return {
        ...node,
        children: node.children.map((child: any) => prune(child, depth + 1)).filter(Boolean),
      };
    };
    return prune(data, 1);
  }

  updateMaxDepthOptions(groupData: any): void {
    const calculateDepth = (node: any): number => {
      if (!node.children || node.children.length === 0) {
        return 1; // Leaf node
      }
      return 1 + Math.max(...node.children.map((child: any) => calculateDepth(child)));
    };

    const maxDepth = calculateDepth(groupData);

    // Update maxDepth dropdown options dynamically
    const depthOptions: string[] = Array.from({ length: maxDepth - 1 }, (_, i) => (i + 2).toString());
    depthOptions.push('max'); // Include the "max" option

    const maxDepthSelect = this.elementRef.nativeElement.querySelector('#maxDepth') as HTMLSelectElement;
    if (maxDepthSelect) {
      maxDepthSelect.innerHTML = ''; // Clear existing options
      depthOptions.forEach((option) => {
        const opt = document.createElement('option');
        opt.value = option;
        opt.textContent = option === 'max' ? 'Max (Whole Tree)' : option;
        maxDepthSelect.appendChild(opt);
      });
    }

    if (this.maxDepth !== 'max' && parseInt(this.maxDepth, 10) > maxDepth) {
      this.maxDepth = 'max'; // Reset to max if current maxDepth exceeds the calculated depth
    }
  }
}
