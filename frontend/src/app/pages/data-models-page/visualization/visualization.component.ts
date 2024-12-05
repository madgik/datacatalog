import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnChanges,
  SimpleChanges,
  ElementRef,
  OnInit,
} from '@angular/core';
import { createTidyTree } from './tidy-tree';
import { FormsModule } from '@angular/forms';
import { ErrorService } from '../services/error.service';
import { NgForOf, NgIf } from '@angular/common';
@Component({
  selector: 'app-visualization',
  templateUrl: './visualization.component.html',
  styleUrls: ['./visualization.component.css'],
  standalone: true,
  imports: [FormsModule, NgForOf, NgIf],
})
export class VisualizationComponent implements OnInit, OnChanges {
  @Input() visualizationType = 'TidyTree';
  @Input() d3Data: any;
  @Output() selectedNodeChange = new EventEmitter<any>();

  breadcrumbPath: string[] = []; // Track breadcrumb path
  private originalData: any;
  error: string | null = null; // Holds the current error message

  constructor(
    private elementRef: ElementRef,
    private errorService: ErrorService
  ) {
    // Subscribe to the error service
    this.errorService.error$.subscribe((message) => {
      this.error = message; // Update the local error property
    });
  }

  ngOnInit(): void {
    if (this.d3Data) {
      this.originalData = this.d3Data;
      this.initializeVisualization();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['d3Data'] && this.d3Data) {
      this.originalData = this.d3Data;
      this.initializeVisualization();
    }
  }

  initializeVisualization(): void {
    this.breadcrumbPath = [this.d3Data.name]; // Initialize breadcrumbs
    this.renderChart();
  }

  handleBreadcrumbClick(index: number): void {
    const targetPath = this.breadcrumbPath.slice(0, index + 1);
    const targetNode = this.findNodeByPath(this.originalData, targetPath);
    if (!targetNode) {
      console.error(`No node found for breadcrumb path:`, targetPath);
      return; // Exit early if no valid node is found
    }

    this.breadcrumbPath = targetPath; // Update breadcrumbs
    this.renderChart(targetNode);
  }

  findNodeByPath(node: any, path: string[]): any {
  if (!node) {
    console.error("Node is undefined. Path segment not found:", path);
    return null; // Gracefully handle the error
  }

  if (!path.length) return node;

  const [head, ...tail] = path;

  // If the current node matches the root of the path, skip searching in children
  if (node.name === head) {
    console.log(`Matched root node: ${head}`);
    return this.findNodeByPath(node, tail);
  }

  const child = node.children?.find((child: any) => child.name === head);

  if (!child) {
    console.error(`Child node "${head}" not found under node:`, node);
    return null; // Return null if the child is not found
  }

  return this.findNodeByPath(child, tail);
}

  renderChart(selectedNode?: any): void {
    const container = this.elementRef.nativeElement.querySelector('#chart');
    if (!container) return;

    const handleNodeClick = (node: any) => {
      this.selectedNodeChange.emit(node);
    };

    const handleBreadcrumbUpdate = (path: string[]) => {
      this.breadcrumbPath = path; // Update breadcrumbs
    };

    createTidyTree(
      selectedNode ? this.breadcrumbPath : [],
      selectedNode || this.originalData,
      container,
      handleNodeClick,
      handleBreadcrumbUpdate,
    );
  }
}
