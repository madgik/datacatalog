import {
  Component,
  EventEmitter,
  Input,
  Output,
  OnInit,
  ElementRef,
  HostListener,
  SimpleChanges,
  OnChanges
} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  standalone: true,
  imports: [
    FormsModule,
    NgIf,
    NgForOf
  ],
  styleUrls: ['./search-bar.component.css']
})
export class SearchBarComponent implements OnInit, OnChanges  {
  @Input() dataModelHierarchy: any;
  @Output() searchResultSelected = new EventEmitter<string>();

  searchQuery: string = '';
  variables: { name: string; type: string; path: string }[] = [];
  groups: { name: string; path: string }[] = [];
  filteredItems: any[] = [];
  searchSuggestionsVisible = false;
  isSearchExpanded = false;
  filterType: string = 'variables'; // Default filter type
  variableTypeFilter: string = ''; // Additional variable type filter
  variableTypes: string[] = []; // List of available variable types

  constructor(private eRef: ElementRef) {}

  ngOnInit(): void {
    this.extractVariablesAndGroups(this.dataModelHierarchy);
  }

  // Detect changes to dataModelHierarchy and reprocess data
    ngOnChanges(changes: SimpleChanges): void {
      if (changes['dataModelHierarchy'] && changes['dataModelHierarchy'].currentValue) {
        this.variables = [];
        this.groups = [];
        this.variableTypes = [];
        this.extractVariablesAndGroups(this.dataModelHierarchy);
      }
    }
  expandSearch(event: MouseEvent): void {
    event.stopPropagation(); // Prevent triggering document click listener
    this.isSearchExpanded = true;
  }

  closeSearch(): void {
    this.isSearchExpanded = false;
    this.searchQuery = '';
    this.searchSuggestionsVisible = false;
  }

  @HostListener('document:click', ['$event'])
  onOutsideClick(event: Event): void {
    if (!this.eRef.nativeElement.contains(event.target)) {
      this.closeSearch();
    }
  }

  // Extract variables, groups, and variable types
  extractVariablesAndGroups(hierarchy: any): void {
    const traverse = (node: any, path: string) => {
      if (!node) return;

      const currentPath = path ? `${path} > ${node.name}` : node.name;

      if (node.hasOwnProperty('variableCount')) {
        this.groups.push({ name: node.name, path: currentPath });
        node.children.forEach((child: any) => traverse(child, currentPath));
      } else {
        this.variables.push({ name: node.name, type: node.type, path: currentPath });
        if (!this.variableTypes.includes(node.type)) {
          this.variableTypes.push(node.type);
        }
      }
    };

    traverse(hierarchy, '');
  }

  handleSearch(query: string): void {
    this.searchQuery = query.toLowerCase();
    this.applyFilter(this.filterType);
    this.searchSuggestionsVisible = this.filteredItems.length > 0;
  }

  applyFilter(type: string): void {
    if (type === 'variables') {
      this.filteredItems = this.variables.filter(
        (v) =>
          v.name.toLowerCase().includes(this.searchQuery) &&
          (this.variableTypeFilter ? v.type === this.variableTypeFilter : true)
      );
    } else if (type === 'groups') {
      this.filteredItems = this.groups.filter((g) =>
        g.name.toLowerCase().includes(this.searchQuery)
      );
    }
  }

  applyVariableTypeFilter(type: string): void {
    this.variableTypeFilter = type;
    this.applyFilter(this.filterType);
  }

  onItemClick(item: any): void {
    this.searchQuery = item.name || item;
    this.searchSuggestionsVisible = false;
    this.searchResultSelected.emit(this.searchQuery);
  }

  generateTooltip(item: any): string {
    if ('type' in item) {
      return `Path: ${item.path}\nType: ${item.type}`;
    }
    return `Path: ${item.path}`;
  }

  onSearchFocus(): void {
    this.searchSuggestionsVisible = true;
    this.handleSearch(this.searchQuery);
  }
}
