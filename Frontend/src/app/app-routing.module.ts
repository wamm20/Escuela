import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { WelcomeComponent } from './welcome/welcome.component';
import { UsuariosComponent } from './usuarios/usuarios.component';
import { AlumnosComponent } from './alumnos/alumnos.component';
import { ProfesoresComponent } from './profesores/profesores.component';
import { MateriasComponent } from './materias/materias.component';
import { CursosComponent } from './cursos/cursos.component';
import { CursosMateriasComponent } from './cursos-materias/cursos-materias.component';
import { ProgramasComponent } from './programas/programas.component';
import { InscripcionesComponent } from './inscripciones/inscripciones.component';
import { CalificacionesComponent } from './calificaciones/calificaciones.component';

const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'welcome', component: WelcomeComponent },
  { path: 'menu', component: HomeComponent },
  { path: 'inscripciones', component: InscripcionesComponent },
  { path: 'calificaciones', component: CalificacionesComponent },
  { path: 'usuarios', component: UsuariosComponent },
  { path: 'alumnos', component: AlumnosComponent },
  { path: 'profesores', component: ProfesoresComponent },
  { path: 'materias', component: MateriasComponent },
  { path: 'cursos', component: CursosComponent },
  { path: 'cursos-materias', component: CursosMateriasComponent },
  { path: 'programas', component: ProgramasComponent },
  { path: '**', redirectTo: '/login' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
