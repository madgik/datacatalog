import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, map, switchMap, tap } from 'rxjs/operators';
import {DataModel} from "../interfaces/data-model.interface";

@Injectable({
  providedIn: 'root',
})
export class DataModelService {
  private apiUrl = `/services/datamodels`;
  private dataModels: any[] = []; // Cache for all data models
  private dataModelsLoaded = false; // Flag to track cache loading

  constructor(private http: HttpClient) {}

  // Fetch and cache all data models
  loadAllDataModels(): Observable<any[]> {
    if (!this.dataModelsLoaded) {
      return this.http.get<any[]>(this.apiUrl).pipe(
        tap((dataModels) => {
          this.dataModels = dataModels;
          this.dataModelsLoaded = true;
        }),
        catchError((error) => {
          console.error('Error fetching data models:', error);
          return of([]);
        })
      );
    }
    return of(this.dataModels);
  }

  // Retrieve all data models, using the cache if available
  getAllReleasedDataModels(): Observable<any[]> {

    // Ensure data models are loaded before returning
    return this.loadAllDataModels().pipe(
      map(() => this.dataModels.filter(dataModel => dataModel.released === true))
    );
  }

  exportDataModel(data_model: DataModel, fileType: 'json' | 'xlsx'): void {
    const url = fileType === 'json'
        ? `${this.apiUrl}/${data_model.uuid}`
        : `${this.apiUrl}/${data_model.uuid}/export`;

    if (fileType === 'json') {
      // JSON case: specify responseType as 'json' and handle the JSON data
      this.http.get<any>(url, { responseType: 'json' }).subscribe(
        (response) => {
          // Beautify the JSON by adding indentation with 2 spaces
          const beautifiedJson = JSON.stringify(response, null, 2);
          const blob = new Blob([beautifiedJson], { type: 'application/json' });
          const link = document.createElement('a');
          link.href = window.URL.createObjectURL(blob);
          link.download = `${data_model.code}_${data_model.version}.json`;
          link.click();
        },
        (error) => {
          console.error('Error exporting JSON data model:', error);
        }
      );
    } else {
      // XLSX case: specify responseType as 'blob' and handle the binary data
      this.http.get(url, { responseType: 'blob' }).subscribe(
        (response) => {
          const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
          const link = document.createElement('a');
          link.href = window.URL.createObjectURL(blob);
          link.download = `${data_model.code}_${data_model.version}.xlsx`;
          link.click();
        },
        (error) => {
          console.error('Error exporting XLSX data model:', error);
        }
      );
    }
  }

  reloadDataModels(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl).pipe(
      tap((dataModels) => {
        this.dataModels = dataModels;
        this.dataModelsLoaded = true;
      }),
      catchError((error) => {
        console.error('Error reloading data models:', error);
        return of([]);
      })
    );
  }

  // Get all data models from cache or API
  getAllDataModels(): Observable<any[]> {
    return this.loadAllDataModels();
  }



  // Get data models by federation IDs
  getDataModelsByIds(ids: string[]): Observable<any[]> {
    return this.getAllDataModels().pipe(
      map((dataModels) => dataModels.filter((model) => ids.includes(model.uuid))),
      catchError((error) => {
        console.error('Error fetching data models by IDs:', error);
        return of([]);
      })
    );
  }

  // Categorize data models into cross-sectional and longitudinal
  categorizeDataModels(dataModels: DataModel[]): {
    crossSectional: DataModel[];
    longitudinal: DataModel[];
  } {
    const crossSectional = dataModels.filter((model) => !model.longitudinal);
    const longitudinal = dataModels.filter((model) => model.longitudinal);

    return { crossSectional, longitudinal };
  }

  // Convert data model to D3 hierarchy format with variable count for groups
convertToD3Hierarchy(data: any): any {
  const convertVariables = (variables: any[]): any[] =>
    variables.map((v) => ({
      name: v.label,
      value: 1,
      ...v,
    }));

  const convertGroups = (groups: any[]): any[] =>
    groups.map((g: any) => {
      const variableNodes = convertVariables(g.variables || []);
      const groupNodes = convertGroups(g.groups || []);
      const totalVariableCount = variableNodes.length + groupNodes.reduce((count, group) => count + (group.variableCount || 0), 0);

      return {
        name: g.label,
        code: g.code,
        variableCount: totalVariableCount, // Track total variables in the group and subgroups
        children: [...variableNodes, ...groupNodes],
      };
    });

  const rootVariables = convertVariables(data.variables || []);
  const rootGroups = convertGroups(data.groups || []);
  const rootVariableCount = rootVariables.length + rootGroups.reduce((count, group) => count + (group.variableCount || 0), 0);

  return {
    name: data.label,
    code: data.code,
    variableCount: rootVariableCount, // Track total variables for the root
    children: [...rootVariables, ...rootGroups],
  };
}

  //CRUD:

  deleteDataModel(dataModelId: string): Observable<any[]> {
    return this.http.delete<void>(`${this.apiUrl}/${dataModelId}`).pipe(
      switchMap(() => this.reloadDataModels()), // Reload data models after deletion
      catchError((error) => {
        console.error('Error deleting data model:', error);
        return throwError(() => error);
      })
    );
  }

  releaseDataModel(dataModelId: string): Observable<any[]> {
    return this.http.post<void>(`${this.apiUrl}/${dataModelId}/release`, {}).pipe(
      switchMap(() => this.reloadDataModels()), // Reload data models after release
      catchError((error) => {
        console.error('Error releasing data model:', error);
        return throwError(() => error);
      })
    );
  }


  createDataModelFromExcel(file: File, version: string, longitudinal: string): Observable<any[]> {
    const url = `${this.apiUrl}/import`;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('version', version);
    formData.append('longitudinal', longitudinal);

    return this.http.post<void>(url, formData).pipe(
      switchMap(() => this.reloadDataModels()), // Reload data models after creation
      tap(() => console.log('Data model created successfully from Excel.')),
      catchError((error: HttpErrorResponse) => {
        console.error('Sanitized error response:', error.error.replace(/<EOL>/g, '\n'));
        const errorMessage = this.extractErrorMessage(error, 'creating Excel data model');
        return throwError(() => errorMessage);
        }
      )
    )
  }

  private extractErrorMessage(error: HttpErrorResponse, action: string): string {
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      return `An error occurred while ${action}: ${error.error.message}`;
    } else if (typeof error.error === 'string') {
      try {
        // Replace <EOL> with actual newlines
        const sanitizedError = error.error.replace(/<EOL>/g, '\n').trim();

        // Extract JSON from the string if it exists
        const jsonStartIndex = sanitizedError.indexOf('{');
        const jsonEndIndex = sanitizedError.lastIndexOf('}');
        if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
          const jsonString = sanitizedError.substring(jsonStartIndex, jsonEndIndex + 1);
          const parsedError = JSON.parse(jsonString);
          if (parsedError.error) {
            return `Error while ${action}: ${parsedError.error}`;
          }
        }

        // If JSON parsing fails, return sanitized string
        return `An unexpected error occurred while ${action}: ${sanitizedError}`;
      } catch (e) {
        // If an error occurs during parsing, return the raw error
        return `An unexpected error occurred while ${action}: ${error.error}`;
      }
    } else if (error.error && error.error.error) {
      // Error object already parsed
      return `Error while ${action}: ${error.error.error}`;
    }

    // Default fallback
    return `An unexpected error occurred while ${action}: ${error.message}`;
  }

  createDataModelFromJson(file: File): Observable<void> {
    const url = `${this.apiUrl}`;
    return new Observable<void>((observer) => {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const dataModelDTO = JSON.parse(reader.result as string);
          this.http.post<void>(url, dataModelDTO).subscribe({
            next: () => {
              console.log('Data model created successfully from JSON.');
              this.reloadDataModels().subscribe(() => {
                console.log('Data models reloaded after JSON creation.');
                observer.next();
                observer.complete();
              });
            },
            error: (error: HttpErrorResponse) => {
              observer.error(this.extractErrorMessage(error, 'creating JSON data model'));
            },
          });
        } catch (error) {
          observer.error('Error parsing JSON file: ' + error);
        }
      };
      reader.readAsText(file);
    });
  }


  updateDataModelFromJson(dataModelId: string, file: File): Observable<void> {
    const url = `${this.apiUrl}/${dataModelId}`;
    return new Observable<void>((observer) => {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const dataModelDTO = JSON.parse(reader.result as string);
          this.http.put<void>(url, dataModelDTO).subscribe({
            next: () => {
              console.log('Data model updated successfully (JSON).');
              this.reloadDataModels().subscribe(() => {
                console.log('Data models reloaded after JSON update.');
                observer.next();
                observer.complete();
              });
            },
            error: (error: HttpErrorResponse) => {
              observer.error(this.extractErrorMessage(error, 'updating JSON data model'));
            },
          });
        } catch (error) {
          observer.error('Error parsing JSON file: ' + error);
        }
      };
      reader.readAsText(file);
    });
  }
  updateDataModelFromExcel(dataModelId: string, file: File, version: string, longitudinal: string): Observable<any[]> {
    const url = `${this.apiUrl}/${dataModelId}/excel`;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('version', version);
    formData.append('longitudinal', longitudinal);

    return this.http.put<void>(url, formData).pipe(
      switchMap(() => this.reloadDataModels()), // Reload data models after update
      tap(() => console.log('Data model updated successfully (Excel).')),
      catchError((error: HttpErrorResponse) => {
        const errorMessage = this.extractErrorMessage(error, 'updating Excel data model');
        return throwError(() => errorMessage);
      })
    );
  }
}
