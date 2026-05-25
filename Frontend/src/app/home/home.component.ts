import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { AlumnoService } from '../services/alumno.service';
import { CursoService } from '../services/curso.service';
import { MateriaService } from '../services/materia.service';
import { ProfesorService } from '../services/profesor.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  username = '';

  alumnosCount = 0;
  cursosCount = 0;
  materiasCount = 0;
  profesoresCount = 0;

  constructor(
    private auth: AuthService,
    private router: Router,
    private alumnoService: AlumnoService,
    private cursoService: CursoService,
    private materiaService: MateriaService,
    private profesorService: ProfesorService
  ) {}

  ngOnInit(): void {
    // prevent page scrollbar while on dashboard
    document.body.style.overflow = 'hidden';
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
    try {
      const payload = this.auth.parseJwt(token);
      this.username = payload?.username || '';
      const nom = (payload?.nom_usuario || '').trim();
      const ape = (payload?.ape_usuario || '').trim();
      if (nom || ape) {
        this.username = (nom + ' ' + ape).trim();
      }
    } catch (e) {
      this.router.navigate(['/login']);
    }

    // cargar estadísticas dinámicas
    this.loadStats();

    // refrescar al volver al menú principal
    this.router.events.subscribe(ev => {
      // recargar en cada NavigationEnd hacia /menu (o '/home' si lo tienes)
      if (ev.constructor.name === 'NavigationEnd') {
        const ne: any = ev;
        if (ne.urlAfterRedirects === '/menu' || ne.urlAfterRedirects === '/home') {
          this.loadStats();
        }
      }
    });
  }

  loadStats() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) return;

    this.alumnoService.getAlumnos().subscribe(a => this.alumnosCount = a.length, _ => {});
    this.cursoService.getCursos().subscribe(c => this.cursosCount = c.length, _ => {});
    this.materiaService.getMaterias().subscribe(m => this.materiasCount = m.length, _ => {});
    this.profesorService.getProfesores().subscribe(p => this.profesoresCount = p.length, _ => {});
  }

  ngOnDestroy(): void {
    document.body.style.overflow = '';
  }

}
