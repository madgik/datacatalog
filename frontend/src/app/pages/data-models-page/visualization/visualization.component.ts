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
import {BreadcrumbComponent} from "./breadcrumb.component";
import {NodeInfoComponent} from "./node-info.component";

@Component({
  selector: 'app-visualization',
  templateUrl: './visualization.component.html',
  styleUrls: ['./visualization.component.css'],
  standalone: true,
  imports: [NgForOf, NgIf, FormsModule, BreadcrumbComponent, NodeInfoComponent],
})
export class VisualizationComponent implements OnInit, OnChanges {
  @Input() dataModelHierarchy: any;

  breadcrumbPath: string[] = [];
  searchQuery: string = '';
  searchSuggestions: string[] = [];
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

  get hasVariableCount(): boolean {
    return this.dataModelHierarchy.hasOwnProperty('variableCount');
  }

  /** Initialize visualization and reset breadcrumb */
  initializeVisualization(): void {
    this.breadcrumbPath = [this.dataModelHierarchy?.name || 'Root'];
    this.renderChart();
  }

  /** Handles search input and suggests matching nodes */
  handleSearch(query: string): void {
    this.searchSuggestions = this.getAllNodeNames(this.originalData).filter((name) =>
      name.toLowerCase().includes(query.toLowerCase())
    );
  }

  /** Select a node based on search result */
  selectSearchResult(selected: string): void {
    const targetNode = this.findNodeByName(this.originalData, selected);
    if (targetNode) {
      this.breadcrumbPath = [targetNode.name];
      this.renderChart(targetNode);
    }
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

  /** Gather all node names for search suggestions */
  getAllNodeNames(node: any, names: string[] = []): string[] {
    names.push(node.name);
    for (const child of node.children || []) {
      this.getAllNodeNames(child, names);
    }
    return names;
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
  renderChart(node: any = this.originalData): void {
    const container = this.elementRef.nativeElement.querySelector('#chart');
    if (!container) return;

    createTidyTree(
      this.breadcrumbPath,
      node,
      container,
      (node) => {
        this.dataModelHierarchy = node;
      },
      (path) => (this.breadcrumbPath = path)
    );
  }
}
