# Arquitectura de Feed y Contenido

Este documento define la estructura y reglas de negocio para la gestión de contenido social en FitlyFans, separándolo estrictamente del modelo de entrenamiento estructurado (Rutinas y Ejercicios).

## 1. Contexto de Entidades

*   **Entidades de Entrenamiento (Core Business)**:
    *   `Rutina` y `Ejercicio`.
    *   Gestionadas desde el "Gestor de Rutinas" y "Gestor de Ejercicios".
    *   NO son "posts" genéricos. Se asignan a los suscriptores a través del "Plan de Entrenamiento".
*   **Entidades Sociales (Engagement)**:
    *   `Contenido`: Son las publicaciones (posts) que los entrenadores hacen para interactuar con su comunidad (fotos, videos motivacionales, tips informales).
    *   **Campo `tipo`**: En la tabla `Contenido`, el campo `tipo` (`ENUM('video', 'imagen', 'texto')`) representa **exclusivamente el formato multimedia** del archivo subido. No existen categorías de negocio adicionales (ej. "Tip", "Publicación") porque introducían ambigüedad. El backend infiere el formato automáticamente.

## 2. Flujos de Visualización (Feed)

El perfil del suscriptor cuenta con dos pestañas principales para el consumo de este contenido social:

### 2.1 El "Muro" (Premium Feed)
*   **Propósito**: Mostrar el contenido exclusivo de los entrenadores a los que el suscriptor ha decidido seguir o suscribirse.
*   **Ruta API**: `GET /api/contenido/feed`
*   **Lógica de Base de Datos**: Realiza un `JOIN` con la tabla `Suscripcion`. Solo retorna registros donde `s.id_seguidor` coincide con el usuario en sesión.
*   **Comportamiento**: Actúa como un espacio privado, libre de ruido, ordenado cronológicamente.

### 2.2 El "Descubrir" (Global Feed)
*   **Propósito**: Actuar como una vitrina pública para el descubrimiento orgánico de nuevos entrenadores dentro de la plataforma.
*   **Ruta API**: `GET /api/contenido/descubrir`
*   **Lógica de Base de Datos**: Retorna las publicaciones globales más recientes, **excluyendo** a los entrenadores a los que el usuario ya está suscrito. 
    *   *Nota Arquitectónica*: Anteriormente, esta pestaña intentaba filtrar por `tipo='publicacion'`, lo cual entraba en conflicto directo con el `ENUM` de formatos multimedia de la base de datos y devolvía resultados vacíos.
*   **Comportamiento**: Un feed infinito estilo "Explorar" para fomentar nuevas suscripciones.
