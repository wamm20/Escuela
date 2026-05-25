import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post('/api/login', { username, password });
  }

  setToken(token: string) {
    localStorage.setItem('access_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  logout() {
    localStorage.removeItem('access_token');
  }

  parseJwt(token: string): any {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      const payload = parts[1];
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(decoded);
    } catch (e) {
      return null;
    }
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  // Devuelve el valor `exp` (segundos epoch) si está presente, o null
  getTokenExpiration(token?: string): number | null {
    try {
      const t = token || this.getToken();
      if (!t) return null;
      const parts = t.split('.');
      if (parts.length !== 3) return null;
      // Añadir padding si hace falta
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payload + '='.repeat((4 - (payload.length % 4)) % 4);
      const decoded = atob(padded);
      const obj = JSON.parse(decoded);
      if (!obj || !obj.exp) return null;
      return Number(obj.exp);
    } catch (e) {
      return null;
    }
  }

  // True si el token está expirado (usa reloj del cliente). Se puede pasar un token opcional.
  isTokenExpired(token?: string, leewaySeconds: number = 60): boolean {
    const exp = this.getTokenExpiration(token);
    if (!exp) return true; // sin exp se considera inválido/expirado
    const now = Math.floor(Date.now() / 1000);
    return now > (exp + leewaySeconds);
  }
}
