import { Component, OnInit } from '@angular/core';
import { MateriaService } from '../services/materia.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-materias',
  templateUrl: './materias.component.html',
  styleUrls: ['./materias.component.css']
})
export class MateriasComponent implements OnInit {
  materias: any[] = [];
  seleccionado: any = null;
  userLevel: number | null = null;

  constructor(private materiaService: MateriaService, private auth: AuthService, private router: Router) { }

  ngOnInit(): void {
    this.checkUserLevel();
    this.cargarMaterias();
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

  cargarMaterias() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      this.auth.logout();
      this.router.navigate(['/login']);
      return;
    }
    this.materiaService.getMaterias().subscribe(
      (data) => this.materias = data,
      (err) => {
        console.error('Error cargando materias', err);
        Swal.fire('Error', 'No se pudieron cargar las materias.', 'error');
      }
    );
  }

  nuevo() {
    this.seleccionado = { nombre_materia: '' };
  }

  editar(m: any) {
    this.seleccionado = { ...m };
  }

  cerrar() { this.seleccionado = null; }

  goToMenu() {
    this.router.navigate(['/menu']);
  }

  guardar() {
    if (!this.seleccionado) return;
    const payload: any = {
      nombre_materia: this.seleccionado.nombre_materia ? this.seleccionado.nombre_materia.toUpperCase() : null
    };

    // validación de longitud
    if (payload.nombre_materia && payload.nombre_materia.length > 255) {
      Swal.fire('Error', `El campo nombre_materia supera el máximo de 255 caracteres.`, 'error');
      return;
    }

    if (this.seleccionado.id_materia) {
      payload.id_materia = this.seleccionado.id_materia;
      this.materiaService.updateMateria(payload).subscribe(
        () => { Swal.fire('Éxito', 'Materia actualizada.', 'success'); this.cargarMaterias(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo actualizar.', 'error'); }
      );
    } else {
      this.materiaService.createMateria(payload).subscribe(
        () => { Swal.fire('Éxito', 'Materia creada.', 'success'); this.cargarMaterias(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo crear.', 'error'); }
      );
    }
  }

  anular(m: any) {
    Swal.fire({ title: 'Anular materia?', icon: 'warning', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.materiaService.anularMateria(m.id_materia).subscribe(
          () => { Swal.fire('Anulado', 'Materia anulada correctamente.', 'success'); this.cargarMaterias(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo anular.', 'error'); }
        );
      }
    });
  }

  activar(m: any) {
    Swal.fire({ title: 'Activar materia?', icon: 'question', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.materiaService.activateMateria(m.id_materia).subscribe(
          () => { Swal.fire('Activado', 'Materia activada correctamente.', 'success'); this.cargarMaterias(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo activar.', 'error'); }
        );
      }
    });
  }
}
