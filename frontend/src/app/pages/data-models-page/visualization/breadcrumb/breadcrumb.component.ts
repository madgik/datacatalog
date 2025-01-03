import { Component, Input, Output, EventEmitter } from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-breadcrumb',
  template: `
    <nav class="breadcrumbs">
      <ng-container *ngFor="let crumb of breadcrumbs; let i = index">
        <span
          class="breadcrumb"
          [class.active]="i === breadcrumbs.length - 1"
          (click)="onBreadcrumbClick(i)"
        >
          {{ crumb }}
        </span>
        <span *ngIf="i < breadcrumbs.length - 1"> &gt; </span>
      </ng-container>
    </nav>
  `,
  styleUrls: ['./breadcrumb.component.css'],
  imports: [
    NgForOf,
    NgIf
  ],
  standalone: true
})
export class BreadcrumbComponent {
  @Input() breadcrumbs: string[] = [];
  @Output() breadcrumbClick = new EventEmitter<number>();

  onBreadcrumbClick(index: number) {
    this.breadcrumbClick.emit(index);
  }
}
