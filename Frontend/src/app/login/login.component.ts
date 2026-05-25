import { Component, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit, OnDestroy {
  username = '';
  password = '';
  error = '';
  loading = false;
  showPassword = false;

  // avioncitos animados
  planes: Array<{top: number; left: number; rotation: number}> = [];
  private planeInterval: any;
  private readonly planeCount = 40;  // número de aviones (aún más tráfico aéreo)

  constructor(private auth: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.initPlanes();
    // lanzar primer desplazamiento para que no estén estáticos
    this.movePlanes();
    // comenzar ciclo de movimiento repetido
    this.planeInterval = setInterval(() => this.movePlanes(), 3500); // un poco más frecuentes
  }

  ngOnDestroy(): void {
    if (this.planeInterval) {
      clearInterval(this.planeInterval);
    }
  }

  get formInvalid(): boolean {
    return !(this.username && this.password);
  }

  private readonly icons = ['✈️','🛩️','✈️','🛩️','✈️'];

  private initPlanes(): void {
    this.planes = [];
    for (let i = 0; i < this.planeCount; i++) {
      // generar algunas aviones directamente en los bordes
      let top = this.randEdge();
      let left = this.randEdge();
      // si ambos son bordes, dejar como está; de lo contrario mezclar con coordenada aleatoria
      if (Math.random() < 0.5) {
        top = Math.random() * 120 - 10;
      }
      if (Math.random() < 0.5) {
        left = Math.random() * 120 - 10;
      }
      this.planes.push({
        top,
        left,
        rotation: 0,
        icon: this.icons[Math.floor(Math.random() * this.icons.length)],
      } as any);
    }
  }

  private randEdge(): number {
    // devuelve -10 o 110 con igual probabilidad
    return Math.random() < 0.5 ? -10 : 110;
  }

  private movePlanes(): void {
    this.planes = this.planes.map(p => {
      const newTop = Math.random() < 0.25 ? this.randEdge() : Math.random() * 120 - 10;
      const newLeft = Math.random() < 0.25 ? this.randEdge() : Math.random() * 120 - 10;
      const dy = newTop - p.top;
      const dx = newLeft - p.left;
      const angle = Math.atan2(dy, dx) * (180 / Math.PI);
      return {
        ...p,
        top: newTop,
        left: newLeft,
        rotation: angle,
      };
    });
  }

    submit() {
    this.error = '';
    if (this.formInvalid) {
      this.error = 'Por favor completa usuario y contraseña.';
      return;
    }
    this.loading = true;
    this.auth.login(this.username, this.password).subscribe({
      next: (res: any) => {
        if (res && res.access_token) {
          this.auth.setToken(res.access_token);
          // Navegar a la pantalla de bienvenida
          this.router.navigate(['/welcome']);
        } else {
          // Este caso es poco probable si el backend siempre devuelve error en fallo
          this.error = 'Respuesta inesperada del servidor.';
          this.loading = false;
        }
      },
      error: (err: any) => {
        // --- INICIO DE LA CORRECCIÓN ---
        // Ahora leemos el mensaje de error específico que envía el backend.
        if (err.error && err.error.message) {
          this.error = err.error.message;
        } else {
          // Fallback por si el error no tiene el formato esperado (ej. error de red)
          this.error = 'Usuario o Clave errada';
        }
        this.loading = false;
        // --- FIN DE LA CORRECCIÓN ---
      },
    });
  }

  toggleShowPassword() {
    this.showPassword = !this.showPassword;
  }
}
