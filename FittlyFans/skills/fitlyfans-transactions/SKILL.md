---
name: fitlyfans-transactions
description: >
  Patrón de Transacciones y Manejo de Errores para base de datos MySQL en FitlyFans.
  Trigger: Cuando el usuario pide hacer múltiples inserts, updates secuenciales o arreglar bugs de persistencia parcial en la base de datos de FitlyFans.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- Cuando vayas a programar lógicas de negocio que alteren más de 1 tabla a la vez.
- Cuando necesites garantizar atomicidad en procesos críticos (ej: pagos, suscripciones, eliminación en cascada).

## Critical Patterns

1. **PROHIBIDO EL COMMIT AUTOMÁTICO CIEGO**: No asumas que la bd hace autosave. Cualquier operación CRUD multi-paso debe orquestarse dentro de un bloque Transaccional del Controller.
2. **Uso de DatabaseConnectionSingleton**: Importa `DatabaseConnectionSingleton` de `app.models.db`.
3. **El Bloque Try/Except/Rollback (MANDATORIO)**: Todo proceso transaccional debe abrirse con `db.start_transaction()` antes del primer query, cerrarse con `db.commit()` al final, y obligatoriamente tener un `except Exception as e:` que invoque `db.rollback()` y relance el error `raise e`.

## Code Examples

### Transacción Segura
```python
from app.models.db import DatabaseConnectionSingleton
from app.repositories.user_repo import UserRepo

class MiController:
    def __init__(self):
        self.db = DatabaseConnectionSingleton()
        self.repo = UserRepo()

    def procesar_doble(self):
        try:
            self.db.start_transaction()
            
            self.repo.actualizar_paso1()
            self.repo.actualizar_paso2()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
```
