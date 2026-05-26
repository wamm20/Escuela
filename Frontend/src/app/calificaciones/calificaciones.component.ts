import { Component, OnInit } from '@angular/core';
import Swal from 'sweetalert2';

import { AuthService } from '../services/auth.service';
import { CalificacionService } from '../services/calificacion.service';
import { CursoService } from '../services/curso.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-calificaciones',
  templateUrl: './calificaciones.component.html',
  styleUrls: ['./calificaciones.component.css']
})
export class CalificacionesComponent implements OnInit {
  private readonly notaPattern = /^\d{1,2}(\.\d{1,2})?$/;

  cursos: any[] = [];
  selectedCurso: any = null;

  alumnos: any[] = [];
  materias: any[] = [];
  calificaciones: any[] = [];

  selectedInscripcionId: number | null = null;
  selectedCursoMateriaId: number | null = null;

  nota: string = '';
  fechaCalificacion: string = new Date().toISOString().slice(0, 10);
  currentCalificacionId: number | null = null;

  constructor(
    private cursoService: CursoService,
    private calificacionService: CalificacionService,
    private auth: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.ensureSession();
    this.cargarCursos();
  }

  ensureSession(): void {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      this.router.navigate(['/login']);
    }
  }

  goToMenu(): void {
    this.router.navigate(['/menu']);
  }

  cargarCursos(): void {
    this.cursoService.getCursos().subscribe({
      next: (data) => {
        this.cursos = (data || []).filter((curso: any) => curso.anu_cur !== 'X');
      },
      error: (err) => {
        console.error(err);
        Swal.fire('Error', 'No se pudieron cargar los cursos.', 'error');
      }
    });
  }

  onCursoChange(): void {
    this.resetSelections();
    if (!this.selectedCurso) {
      this.alumnos = [];
      this.materias = [];
      this.calificaciones = [];
      return;
    }

    this.calificacionService.getEstadoCurso(this.selectedCurso.id_curso).subscribe({
      next: (data) => {
        this.alumnos = data?.alumnos || [];
        this.materias = data?.materias || [];
        this.calificaciones = data?.calificaciones || [];
      },
      error: (err) => {
        console.error(err);
        Swal.fire('Error', err?.error?.message || 'No se pudo cargar el módulo de calificaciones.', 'error');
      }
    });
  }

  resetSelections(): void {
    this.selectedInscripcionId = null;
    this.selectedCursoMateriaId = null;
    this.currentCalificacionId = null;
    this.nota = '';
    this.fechaCalificacion = new Date().toISOString().slice(0, 10);
  }

  selectAlumno(idInscripcion: number): void {
    this.selectedInscripcionId = idInscripcion;
    this.syncFormWithExisting();
  }

  selectMateria(idCursoMateria: number): void {
    this.selectedCursoMateriaId = idCursoMateria;
    this.syncFormWithExisting();
  }

  syncFormWithExisting(): void {
    const existing = this.existingCalificacion;
    if (existing) {
      this.currentCalificacionId = existing.id_calificacion;
      this.nota = String(existing.nota);
      this.fechaCalificacion = existing.fecha_calificacion || new Date().toISOString().slice(0, 10);
      return;
    }

    this.currentCalificacionId = null;
    this.nota = '';
    this.fechaCalificacion = new Date().toISOString().slice(0, 10);
  }

  get selectedAlumno(): any | null {
    return this.alumnos.find((item) => item.id_inscripcion === this.selectedInscripcionId) || null;
  }

  get selectedMateria(): any | null {
    return this.materias.find((item) => item.id_curso_materia === this.selectedCursoMateriaId) || null;
  }

  get existingCalificacion(): any | null {
    if (!this.selectedInscripcionId || !this.selectedCursoMateriaId) {
      return null;
    }
    return this.calificaciones.find(
      (item) => item.id_inscripcion === this.selectedInscripcionId && item.id_curso_materia === this.selectedCursoMateriaId
    ) || null;
  }

  get canSave(): boolean {
    const notaText = String(this.nota ?? '').trim();
    const notaValue = Number(notaText);

    return !!this.selectedCurso?.id_curso
      && !!this.selectedInscripcionId
      && !!this.selectedCursoMateriaId
      && this.nota !== null
      && this.nota !== undefined
      && notaText !== ''
      && this.notaPattern.test(notaText)
      && Number.isFinite(notaValue)
      && notaValue >= 1
      && notaValue <= 20
        && !this.fechaError
      && this.fechaCalificacion.trim() !== '';
  }

  get notaError(): string {
    const notaText = String(this.nota ?? '').trim();
    if (!notaText) {
      return '';
    }

    if (!this.notaPattern.test(notaText)) {
      return 'La nota debe tener hasta 2 enteros y 2 decimales.';
    }

    const notaValue = Number(notaText);
    if (!Number.isFinite(notaValue) || notaValue < 1 || notaValue > 20) {
      return 'La nota debe estar entre 1 y 20.';
    }

    return '';
  }

  get maxFechaCalificacion(): string {
    return new Date().toISOString().slice(0, 10);
  }

  get fechaError(): string {
    const fecha = String(this.fechaCalificacion ?? '').trim();
    if (!fecha) {
      return '';
    }

    if (fecha > this.maxFechaCalificacion) {
      return 'La fecha de calificación no puede ser mayor a la fecha actual.';
    }

    return '';
  }

  onNotaChange(value: string): void {
    const normalizedValue = String(value ?? '')
      .replace(/,/g, '.')
      .replace(/[^\d.]/g, '');

    const [integerPartRaw = '', ...decimalParts] = normalizedValue.split('.');
    const integerPart = integerPartRaw.slice(0, 2);
    const decimalPart = decimalParts.join('').slice(0, 2);

    this.nota = decimalPart ? `${integerPart}.${decimalPart}` : integerPart;
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
    return `${nombre} | AÑO: ${anio}`;
  }

  alumnoLabel(alumno: any): string {
    return `${alumno.nombre} ${alumno.apellido}`;
  }

  guardar(): void {
    if (!this.canSave || !this.selectedCurso) {
      return;
    }

    const payload = {
      id_calificacion: this.currentCalificacionId,
      id_curso: this.selectedCurso.id_curso,
      id_inscripcion: this.selectedInscripcionId,
      id_curso_materia: this.selectedCursoMateriaId,
      nota: this.nota,
      fecha_calificacion: this.fechaCalificacion,
    };

    this.calificacionService.guardar(payload).subscribe({
      next: (res) => {
        Swal.fire('Éxito', res?.message || 'Calificación guardada.', 'success');
        const currentInscripcion = this.selectedInscripcionId;
        const currentMateria = this.selectedCursoMateriaId;
        this.onCursoChange();
        this.selectedInscripcionId = currentInscripcion;
        this.selectedCursoMateriaId = currentMateria;
      },
      error: (err) => {
        console.error(err);
        Swal.fire('Error', err?.error?.message || 'No se pudo guardar la calificación.', 'error');
      }
    });
  }
}