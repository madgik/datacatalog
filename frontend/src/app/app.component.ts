import { FooterComponent } from './pages/shared/footer/footer.component';
import { Component, OnInit } from '@angular/core';
import { HeaderComponent } from './pages/shared/header/header.component';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, RouterModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'datacatalog-frontend';

  ngOnInit(): void {
    this.clearTokenOnInit();
  }

  private clearTokenOnInit(): void {
    // Check if the token should be cleared (example condition)
    const token = localStorage.getItem('auth_token');
    if (token) {
      localStorage.removeItem('auth_token');
      console.log('Token cleared during initialization');
    }
  }
}
