import {Component, Input, Output, EventEmitter, HostListener} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-export-options',
  templateUrl: './export-options.component.html',
  styleUrls: ['./export-options.component.css'],
  standalone: true,
  imports: [
    FormsModule,
    NgIf
  ]
})
export class ExportOptionsComponent {
  @Input() selectedFileType: 'json' | 'xlsx' = 'json';
  @Output() export = new EventEmitter<'json' | 'xlsx'>();
  isDropdownVisible = false;

  toggleDropdown(event: Event): void {
    event.stopPropagation(); // Prevent the click event from propagating
    this.isDropdownVisible = !this.isDropdownVisible;
  }

  @HostListener('document:click', ['$event'])
  closeDropdown(event: Event): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.export-container')) {
      this.isDropdownVisible = false;
    }
  }

  onExport(): void {
    this.export.emit(this.selectedFileType);
    this.isDropdownVisible = false;
  }
}
