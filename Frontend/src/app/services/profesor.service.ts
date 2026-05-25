import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProfesorService {
  private apiUrl = '/api/profesores';

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }

  getProfesores(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.getHeaders() });
  }

  getProfesor(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  createProfesor(profesor: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, profesor, { headers: this.getHeaders() });
  }

  updateProfesor(profesor: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${profesor.id_profesor}`, profesor, { headers: this.getHeaders() });
  }

  anularProfesor(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  activateProfesor(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/activar`, null, { headers: this.getHeaders() });
  }
}
