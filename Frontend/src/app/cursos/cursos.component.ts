import { Component, OnInit } from '@angular/core';
import { CursoService } from '../services/curso.service';
import { CursoMateriaService } from '../services/curso-materia.service';
import { MateriaService } from '../services/materia.service';
import { ProfesorService } from '../services/profesor.service';
import { ProgramaService } from '../services/programa.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-cursos',
  templateUrl: './cursos.component.html',
  styleUrls: ['./cursos.component.css']
})
export class CursosComponent implements OnInit {
  cursos: any[] = [];
  seleccionado: any = null;
  userLevel: number | null = null;
  programas: any[] = [];

  // asignaciones
  materias: any[] = [];
  profesores: any[] = [];
  asignaciones: any[] = [];
  showAsignacionesModal = false;
  cursoParaAsignar: any = null;

  constructor(
    private cursoService: CursoService,
    private cursoMateriaService: CursoMateriaService,
    private materiaService: MateriaService,
    private profesorService: ProfesorService,
    private programaService: ProgramaService,
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

  cargarCursos() {
    // same as before
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      this.auth.logout();
      this.router.navigate(['/login']);
      return;
    }
    this.cursoService.getCursos().subscribe(
      (data) => this.cursos = data,
      (err) => {
        console.error('Error cargando cursos', err);
        Swal.fire('Error', 'No se pudieron cargar los cursos.', 'error');
      }
    );
  }

  nuevo() {
    this.seleccionado = { id_program: null, nombre_curso: '', anio_escolar: '', fecha_inicio: '', fecha_fin: '', estado_curso: 'ACTIVO' };
    this.cargarProgramasActivos();
  }

  editar(c: any) {
    this.seleccionado = {...c};
  }

  cerrar() { this.seleccionado = null; }

  cargarProgramasActivos() {
    this.programaService.getProgramas().subscribe(
      (data) => {
        this.programas = (data || []).filter((programa: any) => programa.anu_prog !== 'X');
      },
      (err) => {
        console.error('Error cargando programas', err);
        this.programas = [];
        Swal.fire('Error', 'No se pudieron cargar los programas.', 'error');
      }
    );
  }

  onProgramaChange() {
    if (!this.seleccionado) return;
    const idProgram = Number(this.seleccionado.id_program);
    const programa = this.programas.find((item: any) => item.id_program === idProgram);
    this.seleccionado.nombre_curso = programa ? (programa.nombre_program || '') : '';
  }

  goToMenu() {
    this.router.navigate(['/menu']);
  }

  guardar() {
    if (!this.seleccionado) return;

    const isCreate = !this.seleccionado.id_curso;
    if (isCreate) {
      if (!this.seleccionado.id_program) {
        Swal.fire('Error', 'Debe seleccionar un programa.', 'error');
        return;
      }
      this.onProgramaChange();
      if (!this.seleccionado.nombre_curso) {
        Swal.fire('Error', 'El programa seleccionado no tiene nombre válido.', 'error');
        return;
      }
    }

    const payload: any = {
      nombre_curso: this.seleccionado.nombre_curso ? this.seleccionado.nombre_curso.toUpperCase() : null,
      anio_escolar: this.seleccionado.anio_escolar ? this.seleccionado.anio_escolar.toUpperCase() : null,
      fecha_inicio: this.seleccionado.fecha_inicio || null,
      fecha_fin: this.seleccionado.fecha_fin || null,
      estado_curso: this.seleccionado.estado_curso ? this.seleccionado.estado_curso.toUpperCase() : null
    };

    // validations
    const checks = [
      { field: 'nombre_curso', value: payload.nombre_curso, max: 255 },
      { field: 'anio_escolar', value: payload.anio_escolar, max: 50 },
      { field: 'estado_curso', value: payload.estado_curso, max: 50 }
    ];
    for (const cck of checks) {
      if (cck.value && cck.value.length > cck.max) {
        Swal.fire('Error', `El campo ${cck.field} supera el máximo de ${cck.max} caracteres.`, 'error');
        return;
      }
    }

    if (this.seleccionado.id_curso) {
      payload.id_curso = this.seleccionado.id_curso;
      this.cursoService.updateCurso(payload).subscribe(
        () => { Swal.fire('Éxito', 'Curso actualizado.', 'success'); this.cargarCursos(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo actualizar.', 'error'); }
      );
    } else {
      this.cursoService.createCurso(payload).subscribe(
        (res) => {
          const newId = res?.id_curso;
          // update seleccionado to include id in case the modal reopens
          if (newId) {
            this.seleccionado.id_curso = newId;
          }
          Swal.fire({
            title: 'Curso creado',
            text: '¿Desea asignar materias ahora?',
            icon: 'success',
            showCancelButton: true,
            confirmButtonText: 'Sí',
            cancelButtonText: 'No'
          }).then((resp) => {
            this.cargarCursos();
            this.cerrar();
            if (resp.isConfirmed && newId) {
              this.abrirAsignaciones({ id_curso: newId, nombre_curso: payload.nombre_curso });
            }
          });
        },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo crear.', 'error'); }
      );
    }
  }

  anular(c: any) {
    Swal.fire({ title: 'Anular curso?', icon: 'warning', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.cursoService.anularCurso(c.id_curso).subscribe(
          () => { Swal.fire('Anulado', 'Curso anulado correctamente.', 'success'); this.cargarCursos(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo anular.', 'error'); }
        );
      }
    });
  }

  abrirAsignaciones(c: any) {
    this.cursoParaAsignar = c;
    this.showAsignacionesModal = true;
    // cargar materias y profesores y asignaciones
    this.materiaService.getMaterias().subscribe((m) => this.materias = m);
    this.profesorService.getProfesores().subscribe((p) => this.profesores = p);
    this.cursoMateriaService.list(c.id_curso).subscribe(
      (asig) => { this.asignaciones = asig; },
      (err) => { console.error(err); Swal.fire('Error', 'No se pudieron cargar las asignaciones.', 'error'); }
    );
  }

  getProfesorAsignado(id_materia: number): number | null {
    const a = this.asignaciones.find(x => x.id_materia === id_materia);
    return a ? a.id_profesor : null;
  }

  onProfesorChanged(id_materia: number, id_profesor: number | null) {
    let a = this.asignaciones.find(x => x.id_materia === id_materia);
    if (a) {
      a.id_profesor = id_profesor;
    } else {
      this.asignaciones.push({ id_materia, id_profesor });
    }
  }

  guardarAsignaciones() {
    if (!this.cursoParaAsignar) return;
    const payload: Array<{id_materia:number,id_profesor:number}> = [];
    for (const m of this.materias) {
      const profesorSelec = this.getProfesorAsignado(m.id_materia);
      if (profesorSelec) {
        payload.push({ id_materia: m.id_materia, id_profesor: profesorSelec });
      }
    }
    if (payload.length === 0) {
      Swal.fire('Advertencia','Seleccione al menos un profesor para una materia','warning');
      return;
    }
    this.cursoMateriaService.addOrUpdate(this.cursoParaAsignar.id_curso, payload).subscribe(
      () => { Swal.fire('Éxito','Asignaciones guardadas','success'); this.showAsignacionesModal=false; },
      (err) => { console.error(err); Swal.fire('Error','No se pudieron guardar asignaciones','error'); }
    );
  }

  activar(c: any) {
    Swal.fire({ title: 'Activar curso?', icon: 'question', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.cursoService.activateCurso(c.id_curso).subscribe(
          () => { Swal.fire('Activado', 'Curso activado correctamente.', 'success'); this.cargarCursos(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo activar.', 'error'); }
        );
      }
    });
  }
}
