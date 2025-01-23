import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Federation } from '../../../interfaces/federations.interface';
import {DecimalPipe, SlicePipe} from "@angular/common";

@Component({
  selector: 'app-federation-card',
  templateUrl: './federation-card.component.html',
  styleUrls: ['./federation-card.component.css'],
  imports: [
    SlicePipe,
    DecimalPipe
  ],
  standalone: true
})
export class FederationCardComponent {
  @Input() federation!: Federation;
  @Input() isAdmin = false;
  @Output() updateFederation = new EventEmitter<string>();
  @Output() deleteFederation = new EventEmitter<string>();
  @Output() visualizeDataModel = new EventEmitter<string>();
  showMore: boolean = false;

  viewDataModel() {
    this.visualizeDataModel.emit(this.federation.code);
  }

  navigateToFederation(url: string): void {
      window.open(url, '_blank');
  }

  update() {
    this.updateFederation.emit(this.federation.code);
  }

  delete() {
    this.deleteFederation.emit(this.federation.code);
  }

  toggleDescription(): void {
    this.showMore = !this.showMore;
  }
}
