import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProgramaService {
  private apiUrl = '/api/programas';

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }

  getProgramas(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.getHeaders() });
  }

  getPrograma(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  createPrograma(programa: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, programa, { headers: this.getHeaders() });
  }

  updatePrograma(programa: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${programa.id_program}`, programa, { headers: this.getHeaders() });
  }

  anularPrograma(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  activatePrograma(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/activar`, null, { headers: this.getHeaders() });
  }
}