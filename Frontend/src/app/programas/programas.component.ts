import { Component, OnInit } from '@angular/core';
import { ProgramaService } from '../services/programa.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-programas',
  templateUrl: './programas.component.html',
  styleUrls: ['./programas.component.css']
})
export class ProgramasComponent implements OnInit {
  programas: any[] = [];
  seleccionado: any = null;
  userLevel: number | null = null;

  constructor(private programaService: ProgramaService, private auth: AuthService, private router: Router) { }

  ngOnInit(): void {
    this.checkUserLevel();
    this.cargarProgramas();
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

  cargarProgramas() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      this.auth.logout();
      this.router.navigate(['/login']);
      return;
    }
    this.programaService.getProgramas().subscribe(
      (data) => this.programas = data,
      (err) => {
        console.error('Error cargando programas', err);
        Swal.fire('Error', 'No se pudieron cargar los programas.', 'error');
      }
    );
  }

  nuevo() {
    this.seleccionado = { nombre_program: '' };
  }

  editar(programa: any) {
    this.seleccionado = { ...programa };
  }

  cerrar() {
    this.seleccionado = null;
  }

  goToMenu() {
    this.router.navigate(['/menu']);
  }

  guardar() {
    if (!this.seleccionado) return;
    const payload: any = {
      nombre_program: this.seleccionado.nombre_program ? this.seleccionado.nombre_program.toUpperCase() : null
    };

    if (payload.nombre_program && payload.nombre_program.length > 255) {
      Swal.fire('Error', 'El campo nombre_program supera el máximo de 255 caracteres.', 'error');
      return;
    }

    if (this.seleccionado.id_program) {
      payload.id_program = this.seleccionado.id_program;
      this.programaService.updatePrograma(payload).subscribe(
        () => { Swal.fire('Éxito', 'Programa actualizado.', 'success'); this.cargarProgramas(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo actualizar.', 'error'); }
      );
    } else {
      this.programaService.createPrograma(payload).subscribe(
        () => { Swal.fire('Éxito', 'Programa creado.', 'success'); this.cargarProgramas(); this.cerrar(); },
        (err) => { console.error(err); Swal.fire('Error', 'No se pudo crear.', 'error'); }
      );
    }
  }

  anular(programa: any) {
    Swal.fire({ title: 'Anular programa?', icon: 'warning', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.programaService.anularPrograma(programa.id_program).subscribe(
          () => { Swal.fire('Anulado', 'Programa anulado correctamente.', 'success'); this.cargarProgramas(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo anular.', 'error'); }
        );
      }
    });
  }

  activar(programa: any) {
    Swal.fire({ title: 'Activar programa?', icon: 'question', showCancelButton: true }).then((res) => {
      if (res.isConfirmed) {
        this.programaService.activatePrograma(programa.id_program).subscribe(
          () => { Swal.fire('Activado', 'Programa activado correctamente.', 'success'); this.cargarProgramas(); },
          (err) => { console.error(err); Swal.fire('Error', 'No se pudo activar.', 'error'); }
        );
      }
    });
  }
}