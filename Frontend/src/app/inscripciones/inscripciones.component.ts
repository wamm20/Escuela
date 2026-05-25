import { Component, OnInit } from '@angular/core';
import { CursoService } from '../services/curso.service';
import { InscripcionService } from '../services/inscripcion.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-inscripciones',
  templateUrl: './inscripciones.component.html',
  styleUrls: ['./inscripciones.component.css']
})
export class InscripcionesComponent implements OnInit {
  cursos: any[] = [];
  selectedCurso: any = null;
  disponibles: any[] = [];
  inscritos: any[] = [];
  selectedDisponibles: Record<number, boolean> = {};
  selectedInscritos: Record<number, boolean> = {};
  userLevel: number | null = null;

  constructor(
    private cursoService: CursoService,
    private inscripcionService: InscripcionService,
    private auth: AuthService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.checkUserLevel();
    this.cargarCursos();
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

  goToMenu() {
    this.router.navigate(['/menu']);
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

  cargarCursos() {
    this.cursoService.getCursos().subscribe(
      (data) => {
        this.cursos = (data || []).filter((curso: any) => curso.anu_cur !== 'X');
      },
      (err) => {
        console.error(err);
        Swal.fire('Error', 'No se pudieron cargar los cursos.', 'error');
      }
    );
  }

  onCourseChange() {
    this.selectedDisponibles = {};
    this.selectedInscritos = {};

    if (!this.selectedCurso) {
      this.disponibles = [];
      this.inscritos = [];
      return;
    }

    this.inscripcionService.getEstadoCurso(this.selectedCurso.id_curso).subscribe(
      (data) => {
        this.disponibles = data?.disponibles || [];
        this.inscritos = data?.inscritos || [];
      },
      (err) => {
        console.error(err);
        Swal.fire('Error', 'No se pudo cargar el estado de inscripciones del curso.', 'error');
      }
    );
  }

  get selectedAlumnoIds(): number[] {
    return Object.keys(this.selectedDisponibles)
      .filter((key) => this.selectedDisponibles[Number(key)])
      .map((key) => Number(key));
  }

  get selectedInscripcionRows(): any[] {
    return this.inscritos.filter((item) => this.selectedInscritos[item.id_inscripcion]);
  }

  get canAgregar(): boolean {
    return this.selectedAlumnoIds.length > 0;
  }

  get canAnular(): boolean {
    return this.selectedInscripcionRows.length > 0 && this.selectedInscripcionRows.every((item) => item.anu_alum !== 'X');
  }

  get canActivar(): boolean {
    return this.selectedInscripcionRows.length > 0 && this.selectedInscripcionRows.every((item) => item.anu_alum === 'X');
  }

  agregarSeleccionados() {
    if (!this.selectedCurso || !this.canAgregar) {
      return;
    }

    this.inscripcionService.agregar(this.selectedCurso.id_curso, this.selectedAlumnoIds).subscribe(
      () => {
        Swal.fire('Éxito', 'Inscripciones agregadas correctamente.', 'success');
        this.onCourseChange();
      },
      (err) => {
        console.error(err);
        Swal.fire('Error', err?.error?.message || 'No se pudieron agregar las inscripciones.', 'error');
      }
    );
  }

  anularSeleccionados() {
    if (!this.selectedCurso || !this.canAnular) {
      return;
    }

    const ids = this.selectedInscripcionRows.map((item) => item.id_inscripcion);
    Swal.fire({ title: 'Suspender inscripciones?', icon: 'warning', showCancelButton: true }).then((result) => {
      if (!result.isConfirmed) {
        return;
      }

      this.inscripcionService.anular(this.selectedCurso.id_curso, ids).subscribe(
        () => {
          Swal.fire('Suspendidas', 'Las inscripciones fueron suspendidas.', 'success');
          this.onCourseChange();
        },
        (err) => {
          console.error(err);
          Swal.fire('Error', err?.error?.message || 'No se pudieron suspender las inscripciones.', 'error');
        }
      );
    });
  }

  activarSeleccionados() {
    if (!this.selectedCurso || !this.canActivar) {
      return;
    }

    const ids = this.selectedInscripcionRows.map((item) => item.id_inscripcion);
    Swal.fire({ title: 'Activar inscripciones?', icon: 'question', showCancelButton: true }).then((result) => {
      if (!result.isConfirmed) {
        return;
      }

      this.inscripcionService.activar(this.selectedCurso.id_curso, ids).subscribe(
        () => {
          Swal.fire('Activadas', 'Las inscripciones fueron activadas.', 'success');
          this.onCourseChange();
        },
        (err) => {
          console.error(err);
          Swal.fire('Error', err?.error?.message || 'No se pudieron activar las inscripciones.', 'error');
        }
      );
    });
  }
}