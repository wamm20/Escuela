import { Component, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from './services/auth.service';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  template: `
    <div class="app-shell">
      <aside class="left" *ngIf="showShell">
        <app-sidebar></app-sidebar>
      </aside>
      <div class="right" [class.full]="!showShell" [class.menu-view]="isMenuRoute">
        <header class="topbar" *ngIf="showShell">
          <div class="top-left">
            <div class="username">{{ displayName || username }}</div>
          </div>
          <div class="top-right">
            <div class="clock">{{ time }}</div>
          </div>
        </header>
        <main class="content-area">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  username = '';
  displayName = '';
  time = '';
  private timerId: any;
  showShell = false;
  isMenuRoute = false;

  constructor(private auth: AuthService, private router: Router) {}

  ngOnInit(): void {
    // 1. Suscribirse a eventos de navegación PRIMERO para asegurar que se actualice el sidebar
    this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((ev: NavigationEnd) => {
        const u = ev.urlAfterRedirects || ev.url;
        this.checkSidebar(u);
        this.refreshHeaderInfo();
      });

    // 2. Chequeo inicial
    this.checkSidebar(this.router.url);

    this.refreshHeaderInfo();
    this.timerId = setInterval(() => this.updateTime(), 1000);
  }

  ngOnDestroy(): void {
    if (this.timerId) clearInterval(this.timerId);
  }

  updateTime() {
    const d = new Date();
    this.time = d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit', hour12: true });
  }

  private refreshHeaderInfo() {
    const token = this.auth.getToken();
    if (!token) {
      this.username = '';
      this.displayName = '';
      this.time = '';
      return;
    }

    if (this.auth.isTokenExpired(token)) {
      this.username = '';
      this.displayName = '';
      this.time = '';
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

    this.updateTime();
  }

  private checkSidebar(url: string) {
    this.isMenuRoute = url.includes('/menu');

    // Ocultar sidebar en login, welcome y raíz
    if (url === '/' || url.includes('/login') || url.includes('/welcome')) {
      this.showShell = false;
    } else {
      this.showShell = true;
    }
  }
}
