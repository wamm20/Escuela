import { Component, OnInit } from '@angular/core';
import { UserService } from '../services/user.service';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-usuarios',
  templateUrl: './usuarios.component.html',
  styleUrls: ['./usuarios.component.css']
})
export class UsuariosComponent implements OnInit {
  usuarios: any[] = [];
  usuarioSeleccionado: any = null; // Objeto para el modal de edición
  userLevel: number | null = null;

  constructor(private userService: UserService, private router: Router, private auth: AuthService) { }

  ngOnInit(): void {
    this.checkUserLevel();
    this.cargarUsuarios();
  }

  checkUserLevel() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      // Forzar logout/redirect si no hay token o está vencido
      this.userLevel = null;
      return;
    }

    const payload = this.auth.parseJwt(token) || {};
    this.userLevel = payload.user_level;
    if (this.userLevel === undefined || this.userLevel === null) {
      console.warn('El token no contiene user_level. Es posible que sea un token antiguo.');
    }
  }

  cargarUsuarios() {
    const token = this.auth.getToken();
    if (!token || this.auth.isTokenExpired(token)) {
      Swal.fire({
        title: 'Sesión Expirada',
        text: 'Su sesión ha caducado. Por favor ingrese nuevamente.',
        icon: 'warning',
        confirmButtonText: 'Ir al Login'
      }).then(() => {
        this.auth.logout();
        this.router.navigate(['/login']);
      });
      return;
    }

    this.userService.getUsers().subscribe(
      (data) => {
        this.usuarios = data;
        console.log('Usuarios cargados:', this.usuarios);
      },
      (error) => {
        console.error('Error al cargar usuarios:', error);
        if (error.status === 401) {
          Swal.fire({
            title: 'Sesión Expirada',
            text: 'Su sesión ha caducado. Por favor ingrese nuevamente.',
            icon: 'warning',
            confirmButtonText: 'Ir al Login'
          }).then(() => {
            this.auth.logout();
            this.router.navigate(['/login']);
          });
        } else {
          Swal.fire('Error', 'No se pudieron cargar los usuarios. Verifique su sesión.', 'error');
        }
      }
    );
  }

  nuevoUsuario() {
    this.usuarioSeleccionado = {
      ci_usuario: '',
      nom_usuario: '',
      ape_usuario: '',
      nvl_usuario: null,
      cargo_usuario: '',
      usuario: '',
      password: '', // Campo para la contraseña
      anu_usu: null
    };
  }

  editarUsuario(usuario: any) {
    // Creamos una copia para editar sin afectar la fila de la tabla inmediatamente
    this.usuarioSeleccionado = { ...usuario };
  }

  cerrarModal() {
    this.usuarioSeleccionado = null;
  }

  goToMenu() {
    this.router.navigate(['/menu']);
  }

  guardarEdicion() {
    if (!this.usuarioSeleccionado) return;

    // Aseguramos mayúsculas en el frontend también para feedback visual inmediato
    const u = this.usuarioSeleccionado;
    u.nom_usuario = u.nom_usuario?.toUpperCase();
    u.ape_usuario = u.ape_usuario?.toUpperCase();
    u.cargo_usuario = u.cargo_usuario?.toUpperCase();
    u.usuario = u.usuario?.toUpperCase();
    u.ci_usuario = u.ci_usuario?.toUpperCase();

    if (u.id_usuario) {
      // Edición (PUT)
      this.userService.updateUser(u).subscribe(
        (response: any) => {
          Swal.fire('Éxito', 'Usuario actualizado correctamente.', 'success');
          this.cargarUsuarios();
          this.cerrarModal();
        },
        (error: any) => {
          console.error('Error al actualizar:', error);
          Swal.fire('Error', 'No se pudo actualizar el usuario.', 'error');
        }
      );
    } else {
      // Creación (POST)
      this.userService.createUser(u).subscribe(
        (response: any) => {
          Swal.fire('Éxito', 'Usuario creado correctamente.', 'success');
          this.cargarUsuarios();
          this.cerrarModal();
        },
        (error: any) => {
          console.error('Error al crear:', error);
          Swal.fire('Error', 'No se pudo crear el usuario. Verifique si el usuario ya existe.', 'error');
        }
      );
    }
  }

  anularUsuario(usuario: any) {
    Swal.fire({
      title: '¿Está Seguro de Anular este Usuario?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Si',
      cancelButtonText: 'No'
    }).then((result) => {
      if (result.isConfirmed) {
        // Se coloca la X al campo anu_usu
        usuario.anu_usu = 'X';
        
        // Aquí deberías llamar al servicio para guardar el cambio en la BD
        // this.userService.updateUser(usuario).subscribe(...)
        
        console.log('Usuario anulado (anu_usu="X"):', usuario);
        
        this.userService.updateUser(usuario).subscribe(
          (response: any) => {
            console.log('Usuario anulado (anu_usu="X"):', usuario);
            Swal.fire(
              '¡Anulado!',
              'El usuario ha sido anulado correctamente.',
              'success'
            );
          },
          (error: any) => {
            console.error('Error al anular usuario:', error);
            Swal.fire('Error', 'No se pudo guardar el cambio en la base de datos.', 'error');
          }
        );
      }
    });
  }

  activarUsuario(usuario: any) {
    Swal.fire({
      title: '¿Activar este Usuario?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Sí',
      cancelButtonText: 'No'
    }).then((result) => {
      if (result.isConfirmed) {
        // Quitar la X en anu_usu (usar null para almacenar NULL en la BD)
        usuario.anu_usu = null;
        this.userService.updateUser(usuario).subscribe(
          (response: any) => {
            Swal.fire('Activado', 'Usuario activado correctamente.', 'success');
            this.cargarUsuarios();
          },
          (error: any) => {
            console.error('Error al activar usuario:', error);
            Swal.fire('Error', 'No se pudo activar el usuario.', 'error');
          }
        );
      }
    });
  }
}
