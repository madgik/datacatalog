import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FederationService } from '../../services/federation.service';
import { Federation } from "../../interfaces/federations.interface";
import { AuthService } from '../../services/auth.service';
import {Router} from "@angular/router";

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.css'],
})
export class LandingPageComponent implements OnInit {
  federations: Federation[] = [];
  selectedFederation!: Federation;

  constructor(
    private federationService: FederationService,
    private authService: AuthService,
    private router: Router

  ) {}

  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  redirectToSignUp(): void {
    window.open('https://www.ebrains.eu/page/sign-up', '_blank');
  }

  navigateToFederation(url: string): void {
      window.open(url, '_blank');
  }

  learnMore(): void {
    this.router.navigate(['/about']);
  }

  getStarted(): void {
    this.router.navigate(['/federations']);
  }

  ngOnInit(): void {
    // Check if user is logged in

    // Load federations
    this.federationService.getFederationsWithModels().subscribe({
      next: (federations) => {
        this.federations = federations;
      },
      error: (error) => console.error('Error loading federations:', error)
    });
  }

  selectDefaultFederation(): void {
    if (this.federations.length > 0) {
      this.selectedFederation = this.federations[0];
    }
  }

  selectFederation(federation: Federation): void {
    this.selectedFederation = federation;
  }
}
