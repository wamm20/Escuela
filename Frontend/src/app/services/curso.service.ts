import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CursoService {
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

  getCursos(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl, { headers: this.getHeaders() });
  }

  getCurso(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  createCurso(curso: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, curso, { headers: this.getHeaders() });
  }

  updateCurso(curso: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${curso.id_curso}`, curso, { headers: this.getHeaders() });
  }

  anularCurso(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  activateCurso(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/activar`, null, { headers: this.getHeaders() });
  }
}
