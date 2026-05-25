import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AlumnoService {
  private apiUrl = '/api/alumnos';

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }

  getAlumnos(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.getHeaders() });
  }

  getAlumno(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  createAlumno(alumno: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, alumno, { headers: this.getHeaders() });
  }

  updateAlumno(alumno: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${alumno.id_alumno}`, alumno, { headers: this.getHeaders() });
  }

  anularAlumno(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  activateAlumno(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/activar`, null, { headers: this.getHeaders() });
  }
}
