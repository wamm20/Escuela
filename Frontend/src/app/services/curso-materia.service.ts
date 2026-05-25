import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CursoMateriaService {
  private apiUrl = '/api/cursos';

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  }

  list(cursoId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${cursoId}/materias`, { headers: this.getHeaders() });
  }

  addOrUpdate(cursoId: number, assignments: Array<{id_materia:number, id_profesor:number}>): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${cursoId}/materias`, assignments, { headers: this.getHeaders() });
  }

  anular(cursoId: number, id_curso_materia: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${cursoId}/materias/${id_curso_materia}/anular`, null, { headers: this.getHeaders() });
  }

  activar(cursoId: number, id_curso_materia: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${cursoId}/materias/${id_curso_materia}/activar`, null, { headers: this.getHeaders() });
  }
}
