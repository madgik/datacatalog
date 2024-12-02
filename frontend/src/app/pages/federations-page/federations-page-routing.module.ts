import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FederationFormComponent } from './federation-form/federation-form.component';

const routes: Routes = [
  {
    path: 'add',
    component: FederationFormComponent,
    data: { isUpdate: false },
  },
  {
    path: 'update',
    component: FederationFormComponent,
    data: { isUpdate: true },
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class FederationsPageRoutingModule {}
