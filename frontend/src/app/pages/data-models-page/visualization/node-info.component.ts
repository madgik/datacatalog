import { Component, Input } from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-node-info',
  template: `
    <div class="node-info" *ngIf="data">
      <h3 class="node-info-title">{{ hasVariableCount ? 'Group Information' : 'Variable Information' }}</h3>
      <div class="node-info-content">
        <p><strong>Code:</strong> {{ data.code || 'N/A' }}</p>
        <p><strong>Name:</strong> {{ data.name || 'N/A' }}</p>
        <ng-container *ngIf="hasVariableCount; else variableDetails">
          <p><strong>Number of Variables:</strong> {{ data.variableCount }}</p>
        </ng-container>
        <ng-template #variableDetails>
          <p *ngIf="fieldExists('description')"><strong>Description:</strong> {{ data.description }}</p>
          <p *ngIf="fieldExists('type')"><strong>Type:</strong> {{ data.type }}</p>
          <div *ngIf="fieldExists('enumerations') && data.enumerations?.length > 0">
            <p><strong>Enumerations:</strong></p>
            <ul class="enumerations-list">
              <li *ngFor="let enumItem of data.enumerations">{{ enumItem.label }}</li>
            </ul>
          </div>
        </ng-template>
      </div>
    </div>
  `,
  styleUrls: ['./node-info.component.css'],
  imports: [
    NgIf,
    NgForOf
  ],
  standalone: true
})
export class NodeInfoComponent {
  @Input() data: any;
  @Input() hasVariableCount: boolean = false;

  /** Utility: Check if a field exists in the data */
  fieldExists(field: string): boolean {
    return this.data && field in this.data && this.data[field] !== undefined && this.data[field] !== "";
  }
}
