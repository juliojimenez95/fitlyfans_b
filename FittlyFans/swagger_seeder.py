import os
import re

ROUTES_DIR = "app/routes"
DOCS_DIR = "docs_api"
EXCLUDE = ["auth_routes.py", "entrenador_routes.py", "__init__.py"]

YAML_TEMPLATE = """tags:
  - {tag}
security:
  - Bearer: []
responses:
  200:
    description: Operación exitosa (Autogenerado)
  401:
    description: No autorizado
"""

for file_name in os.listdir(ROUTES_DIR):
    if file_name in EXCLUDE or not file_name.endswith("_routes.py"):
        continue

    module_name = file_name.replace("_routes.py", "")
    module_docs_dir = os.path.join(DOCS_DIR, module_name)
    os.makedirs(module_docs_dir, exist_ok=True)
    
    file_path = os.path.join(ROUTES_DIR, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    new_lines = []
    has_flasgger_import = any("from flasgger import swag_from" in line for line in lines)
    if not has_flasgger_import:
        new_lines.append("from flasgger import swag_from\n")

    for line in lines:
        new_lines.append(line)
        m = re.match(r"^def\s+([a-zA-Z0-9_]+)\(.*\):", line)
        if m:
            func_name = m.group(1)
            # Validar si es una ruta buscando hacia atras
            is_route = False
            for j in range(max(0, len(new_lines)-6), len(new_lines)):
                if ".route(" in new_lines[j]:
                    is_route = True
                    break
            
            if is_route:
                def_line = new_lines.pop()
                yaml_path = f"../../docs_api/{module_name}/{func_name}.yml"
                decorator = f"@swag_from('{yaml_path}')\n"
                
                if len(new_lines) > 0 and "swag_from" in new_lines[-1]:
                    new_lines.append(def_line)
                    continue
                
                new_lines.append(decorator)
                new_lines.append(def_line)
                
                tag_name = module_name.capitalize()
                yaml_content = YAML_TEMPLATE.format(tag=tag_name)
                y_path = os.path.join(module_docs_dir, f"{func_name}.yml")
                if not os.path.exists(y_path):
                    with open(y_path, "w", encoding="utf-8") as yf:
                        yf.write(yaml_content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
print(f"Seed para el modulo {file_name} inyectado!")
