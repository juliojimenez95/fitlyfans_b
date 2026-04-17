# Agent Skills for FitlyFans Backend

This file registers the local AI skills tailored specifically for the architecture and constraints of the FitlyFans project. 
The orchestrator should load these skills when performing architecture refactoring or when the triggers match.

| Skill Name | Description | Path |
|------------|-------------|------|
| `fitlyfans-repository` | Estándares de Arquitectura MVC (Controlador + Repositorio) en FitlyFans sin acoplamiento SQL. | [SKILL.md](skills/fitlyfans-repository/SKILL.md) |
| `fitlyfans-transactions` | Estándar de protección atómica (Transacciones, Commit y Rollback automático en MVC) para BD MySQL. | [SKILL.md](skills/fitlyfans-transactions/SKILL.md) |
