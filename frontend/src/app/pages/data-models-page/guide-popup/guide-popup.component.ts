import {Component, OnInit} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-guide-popup',
  templateUrl: './guide-popup.component.html',
  styleUrls: ['./guide-popup.component.css'],
  imports: [
    FormsModule,
    NgIf
  ],
  standalone: true
})
export class GuidePopupComponent implements OnInit{
  showPopup = true;
  dontShowAgain = false;

  closePopup() {
    this.showPopup = false;

    if (this.dontShowAgain) {
      localStorage.setItem('hideGuidePopup', 'true');
    }
  }

  ngOnInit() {
    const hideGuidePopup = localStorage.getItem('hideGuidePopup');
    if (hideGuidePopup === 'true') {
      this.showPopup = false;
    }
  }
}
