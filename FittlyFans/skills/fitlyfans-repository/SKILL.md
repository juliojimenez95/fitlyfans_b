---
name: fitlyfans-repository
description: >
  Estándar para crear y refactorizar Controladores y Repositorios en FitlyFans usando Arquitectura Limpia.
  Trigger: Cuando el usuario pide crear un nuevo endpoint, módulo, o refactorizar SQL quemado de un controlador en FitlyFans.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- Al crear nuevos módulos de negocio en FitlyFans.
- Al aislar queries de SQL que estén erróneamente dentro de `app/controllers`.
- Al inyectar base de datos en los servicios.

## Critical Patterns

1. **PROHIBIDO EL SQL EN CONTROLADORES**: Ningún controlador (`_controller.py`) debe tener strings con consultas SQL. TODO SQL debe residir exclusivamente en `app/repositories/`.
2. **Uso de BaseRepository**: Todo nuevo repositorio debe heredar de `BaseRepository` ubicado en `app/repositories/base_repository.py`.
3. **Inyección en Constructor**: Los controladores deben instanciar los repositorios en su método `__init__()`.
4. **Respuesta HTTP Predictiva**: Los controladores deben retornar diccionarios y booleanos; la envoltura a `jsonify()` con sus códigos de estado HTTP correctos (200, 201, 400, 404, 500) se hace en la capa de Rutas (`app/routes/`).

## Code Examples

### Repositorio Correcto (`ejemplo_repository.py`)
```python
from app.repositories.base_repository import BaseRepository

class EjemploRepository(BaseRepository):
    def crear_algo(self, nombre: str) -> int:
        query = "INSERT INTO Algo (nombre) VALUES (%s)"
        return self.execute_insert(query, (nombre,))
```

### Controlador Correcto (`ejemplo_controller.py`)
```python
from app.repositories.ejemplo_repository import EjemploRepository

class EjemploController:
    def __init__(self):
        self.ejemplo_repo = EjemploRepository()

    def procesar(self, nombre: str):
        return self.ejemplo_repo.crear_algo(nombre) > 0
```
