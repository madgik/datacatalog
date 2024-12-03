import { Component, Input, Output, EventEmitter } from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-node-info',
  templateUrl: './node-info.component.html',
  styleUrls: ['./node-info.component.css'],
  standalone: true,
  imports: [
    NgIf,
    NgForOf
  ]
})
export class NodeInfoComponent {
  @Input() selectedNode: any | null = null;
  @Output() visibilityChange = new EventEmitter<boolean>();

  visible: boolean = true;

  get hasVariableCount(): boolean {
    return this.selectedNode.hasOwnProperty('variableCount');
  }

  toggleVisibility(): void {
    this.visible = !this.visible;
    this.visibilityChange.emit(this.visible); // Notify parent about the change
  }

  /**
   * Checks if a given field exists in the selectedNode.
   * @param field The field name to check.
   * @returns true if the field exists and is not undefined, false otherwise.
   */
  fieldExists(field: string): boolean {
    return this.selectedNode && field in this.selectedNode && this.selectedNode[field] !== undefined && this.selectedNode[field] != "";
  }
}
