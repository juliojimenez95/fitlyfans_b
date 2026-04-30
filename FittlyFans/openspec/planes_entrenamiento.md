# Especificación: Planes de Entrenamiento y Asignación

## 1. Visión General
Esta especificación detalla el comportamiento del módulo de **Planes de Entrenamiento** en FitlyFans. El objetivo es permitir a los entrenadores agrupar `Rutinas` previamente creadas en un cronograma estructurado (Semanas y Días) y asignarlo de manera transaccional a sus suscriptores activos.

## 2. Entidades Principales (Dominio)
* **Plan_Entrenamiento**: Entidad que define la metadata del programa. Campos: `id`, `entrenador_id`, `nombre`, `descripcion`, `objetivo`, `nivel_dificultad`, `duracion_semanas`, `estado` (borrador/publicado).
* **Plan_Rutina**: Tabla pivote que modela la matriz del cronograma. Campos: `plan_id`, `rutina_id`, `semana`, `dia`.
* **Asignacion_Plan**: Entidad transaccional. Campos: `id`, `plan_id`, `suscriptor_id`, `entrenador_id`, `fecha_inicio`, `estado`.
* **Historial_Entrenamiento**: Entidad que registra la progresión de los suscriptores. Campos: `id`, `suscriptor_id`, `rutina_id`, `asignacion_plan_id`, `semana`, `dia`, `fecha_completada`, `duracion_segundos`. Todos los IDs foráneos DEBEN ser `BIGINT`.

## 3. Escenarios de Comportamiento (Gherkin)

### Escenario 1: Creación de un Plan por el Entrenador
* **Dado** que soy un entrenador autenticado
* **Cuando** ingreso al "Gestor de Planes" y completo el formulario básico
* **Y** arrastro o asigno rutinas de mi catálogo a los días específicos de cada semana en el "Constructor de Plan"
* **Entonces** el sistema persiste la estructura matriz en `Plan_Rutina` y marca el plan como listo para asignar.

### Escenario 2: Asignación Individual
* **Dado** que tengo planes creados
* **Cuando** ingreso al perfil de un "Suscriptor" en "Subscriber Management"
* **Y** presiono "Asignar Plan", elijo un plan y selecciono una fecha de inicio (ej. el próximo lunes)
* **Entonces** el sistema crea un registro en `Asignacion_Plan` y le notifica al suscriptor sobre su nuevo plan.

### Escenario 3: Motor de Entrenamiento Diario (Suscriptor)
* **Dado** que soy un suscriptor con un plan asignado
* **Cuando** ingreso a mi Feed y voy a la pestaña "Mi Plan" (`/mi-entrenamiento`)
* **Entonces** el sistema (Backend: `PlanController`) calcula los días transcurridos desde mi `fecha_inicio` hasta la `fecha_actual`.
* **Y** me devuelve la semana y día en los que me encuentro.
* **Y** si hoy tengo asignada una rutina, verifica en `Historial_Entrenamiento` si ya la completé hoy.
* **Y** visualizo mi plan. Si no está completada, veo "INICIAR ENTRENAMIENTO". Si ya está completada, veo el botón verde "REPETIR RUTINA COMPLETADA". Si no tengo rutina, veo "Día de Descanso".

### Escenario 4: Registro de Progreso
* **Dado** que el suscriptor está realizando una rutina desde "Mi Plan"
* **Cuando** el usuario marca como finalizado el último ejercicio de la rutina
* **Entonces** el Frontend (`ejecucion-rutina`) invoca la API pasándole `rutina_id`, `asignacion_plan_id`, `semana` y `dia`.
* **Y** el Backend (`ProgresoController`) verifica si ya existe un registro para esa asignación, semana y día.
* **Y** si no existe, inserta el progreso en `Historial_Entrenamiento` de manera inmutable. Si existe, retorna éxito silenciosamente sin crear registros duplicados.

## 4. Reglas de Negocio (Backend)
* `fecha_inicio` en la tabla `Asignacion_Plan` DEBE dictar todo el cronograma temporal. Las aplicaciones móviles u horarias del cliente no rigen, sino la matemática respecto al servidor.
* Una Asignación se considera `COMPLETADA` si `semana_actual > duracion_semanas`.
* Un día de un plan puede estar libre de rutinas (Día de descanso = `None`).
* Para evitar fallos estructurales (Error 3780 de MySQL), todas las llaves foráneas referentes a Rutinas o Usuarios DEBEN ser `BIGINT`.

## 5. Endpoints Principales
* `POST /api/planes`: Crear estructura de plan.
* `POST /api/planes/<id>/rutina`: Agregar rutina a semana/día.
* `POST /api/planes/<id>/asignar`: Asignar plan a un suscriptor.
* `GET /api/planes/mi-entrenamiento`: Endpoint dinámico para el suscriptor. Retorna `{ estado, asignacion, progreso, rutina_hoy (incluye boolean 'completado') }`.
* `POST /api/progreso/finalizar-rutina`: Registra que un usuario finalizó una rutina, vinculándola opcionalmente a un plan.
