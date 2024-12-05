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

    this.breadcrumbPath = targetPath; // Update breadcrumbs
    this.renderChart(targetNode);
  }

  findNodeByPath(node: any, path: string[]): any {
    if (!path.length) return node;
    const [head, ...tail] = path;
    const child = node.children?.find((child: any) => child.name === head);
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
      selectedNode || this.originalData,
      container,
      handleNodeClick,
      handleBreadcrumbUpdate,
    );
  }
}
