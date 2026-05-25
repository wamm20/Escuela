import { Component, OnInit } from '@angular/core';
import { ProfesorService } from '../services/profesor.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-profesores',
  templateUrl: './profesores.component.html',
  styleUrls: ['./profesores.component.css']
})
export class ProfesoresComponent implements OnInit {
  profesores: any[] = [];
  seleccionado: any = null;
  userLevel: number | null = null;

  constructor(private profesorService: ProfesorService, private auth: AuthService, private router: Router) { }

  ngOnInit(): void {
    this.checkUserLevel();
    this.cargarProfesores();
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

  cargarProfesores() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      this.auth.logout();
      this.router.navigate(['/login']);
      return;
    }
    this.profesorService.getProfesores().subscribe(
      (data) => this.profesores = data,
      (err) => { console.error('Error cargando profesores', err); Swal.fire('Error', 'No se pudieron cargar los profesores.', 'error'); }
    );
  }

  nuevo() { this.seleccionado = { nombre: '', apellido: '', cedula_prof: '', especialidad: '', email: '' }; }
  editar(p: any) { this.seleccionado = { ...p }; }
  cerrar() { this.seleccionado = null; }

  goToMenu() {
    this.router.navigate(['/menu']);
  }

  guardar() {
    if (!this.seleccionado) return;
    const payload: any = {
      nombre: this.seleccionado.nombre ? this.seleccionado.nombre.toUpperCase() : null,
      apellido: this.seleccionado.apellido ? this.seleccionado.apellido.toUpperCase() : null,
      cedula_prof: this.seleccionado.cedula_prof || null,
      especialidad: this.seleccionado.especialidad ? this.seleccionado.especialidad.toUpperCase() : null,
      email: this.seleccionado.email ? this.seleccionado.email : null
    };

    const checks = [
      { field: 'nombre', value: payload.nombre, max: 100 },
      { field: 'apellido', value: payload.apellido, max: 100 },
      { field: 'cedula_prof', value: payload.cedula_prof ? String(payload.cedula_prof) : null, max: 8 },
      { field: 'especialidad', value: payload.especialidad, max: 255 },
      { field: 'email', value: payload.email, max: 255 }
    ];
    for (const c of checks) {
      if (c.value && c.value.length > c.max) {
        Swal.fire('Error', `El campo ${c.field} supera el máximo de ${c.max} caracteres.`, 'error');
        return;
      }
    }

    if (this.seleccionado.id_profesor) {
      payload.id_profesor = this.seleccionado.id_profesor;
      this.profesorService.updateProfesor(payload).subscribe(
        () => { Swal.fire('Éxito', 'Profesor actualizado.', 'success'); this.cargarProfesores(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo actualizar.', 'error'); }
      );
    } else {
      this.profesorService.createProfesor(payload).subscribe(
        () => { Swal.fire('Éxito', 'Profesor creado.', 'success'); this.cargarProfesores(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo crear.', 'error'); }
      );
    }
  }

  anular(p: any) {
    Swal.fire({ title: 'Anular profesor?', icon: 'warning', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.profesorService.anularProfesor(p.id_profesor).subscribe(
          () => { Swal.fire('Anulado', 'Profesor anulado correctamente.', 'success'); this.cargarProfesores(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo anular.', 'error'); }
        );
      }
    });
  }

  activar(p: any) {
    Swal.fire({ title: 'Activar profesor?', icon: 'question', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.profesorService.activateProfesor(p.id_profesor).subscribe(
          () => { Swal.fire('Activado', 'Profesor activado correctamente.', 'success'); this.cargarProfesores(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo activar.', 'error'); }
        );
      }
    });
  }

  onUpper(field: string, value: any) {
    if (!this.seleccionado) return;
    this.seleccionado[field] = value == null ? null : String(value).toUpperCase();
  }

  onDigitsOnly(field: string, value: any) {
    if (!this.seleccionado) return;
    const cleaned = value == null ? null : String(value).replace(/\D+/g, '');
    this.seleccionado[field] = cleaned;
  }
}
