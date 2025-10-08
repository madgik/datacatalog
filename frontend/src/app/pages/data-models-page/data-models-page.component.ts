import { Component, OnInit, signal} from '@angular/core';
import { FormsModule } from "@angular/forms";
import { CommonModule } from "@angular/common";
import { Federation } from "../../interfaces/federations.interface";
import { FederationService } from "../../services/federation.service";
import { DataModelService } from "../../services/data-model.service";
import {ActivatedRoute, Router, RouterOutlet} from '@angular/router';
import { AuthService } from "../../services/auth.service";
import { MatMenu, MatMenuItem, MatMenuTrigger } from "@angular/material/menu";
import { MatIcon } from "@angular/material/icon";
import { MatIconButton } from "@angular/material/button";
import { DataModel } from "../../interfaces/data-model.interface";
import { FederationSelectorComponent } from "./federation-selector/federation-selector.component";
import { VisualizationComponent } from "./visualization/visualization.component";
import { ActionMenuComponent } from "./action-menu/action-menu.component";
import { DataModelSelectorComponent } from "./data-model-selector/data-model-selector.component";
import { ExportOptionsComponent } from "./export-options/export-options.component";
import {ErrorService} from "./services/error.service";
import {ConfirmationDialogComponent} from "./confirmation-dialog/confirmation-dialog.component";
import {MatDialog} from "@angular/material/dialog";
import {DataModelFormComponent} from "./data-model-form/data-model-form.component";
import {GuidePopupComponent} from "./guide-popup/guide-popup.component";


@Component({
  selector: 'app-data-models-page',
  templateUrl: './data-models-page.component.html',
  styleUrls: ['./data-models-page.component.css'],
  imports: [
    CommonModule,
    FormsModule,
    MatMenuTrigger,
    MatIcon,
    MatMenu,
    MatIconButton,
    MatMenuItem,
    FederationSelectorComponent,
    VisualizationComponent,
    ActionMenuComponent,
    DataModelSelectorComponent,
    ExportOptionsComponent,
    RouterOutlet,
    GuidePopupComponent,
  ],
  standalone: true
})
export class DataModelsPageComponent implements OnInit{
  d3Data: any;
  federations: Federation[] = [];
  selectedFederation: Federation | null = null;
  selectedDataModel: DataModel | null | undefined;
  queryDataModelCode: string | null = null;
  queryDataModelSlug: string | null = null;
  queryLatestFlag = false;
  isDomainExpert = false;
  selectedFileType = signal<'json' | 'xlsx'>('json');
  crossSectionalModels: DataModel[] = [];
  longitudinalModels: DataModel[] = [];
  menuVisible = signal(false);

  constructor(
    private federationService: FederationService,
    private dataModelService: DataModelService,
    private authService: AuthService,
    private errorService: ErrorService,
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog
  ) {}



  ngOnInit(): void {
    // Check for the user's role first
    this.authService.hasRole('DC_DOMAIN_EXPERT').subscribe((hasRole) => {
      this.isDomainExpert = hasRole;
    });

    // Load federations and query params together
    this.federationService.getFederationsWithModels().subscribe({
      next: (federations: Federation[]) => {
        this.federations = federations;

        // Now process the query parameters
        this.route.queryParams.subscribe((params) => {
          const federationCode = params['federationCode'];
          const dataModelCode = params['dataModelCode'];
          const latestFlag = params['latest'];

          // Set selectedFederation based on federationCode
          this.selectedFederation = federationCode
            ? this.federations.find((fed) => fed.code === federationCode) || null
            : null;

          if (typeof dataModelCode === 'string') {
            this.queryDataModelCode = this.normalizeIdentifier(dataModelCode);
            this.queryDataModelSlug = this.slugifyIdentifier(this.queryDataModelCode);
          } else {
            this.queryDataModelCode = null;
            this.queryDataModelSlug = null;
          }
          this.queryLatestFlag = this.parseLatestFlag(latestFlag);

          console.log('[DataModels] Applied query params', {
            federationCode,
            dataModelCode,
            normalizedCode: this.queryDataModelCode,
            slug: this.queryDataModelSlug,
            latest: this.queryLatestFlag,
          });

          this.loadDataModels();
        });
      },
      error: (error) => {
        console.error('Error loading federations:', error);
        this.errorService.setError('Failed to load federations.');
      },
    });
  }

  loadDataModels(): void {

    if (this.selectedFederation) {

      this.dataModelService.getDataModelsByIds(this.selectedFederation.dataModelIds).subscribe((dataModels) => {

        this.handleDataModelResponse(dataModels);
      });

    } else {
      if (this.isDomainExpert){
        this.dataModelService.getAllDataModels().subscribe((dataModels) => {
          this.handleDataModelResponse(dataModels);
        });
      }
      else {
        this.dataModelService.getAllReleasedDataModels().subscribe((dataModels) => {
          this.handleDataModelResponse(dataModels);
        });
      }
    }
  }

  handleDataModelResponse(dataModels: DataModel[]): void {
    const { crossSectional, longitudinal } = this.dataModelService.categorizeDataModels(dataModels);
    this.crossSectionalModels = crossSectional;
    this.longitudinalModels = longitudinal;
    this.selectedDataModel = this.pickDataModelSelection(crossSectional, longitudinal);
    this.loadVisualizationData();
  }

  loadVisualizationData(): void {
    if (this.selectedDataModel) {
      this.d3Data = this.dataModelService.convertToD3Hierarchy(this.selectedDataModel);
    }
  }

  onSelectedDataModelChange(selectedDataModel: DataModel | null): void {
    this.selectedDataModel = selectedDataModel;
    this.loadVisualizationData();
  }

  onSelectedFederationChange(selectedFederation: Federation | null): void {
    this.selectedFederation = selectedFederation;
    this.loadDataModels();
  }

  private pickDataModelSelection(crossSectional: DataModel[], longitudinal: DataModel[]): DataModel | null {
    const combined = [...crossSectional, ...longitudinal];

    if (!this.queryDataModelCode) {
      console.log('[DataModels] No dataModelCode query provided; falling back to first available model.');
      return crossSectional[0] || longitudinal[0] || null;
    }

    const matchingLogs = combined.map((model) => {
      const normalizedCode = this.normalizeIdentifier(model.code);
      const normalizedLabel = this.normalizeIdentifier(model.label);
      const candidates = [
        normalizedCode,
        normalizedLabel,
        this.slugifyIdentifier(normalizedCode),
        this.slugifyIdentifier(normalizedLabel),
      ].filter((candidate): candidate is string => candidate !== null);

      const exactMatch = candidates.some((candidate) =>
        candidate === this.queryDataModelCode
        || (this.queryDataModelSlug !== null && candidate === this.queryDataModelSlug)
      );
      const partialMatch = candidates.some((candidate) =>
        (this.queryDataModelCode !== null && candidate.includes(this.queryDataModelCode))
        || (this.queryDataModelSlug !== null && candidate.includes(this.queryDataModelSlug))
      );

      return {
        code: model.code,
        label: model.label,
        version: model.version,
        candidates,
        exactMatch,
        partialMatch,
        matches: exactMatch || partialMatch,
      };
    });

    const matchingModels = combined.filter((_, index) => matchingLogs[index].matches);

    console.log('[DataModels] Evaluated data model matches', {
      query: {
        code: this.queryDataModelCode,
        slug: this.queryDataModelSlug,
        latest: this.queryLatestFlag,
      },
      results: matchingLogs,
    });

    if (matchingModels.length === 0) {
      console.log('[DataModels] No matching data models found; falling back to default ordering.');
      return crossSectional[0] || longitudinal[0] || null;
    }

    if (this.queryLatestFlag) {
      const selectedLatest = matchingModels.reduce((latest, current) =>
        this.compareSemanticVersions(current.version, latest.version) > 0 ? current : latest
      , matchingModels[0]);
      console.log('[DataModels] Selected latest matching model', {
        code: selectedLatest.code,
        label: selectedLatest.label,
        version: selectedLatest.version,
      });
      return selectedLatest;
    }

    const selectedModel = matchingModels[0];
    console.log('[DataModels] Selected matching model', {
      code: selectedModel.code,
      label: selectedModel.label,
      version: selectedModel.version,
    });
    return selectedModel;
  }

  private parseLatestFlag(value: unknown): boolean {
    if (typeof value === 'string') {
      return value.toLowerCase() === 'true';
    }
    if (typeof value === 'boolean') {
      return value;
    }
    return false;
  }

  private compareSemanticVersions(a: string | undefined, b: string | undefined): number {
    const aTokens = this.tokenizeVersion(a);
    const bTokens = this.tokenizeVersion(b);
    const maxLength = Math.max(aTokens.length, bTokens.length);

    for (let i = 0; i < maxLength; i += 1) {
      const aToken = aTokens[i];
      const bToken = bTokens[i];

      if (aToken === undefined && bToken === undefined) {
        return 0;
      }
      if (aToken === undefined) {
        return -1;
      }
      if (bToken === undefined) {
        return 1;
      }

      const aIsNumeric = /^\d+$/.test(aToken);
      const bIsNumeric = /^\d+$/.test(bToken);

      if (aIsNumeric && bIsNumeric) {
        const aVal = parseInt(aToken, 10);
        const bVal = parseInt(bToken, 10);
        if (aVal !== bVal) {
          return aVal > bVal ? 1 : -1;
        }
        continue;
      }

      if (aIsNumeric) {
        return 1;
      }
      if (bIsNumeric) {
        return -1;
      }

      if (aToken !== bToken) {
        return aToken > bToken ? 1 : -1;
      }
    }

    return 0;
  }

  private tokenizeVersion(value: string | undefined): string[] {
    if (!value) {
      return [];
    }

    const normalized = value.trim().toLowerCase();
    if (!normalized) {
      return [];
    }

    const rawTokens = normalized.match(/[a-z]+|\d+/g) || [];
    if (rawTokens.length > 1 && rawTokens[0] === 'v') {
      rawTokens.shift();
    }
    return rawTokens;
  }

  private normalizeIdentifier(value: unknown): string | null {
    if (typeof value !== 'string') {
      return null;
    }
    const normalized = value.trim().toLowerCase();
    return normalized.length > 0 ? normalized : null;
  }

  private slugifyIdentifier(value: string | null): string | null {
    if (!value) {
      return null;
    }
    const slug = value.replace(/[^a-z0-9]/g, '');
    return slug.length > 0 ? slug : null;
  }


  handleAction(action: string): void {
    switch (action) {
      case 'add':
        this.goToAddDataModel();
        break;
      case 'update':
        this.goToUpdateDataModel();
        break;
      case 'delete':
        this.deleteDataModel();
        break;
      case 'release':
        this.releaseDataModel();
        break;
      default:
        console.error('Unknown action:', action);
    }
  }

  goToAddDataModel(): void {
    const dialogRef = this.dialog.open(DataModelFormComponent, {
      data: { isUpdateMode: false }, // Pass props for add mode
    });

    dialogRef.componentInstance.dataModelUpdated.subscribe(() => {
      this.onDataModelUpdated(); // Refresh data models after adding
      dialogRef.close(); // Close the dialog after the operation
    });
  }

  goToUpdateDataModel(): void {
    if (this.selectedDataModel) {
      const dialogRef = this.dialog.open(DataModelFormComponent, {
        data: {
          isUpdateMode: true,
          dataModelId: this.selectedDataModel.uuid, // Pass the current data model's ID for update mode
        },
      });

      dialogRef.componentInstance.dataModelUpdated.subscribe(() => {
        this.onDataModelUpdated(); // Refresh data models after updating
        dialogRef.close(); // Close the dialog after the operation
      });
    }
  }

  onDataModelUpdated(): void {
    this.loadDataModels();
  }


  // Check if the current route is a child route
  isChildRouteActive(): boolean {
    const currentPath = this.router.url;
    return currentPath.includes('/data-models/add') || currentPath.includes('/data-models/update');
  }

  deleteDataModel(): void {
    if (!this.selectedDataModel) { // Ensure selectedDataModel is defined
      console.error('No data model selected to delete.');
      return;
    }

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Delete DataModel',
        message: 'Are you sure you want to delete this data model? This action cannot be undone.'
      }
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (confirmed) {
        const uuid = this.selectedDataModel?.uuid; // Safe optional chaining for uuid
        if (uuid) { // Ensure uuid exists
          this.dataModelService.deleteDataModel(uuid).subscribe({
            next: () => {
              this.dataModelService.getAllDataModels().subscribe((dataModels) => {
                this.handleDataModelResponse(dataModels);
              }); // Reload models after successful deletion
            },
            error: (error) => console.error('Error deleting data model:', error),
          });
        } else {
          console.error('Selected data model does not have a valid UUID.');
        }
      }
    });
  }

  releaseDataModel(): void {
    if (!this.selectedDataModel) { // Ensure selectedDataModel is defined
      console.error('No data model selected to release.');
      return;
    }

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Release DataModel',
        message: 'Are you sure you want to release this data model? Once released, you will no longer be able to delete, update, or revert this data model.'
      }
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (confirmed) {
        const uuid = this.selectedDataModel?.uuid; // Safe optional chaining for uuid
        if (uuid) { // Ensure uuid exists
          this.dataModelService.releaseDataModel(uuid).subscribe({
            next: () => {
              this.dataModelService.getAllDataModels().subscribe((dataModels) => {
                this.handleDataModelResponse(dataModels);
              }); // Reload models after successful release
            },
            error: (error) => console.error('Error releasing data model:', error),
          });
        } else {
          console.error('Selected data model does not have a valid UUID.');
        }
      }
    });
  }


  exportDataModel(fileType: 'json' | 'xlsx'): void {
    if (this.selectedDataModel) {
      this.dataModelService.exportDataModel(this.selectedDataModel, fileType);
    }
  }

  handleMenuToggle(visible: boolean): void {
    this.menuVisible.set(visible);
  }
}
