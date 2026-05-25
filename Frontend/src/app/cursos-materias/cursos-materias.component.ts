import { Component, OnInit } from '@angular/core';
import { CursoService } from '../services/curso.service';
import { CursoMateriaService } from '../services/curso-materia.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-cursos-materias',
  templateUrl: './cursos-materias.component.html',
  styleUrls: ['./cursos-materias.component.css']
})
export class CursosMateriasComponent implements OnInit {
  cursos: any[] = [];
  selectedCurso: any = null;

  asignaciones: any[] = [];
  userLevel: number | null = null;

  constructor(
    private cursoService: CursoService,
    private cursoMateriaService: CursoMateriaService,
    private auth: AuthService,
    private router: Router
  ) { }

  goToMenu() {
    this.router.navigate(['/menu']);
  }

  ngOnInit(): void {
    this.checkUserLevel();
    this.loadCourses();
  }

  checkUserLevel() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      this.userLevel = null;
      return;
    }
    const payload = this.auth.parseJwt ? this.auth.parseJwt(token) : null;
    this.userLevel = payload ? payload.user_level : null;
  }

  loadCourses() {
    this.cursoService.getCursos().subscribe(
      data => this.cursos = data,
      err => { console.error(err); Swal.fire('Error','No se pudieron cargar los cursos','error'); }
    );
  }

  formatDate(value: string | null | undefined): string {
    if (!value) {
      return 'N/A';
    }

    const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!match) {
      return value;
    }

    const [, year, month, day] = match;
    return `${day}-${month}-${year}`;
  }

  getCursoLabel(curso: any): string {
    if (!curso) {
      return '';
    }

    const nombre = curso.nombre_curso || 'SIN NOMBRE';
    const anio = curso.anio_escolar || 'N/A';
    const fechaInicio = this.formatDate(curso.fecha_inicio);
    const fechaFin = this.formatDate(curso.fecha_fin);

    return `${nombre} | AÑO: ${anio} | INICIO: ${fechaInicio} | FIN: ${fechaFin}`;
  }

  onCourseChange() {
    if (!this.selectedCurso) {
      this.asignaciones = [];
      return;
    }
    this.cursoMateriaService.list(this.selectedCurso.id_curso).subscribe(
      a => this.asignaciones = a,
      err => { console.error(err); Swal.fire('Error','No se pudieron cargar las asignaciones','error'); }
    );
  }

  getAsignacion(id_materia: number) {
    return this.asignaciones.find(x => x.id_materia === id_materia) || null;
  }

  // acciones contra asignaciones

  anularFila(id_cm: number | undefined) {
    if (!id_cm) return;
    Swal.fire({title:'Anular asignación?',icon:'warning',showCancelButton:true}).then(res=>{
      if(res.isConfirmed){
        this.cursoMateriaService.anular(this.selectedCurso.id_curso, id_cm).subscribe(
          () => { this.onCourseChange(); Swal.fire('Anulado','Registro anulado','success'); },
          err => { console.error(err); Swal.fire('Error','No se pudo anular','error'); }
        );
      }
    });
  }

  activarFila(id_cm: number | undefined) {
    if (!id_cm) return;
    Swal.fire({title:'Activar asignación?',icon:'question',showCancelButton:true}).then(res=>{
      if(res.isConfirmed){
        this.cursoMateriaService.activar(this.selectedCurso.id_curso, id_cm).subscribe(
          () => { this.onCourseChange(); Swal.fire('Activado','Registro activado','success'); },
          err => { console.error(err); Swal.fire('Error','No se pudo activar','error'); }
        );
      }
    });
  }
}
