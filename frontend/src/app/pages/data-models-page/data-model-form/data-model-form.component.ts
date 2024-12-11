import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {CommonModule} from "@angular/common";
import {DataModelService} from "../../../services/data-model.service";

@Component({
  selector: 'app-data-model-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './data-model-form.component.html',
  styleUrls: ['./data-model-form.component.css'],
})
export class DataModelFormComponent implements OnInit {
  @Output() dataModelUpdated = new EventEmitter<void>();
  dataModelForm: FormGroup;
  isUpdateMode: boolean = false;

  selectedFileType: string = 'json';
  file: File | null = null;
  selectedDataModelID: string | undefined;
  errorMessage: string | null = null;


  constructor(
    private dataModelService: DataModelService,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.dataModelForm = this.fb.group({
      fileType: ["json"],
      file: [''],
      version: [''],        // New control for version
      longitudinal: [false] // New control for longitudinal (default to false)
    });
  }

  ngOnInit(): void {
    this.route.data.subscribe((data) => {
      this.isUpdateMode = data['isUpdate'];
    });

    if (this.isUpdateMode) {
      this.route.queryParams.subscribe((params) => {
        this.selectedDataModelID = params['dataModelId'];
      });
    }
  }

  onFileTypeChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.selectedFileType = target.value;
    this.file = null;
    this.errorMessage = null; // Reset error message
  }

  onFileChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      this.file = target.files[0];
    }
    this.errorMessage = null; // Reset error message
  }

  submitForm(): void {
    if (this.isUpdateMode && this.selectedDataModelID) {
      this.handleUpdateMode();
    } else {
      this.handleAddMode();
    }
  }

  handleAddMode(): void {
    if (!this.file) {
      this.errorMessage = 'No file selected';
      return;
    }

    this.errorMessage = null; // Reset error message
    if (this.selectedFileType === 'json') {
      this.dataModelService.createDataModelFromJson(this.file).subscribe({
        next: () => {
          console.log('JSON Data Model created successfully.');
          this.dataModelUpdated.emit(); // Notify parent
          this.router.navigate(['/data-models']); // Navigate to data models page
        },
        error: (error) => {
          console.error('Error creating JSON Data Model:', error);
          this.errorMessage = error; // Display the extracted error message
        },
      });
    } else if (this.selectedFileType === 'xlsx') {
      const version = this.dataModelForm.get('version')?.value;
      const longitudinal = this.dataModelForm.get('longitudinal')?.value;

      this.dataModelService.createDataModelFromExcel(this.file, version, longitudinal).subscribe({
        next: () => {
          console.log('Excel Data Model created successfully.');
          this.dataModelUpdated.emit(); // Notify parent
          this.router.navigate(['/data-models']); // Navigate to data models page
        },
        error: (error) => {
          console.error('Error creating Excel Data Model:', error);
          this.errorMessage = error; // Display the extracted error message
        },
      });
    }
  }

  handleUpdateMode(): void {
    if (!this.file || !this.selectedDataModelID) {
      this.errorMessage = 'No file or data model ID provided';
      return;
    }

    this.errorMessage = null; // Reset error message
    if (this.selectedFileType === 'json') {
      this.dataModelService.updateDataModelFromJson(this.selectedDataModelID, this.file).subscribe({
        next: () => {
          console.log('Data model updated successfully (JSON).');
          this.dataModelUpdated.emit(); // Notify parent
          this.router.navigate(['/data-models']); // Navigate to data models page
        },
        error: (error) => {
          console.error('Error updating JSON Data Model:', error);
          this.errorMessage = error; // Set the error message for display
        },
      });
    } else if (this.selectedFileType === 'xlsx') {
      const version = this.dataModelForm.get('version')?.value;
      const longitudinal = this.dataModelForm.get('longitudinal')?.value;

      this.dataModelService.updateDataModelFromExcel(this.selectedDataModelID, this.file, version, longitudinal).subscribe({
        next: () => {
          console.log('Data model updated successfully (Excel).');
          this.dataModelUpdated.emit(); // Notify parent
          this.router.navigate(['/data-models']); // Navigate to data models page
        },
        error: (error) => {
          console.error('Error updating Excel Data Model:', error);
          this.errorMessage = error; // Set the error message for display
        },
      });
    }
  }
}
