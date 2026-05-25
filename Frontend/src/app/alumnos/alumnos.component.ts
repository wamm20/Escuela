import { Component, OnInit } from '@angular/core';
import { AlumnoService } from '../services/alumno.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-alumnos',
  templateUrl: './alumnos.component.html',
  styleUrls: ['./alumnos.component.css']
})
export class AlumnosComponent implements OnInit {
  alumnos: any[] = [];
  seleccionado: any = null;
  userLevel: number | null = null;

  constructor(private alumnoService: AlumnoService, private auth: AuthService, private router: Router) { }

  ngOnInit(): void {
    this.checkUserLevel();
    this.cargarAlumnos();
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

  cargarAlumnos() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      this.auth.logout();
      this.router.navigate(['/login']);
      return;
    }
    this.alumnoService.getAlumnos().subscribe(
      (data) => this.alumnos = data,
      (err) => {
        console.error('Error cargando alumnos', err);
        Swal.fire('Error', 'No se pudieron cargar los alumnos.', 'error');
      }
    );
  }

  nuevo() {
    this.seleccionado = { nombre: '', apellido: '', fecha_nacimiento: '', direccion: '', telefono: '', cedula: '', anu_alum: null };
  }

  editar(a: any) {
    this.seleccionado = { ...a };
  }

  cerrar() { this.seleccionado = null; }

  goToMenu() {
    this.router.navigate(['/menu']);
  }

  guardar() {
    if (!this.seleccionado) return;
    // Construir payload sin mutar el objeto mostrado en la UI
    const payload: any = {
      nombre: this.seleccionado.nombre ? this.seleccionado.nombre.toUpperCase() : null,
      apellido: this.seleccionado.apellido ? this.seleccionado.apellido.toUpperCase() : null,
      direccion: this.seleccionado.direccion ? this.seleccionado.direccion.toUpperCase() : null,
      telefono: this.seleccionado.telefono ? this.seleccionado.telefono.toUpperCase() : null,
      cedula: this.seleccionado.cedula || null,
      fecha_nacimiento: this.seleccionado.fecha_nacimiento || null
    };

    // Validaciones de longitud antes de enviar (coinciden con tamaños en la BD)
    const checks = [
      { field: 'nombre', value: payload.nombre, max: 100 },
      { field: 'apellido', value: payload.apellido, max: 100 },
      { field: 'direccion', value: payload.direccion, max: 255 },
      { field: 'telefono', value: payload.telefono, max: 20 },
      { field: 'cedula', value: payload.cedula ? String(payload.cedula) : null, max: 8 }
    ];
    for (const c of checks) {
      if (c.value && c.value.length > c.max) {
        Swal.fire('Error', `El campo ${c.field} supera el máximo de ${c.max} caracteres.`, 'error');
        return;
      }
    }

    if (this.seleccionado.id_alumno) {
      // Mantener id para la ruta del PUT
      payload.id_alumno = this.seleccionado.id_alumno;
      this.alumnoService.updateAlumno(payload).subscribe(
        () => { Swal.fire('Éxito', 'Alumno actualizado.', 'success'); this.cargarAlumnos(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo actualizar.', 'error'); }
      );
    } else {
      this.alumnoService.createAlumno(payload).subscribe(
        () => { Swal.fire('Éxito', 'Alumno creado.', 'success'); this.cargarAlumnos(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo crear.', 'error'); }
      );
    }
  }

  anular(a: any) {
    Swal.fire({ title: 'Anular alumno?', icon: 'warning', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.alumnoService.anularAlumno(a.id_alumno).subscribe(
          () => { Swal.fire('Anulado', 'Alumno anulado correctamente.', 'success'); this.cargarAlumnos(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo anular.', 'error'); }
        );
      }
    });
  }

  activar(a: any) {
    Swal.fire({ title: 'Activar alumno?', icon: 'question', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.alumnoService.activateAlumno(a.id_alumno).subscribe(
          () => { Swal.fire('Activado', 'Alumno activado correctamente.', 'success'); this.cargarAlumnos(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo activar.', 'error'); }
        );
      }
    });
  }

  calcularEdad(fechaNacimiento?: string | null): string | number {
    if (!fechaNacimiento) return '-';
    const nacimiento = new Date(fechaNacimiento);
    if (isNaN(nacimiento.getTime())) return '-';
    const ahora = new Date();
    let edad = ahora.getFullYear() - nacimiento.getFullYear();
    const mesDiff = ahora.getMonth() - nacimiento.getMonth();
    if (mesDiff < 0 || (mesDiff === 0 && ahora.getDate() < nacimiento.getDate())) {
      edad--;
    }
    return edad >= 0 ? edad : '-';
  }
}
