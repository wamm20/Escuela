import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent {
  settingsOpen = false;

  constructor(private auth: AuthService, private router: Router) {}

  toggleSettings() {
    this.settingsOpen = !this.settingsOpen;
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
