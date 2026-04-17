# FitlyFans Backend API

Backend del proyecto FitlyFans, una API RESTFul desarrollada en **Python** con **Flask** y conexión a base de datos **MySQL**. El proyecto sigue una arquitectura modular separando dominios por responsabilidades (Blueprint y MVC/Capas).

## Arquitectura y Módulos

El proyecto está diseñado bajo una arquitectura limpia y modularizada por dominio de negocio. Utilizamos `Blueprints` de Flask para separar las rutas de cada módulo.

- **Autenticación (`auth`)**: JWT (`PyJWT`) para manejo de sesiones y `bcrypt` para las contraseñas.
- **Suscriptores y Entrenadores (`suscriptor`, `entrenador`)**: Gestión de perfiles y roles.
- **Suscripciones y Pagos (`suscripcion`, `pagos`)**: Lógica de acceso e interacciones monetarias.
- **Gestión Física (`experiencias`, `ejercicios`, `rutina`)**: Manejo estructurado de entrenamientos.
- **Interacción (`contenido`, `comentario`, `mensajes`)**: Gestión de contenido multimedia, foro/comentarios y mensajería directa intra-plataforma.

---

## 📂 Estructura de Directorios

```text
FittlyFans/
├── app/
│   ├── __init__.py          # Entry point central, registro de Blueprints y CORS
│   ├── config.py            # Mapeo de variables de entorno y configs de app
│   ├── controllers/         # (Capa Controlador) Lógica de orquestación de negocio
│   ├── models/              # (Capa Modelo) Conexión a BD (DatabaseConnectionSingleton)
│   ├── routes/              # (Capa Presentación) Endpoints y Blueprints
│   ├── utils/               # Funciones compartidas, encriptación, validaciones
│   └── uploads/             # Almacenamiento local de archivos (videos, etc.)
├── docs_api/                # (Swagger) Documentación estática modular en YAML
├── tests/                   # Directorio de pruebas y testing de la API
├── .env                     # Variables de entorno locales (NO SUBIR A REPOSITORIO)
├── requirements.txt         # Dependencias de Python
└── run.py                   # Script de ejecución del servidor local
```

---

## 🛠 Requisitos Previos

- **Python 3.8+** (Actualmente usando 3.10 según cache)
- **MySQL 8.0+**
- **pip** (Manejador de paquetes)
- Entorno Virtual recomendado (e.g. `venv`)

---

## 🚀 Instalación y Despliegue Local

### 1. Clonar y preparar entorno
Asegúrate de estar en el nivel del repositorio:
```bash
git clone https://github.com/juliojimenez95/fitlyfans_b.git
cd fitlyfans_b/FittlyFans
```

Crea tu entorno virtual y actívalo:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Entorno
Crea un archivo `.env` en la raíz (junto a `run.py`) copiando el esquema base:

```env
# ========================
# CONFIGURACIÓN FLASK
# ========================
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=TU_SECRET_KEY_AQUI

# ========================
# CONFIGURACIÓN BASE DE DATOS
# ========================
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=fittlyfans
DB_USER=root
DB_PASSWORD=

# ========================
# JWT
# ========================
JWT_SECRET_KEY=TU_JWT_SECRET_KEY_AQUI
JWT_ACCESS_TOKEN_EXPIRES=3600
```
> **Tip:** Puedes generar llaves seguras ejecutando en python: `import secrets; print(secrets.token_hex(32))`

### 4. Inicializar servidor
Ejecuta la base de datos MySQL localmente asegurándote de haber creado la BD `fittlyfans` y luego levanta la API:

```bash
python run.py
```
> La API estará disponible en `http://127.0.0.1:5000`

---

## 📝 Patrones Usados (Obligatorios para escalar)

1. **Patrón Singleton**: Implementado en la capa de base de datos (`app/models/db.py` -> `DatabaseConnectionSingleton()`) para optimizar conexiones con MySQL y evitar sobrecarga en MySQL connector.
2. **MVC Adaptado**: Separación estricta de:
   - Rutinas (Routing) - `app/routes`
   - Lógica de Dominio (Controladores/Casos de uso) - `app/controllers`
   - Acceso a datos e infraestructura - `app/models`
3. **Early Returns (Bouncer Pattern)**: Preferido en los controladores para validación fluida de data y evitar *if* anidados.
4. **Documentación Modular (Separation of Concerns)**: Todas las rutas de Swagger flasgger están extraídas de los `controllers`/`routes` hacia el directorio autónomo `docs_api/` gestionado por el decorador `@swag_from`.

---

## 📖 Documentación Gráfica (Swagger)
El backend despliega una interfaz de documentación interactiva generada a través de `Flasgger`. 
- **Ruta de acceso:** `http://127.0.0.1:5000/apidocs/`
- Cuenta con autorización global inyectando el token JWT bajo la regla `Bearer <Token>` en el candado superior.
- Cada archivo de ruta cuenta con un `yml` asociado dentro del bloque `docs_api/` para probar interactivamente sin depender de Postman.

## ✨ Consideraciones Técnicas
- **Archivos Estáticos**: Este backend sube archivos localmente a `app/uploads`. Para un entorno productivo, se recomienda usar Storage en la nube (S3, Cloudinary).
- **Controladores y Try/Catch**: Toda capa de base de datos está atada a bloques try/catch/finally garantizando la desconexión del pool (observar `db.disconnect()` via context hook de Flask).

---
*Desarrollado con arquitectura escalable y separación de responsabilidades.*
