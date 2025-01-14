import {
  Component,
  Input,
  OnChanges,
  SimpleChanges,
  ElementRef,
  OnInit,
} from '@angular/core';
import { createTidyTree } from './tidy-tree';
import { FormsModule } from '@angular/forms';
import { ErrorService } from '../services/error.service';
import { NgForOf, NgIf } from '@angular/common';
import {BreadcrumbComponent} from "./breadcrumb/breadcrumb.component";
import {SearchBarComponent} from "./search-bar/search-bar.component";

@Component({
  selector: 'app-visualization',
  templateUrl: './visualization.component.html',
  styleUrls: ['./visualization.component.css'],
  standalone: true,
  imports: [NgForOf, NgIf, FormsModule, BreadcrumbComponent, SearchBarComponent],
})
export class VisualizationComponent implements OnInit, OnChanges {
  @Input() dataModelHierarchy: any;

  breadcrumbPath: string[] = [];
  error: string | null = null;
  maxDepth: number = 1;
  newAvailableDepths: number = 5;
  isZoomEnabled = true; // Default state

  toggleZoom() {
    this.isZoomEnabled = !this.isZoomEnabled;
  }

  onZoomToggleChange() {
    // Re-render the tree when zoom state changes
    this.renderChart();
  }

  private originalData: any;

  constructor(
    private elementRef: ElementRef,
    private errorService: ErrorService
  ) {
    this.errorService.error$.subscribe((message) => {
      this.error = message;
    });
  }

  ngOnInit(): void {
    if (this.dataModelHierarchy) {
      this.originalData = this.dataModelHierarchy;
      this.initializeVisualization();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {

    if (changes['dataModelHierarchy']?.currentValue) {
      this.originalData = this.dataModelHierarchy;
      this.initializeVisualization();
    }
  }


  /** Initialize visualization and reset breadcrumb */
  initializeVisualization(): void {
    this.breadcrumbPath = [this.dataModelHierarchy?.name || 'Root'];
    this.renderChart();
  }
  createArray(size: number): number[] {
    return Array.from({ length: size }, (_, i) => i + 1);
  }

  onSearchResult(selectedItem: string): void {
    this.selectSearchResult(selectedItem); // Call your existing method
  }

  /** Select a node based on search result */
  selectSearchResult(selected: string): void {

    const targetNode = this.findNodeByName(this.originalData, selected);

    if (!targetNode) {
      console.warn('No node found for the given search query.');
      return;
    }

    if (targetNode.children && targetNode.children.length > 0) {
      // If node has children, make it the new root
      this.breadcrumbPath = this.getPathToNode(this.originalData, targetNode) || [];
      this.renderChart(targetNode, targetNode);
    } else {
      // If node has no children, make the parent the root and highlight the node
      const parentNode = this.findParentNode(this.originalData, targetNode);

      if (parentNode) {
        this.breadcrumbPath = this.getPathToNode(this.originalData, parentNode) || [];
        this.renderChart(parentNode, targetNode, 1); // Highlight the selected node
        this.maxDepth = 1
      } else {
      }
    }
  }

  /** Handle maxDepth change */
  onMaxDepthChange(): void {
    // Get the current node based on the breadcrumb path
    const currentNode = this.findNodeByPath(this.originalData, this.breadcrumbPath);

    // Re-render the chart while keeping the breadcrumb intact
    this.renderChart(currentNode, null, this.maxDepth);
  }


  /** Recursively find the path to a node */
  getPathToNode(node: any, target: any, path: string[] = []): string[] | null {
    path.push(node.name);
    if (node === target) return path;

    for (const child of node.children || []) {
      const foundPath = this.getPathToNode(child, target, [...path]);
      if (foundPath) return foundPath;
    }

    return null;
  }

  findParentNode(currentNode: any, targetNode: any, parent: any = null): any {
    if (currentNode === targetNode) return parent;
    for (const child of currentNode.children || []) {
      const foundParent = this.findParentNode(child, targetNode, currentNode);
      if (foundParent) return foundParent;
    }
    return null;
  }

  /** Recursively find a node by name */
  findNodeByName(node: any, name: string): any {
    if (node.name === name) return node;
    for (const child of node.children || []) {
      const found = this.findNodeByName(child, name);
      if (found) return found;
    }
    return null;
  }

  /** Handle breadcrumb navigation */
  handleBreadcrumbClick(index: number): void {
    // Slice the breadcrumb path to the clicked index
    this.breadcrumbPath = this.breadcrumbPath.slice(0, index + 1);

    // Find the target node based on the trimmed breadcrumb path
    const targetNode = this.findNodeByPath(this.originalData, this.breadcrumbPath);

    // Render the chart with the adjusted maxDepth
    if (targetNode) {
      this.renderChart(targetNode);
    }
  }

  /** Recursively find a node based on breadcrumb path */
  findNodeByPath(node: any, path: string[]): any {
    return path.reduce(
      (current, part) => current?.children?.find((child: any) => child.name === part) || current,
      node
    );
  }


  /** Render the Tidy Tree chart */
  renderChart(node: any = this.originalData, highlightedNode: any = null, maxDepth: number | null = null): void {
    const container = this.elementRef.nativeElement.querySelector('#chart');
    if (!container) return;
    createTidyTree(
      this.breadcrumbPath, // Use the breadcrumb path as-is
      node,
      container,
      (path) => {
        this.breadcrumbPath = path;
      },
      (newAvailableDepths) => {
        this.newAvailableDepths = newAvailableDepths; // Update the available depths
        this.maxDepth = newAvailableDepths; // Update the available depths
      },
      highlightedNode,
      maxDepth,
      this.isZoomEnabled
    );
  }
}
