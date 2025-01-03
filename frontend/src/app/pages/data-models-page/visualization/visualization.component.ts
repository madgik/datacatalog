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
  isFullScreen = false;

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
        this.renderChart(parentNode, targetNode); // Highlight the selected node
      } else {
      }
    }
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
    this.breadcrumbPath = this.breadcrumbPath.slice(0, index + 1);
    const targetNode = this.findNodeByPath(this.originalData, this.breadcrumbPath);
    this.renderChart(targetNode);
  }

  /** Recursively find a node based on breadcrumb path */
  findNodeByPath(node: any, path: string[]): any {
    return path.reduce(
      (current, part) => current?.children?.find((child: any) => child.name === part) || current,
      node
    );
  }

  /** Toggle full-screen mode */
  toggleFullScreen(): void {
    const chartContainer = this.elementRef.nativeElement.querySelector('#chart-container');
    if (!chartContainer) return;

    if (!document.fullscreenElement) {
      chartContainer.requestFullscreen().then(() => (this.isFullScreen = true));
    } else {
      document.exitFullscreen().then(() => (this.isFullScreen = false));
    }
  }

  /** Render the Tidy Tree chart */
  renderChart(node: any = this.originalData, highlightedNode: any = null): void {
    const container = this.elementRef.nativeElement.querySelector('#chart');
    if (!container) return;

    createTidyTree(
      this.breadcrumbPath,
      node,
      container,
      (path) => (this.breadcrumbPath = path),
      highlightedNode // Pass the highlighted node
    );
  }

}
