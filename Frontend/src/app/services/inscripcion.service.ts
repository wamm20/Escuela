import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class InscripcionService {
  private apiUrl = '/api/inscripciones/cursos';

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }

  getEstadoCurso(cursoId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${cursoId}`, { headers: this.getHeaders() });
  }

  agregar(cursoId: number, alumnoIds: number[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${cursoId}`, { alumnos: alumnoIds }, { headers: this.getHeaders() });
  }

  anular(cursoId: number, inscripcionIds: number[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${cursoId}/anular`, { inscripciones: inscripcionIds }, { headers: this.getHeaders() });
  }

  activar(cursoId: number, inscripcionIds: number[]): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${cursoId}/activar`, { inscripciones: inscripcionIds }, { headers: this.getHeaders() });
  }
}