import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.css']
})
export class WelcomeComponent implements OnInit, OnDestroy {
  username = '';
  displayName = '';
  private tId: any;

  constructor(private auth: AuthService, private router: Router) {}

  ngOnInit(): void {
    const token = this.auth.getToken();
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }
    if (this.auth.isTokenExpired(token)) {
      this.auth.logout();
      this.router.navigate(['/login']);
      return;
    }
    const payload: any = this.auth.parseJwt(token) || {};
    this.username = payload?.username || '';
    const nom = (payload?.nom_usuario || '').trim();
    const ape = (payload?.ape_usuario || '').trim();
    if (nom || ape) {
      this.displayName = (nom + ' ' + ape).trim();
    } else if (payload?.username) {
      this.displayName = payload.username;
    } else if (payload?.email) {
      this.displayName = payload.email;
    } else {
      this.displayName = '';
    }

    // Mostrar welcome 3s y navegar al menú
    this.tId = setTimeout(() => {
      this.router.navigate(['/menu']);
    }, 3000);
  }

  ngOnDestroy(): void {
    if (this.tId) clearTimeout(this.tId);
  }
}
