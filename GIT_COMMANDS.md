# 📝 Guía de Git - Comandos Útiles

Esta guía contiene los comandos más comunes para trabajar con este repositorio.

---

## 🔄 Flujo de Trabajo Básico

### 1. Ver estado actual
```bash
git status
```

### 2. Ver qué archivos cambiaron
```bash
git diff
```

### 3. Agregar archivos modificados
```bash
# Agregar un archivo específico
git add archivo.py

# Agregar todos los cambios
git add .

# Agregar solo archivos .py
git add *.py
```

### 4. Hacer commit
```bash
git commit -m "Descripción clara del cambio"
```

### 5. Subir cambios a GitHub
```bash
git push origin main
```

---

## 📥 Obtener Cambios del Repositorio

### Ver cambios remotos sin descargar
```bash
git fetch
```

### Descargar y fusionar cambios
```bash
git pull origin main
```

---

## 🔍 Ver Historial

### Ver commits recientes
```bash
# Últimos 10 commits
git log --oneline -n 10

# Log detallado
git log

# Log con gráfico de ramas
git log --oneline --graph --all
```

### Ver cambios de un commit específico
```bash
git show <commit-id>
```

---

## 🌿 Trabajo con Ramas

### Ver ramas
```bash
# Ramas locales
git branch

# Todas las ramas (local + remoto)
git branch -a
```

### Crear nueva rama
```bash
# Crear y cambiar a la nueva rama
git checkout -b feature/nueva-funcionalidad

# O en dos pasos
git branch feature/nueva-funcionalidad
git checkout feature/nueva-funcionalidad
```

### Cambiar de rama
```bash
git checkout main
git checkout feature/otra-rama
```

### Fusionar rama
```bash
# Estar en la rama destino (main)
git checkout main

# Fusionar la rama feature
git merge feature/nueva-funcionalidad
```

### Eliminar rama
```bash
# Local
git branch -d feature/rama-completada

# Remoto
git push origin --delete feature/rama-completada
```

---

## ↩️ Deshacer Cambios

### Descartar cambios en un archivo (NO commiteado)
```bash
git checkout -- archivo.py
```

### Descartar TODOS los cambios (NO commiteados)
```bash
git reset --hard
```

### Deshacer último commit (mantener cambios)
```bash
git reset --soft HEAD~1
```

### Deshacer último commit (eliminar cambios)
```bash
git reset --hard HEAD~1
```

### Revertir un commit específico
```bash
git revert <commit-id>
```

---

## 🏷️ Tags (Versiones)

### Crear tag
```bash
git tag v1.0.0
git tag -a v1.0.0 -m "Versión 1.0.0 - Primera versión estable"
```

### Ver tags
```bash
git tag
```

### Subir tags a GitHub
```bash
# Un tag específico
git push origin v1.0.0

# Todos los tags
git push origin --tags
```

---

## 🔒 Seguridad

### Verificar que .env NO esté en el repo
```bash
git ls-files | Select-String -Pattern "\.env"
# Solo debe aparecer: .env.example
```

### Si accidentalmente agregaste .env
```bash
# Removerlo del staging
git reset .env

# Removerlo del repositorio pero mantenerlo local
git rm --cached .env

# Agregar a .gitignore si no está
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Agregar .env al gitignore"
```

---

## 🔄 Actualizar desde GitHub (Colaboración)

Cuando trabajes en equipo:

```bash
# 1. Antes de empezar a trabajar
git pull origin main

# 2. Hacer tus cambios
# ... editar archivos ...

# 3. Ver qué cambió
git status
git diff

# 4. Agregar y commitear
git add .
git commit -m "Descripción de cambios"

# 5. Actualizar por si hay nuevos cambios
git pull origin main

# 6. Resolver conflictos si los hay
# ... editar archivos con conflictos ...
git add .
git commit -m "Resolver conflictos"

# 7. Subir
git push origin main
```

---

## 🛠️ Comandos Útiles

### Ver configuración de Git
```bash
git config --list
```

### Configurar usuario (si no lo has hecho)
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

### Ver repositorio remoto
```bash
git remote -v
```

### Cambiar URL del repositorio remoto
```bash
git remote set-url origin https://github.com/nuevo-usuario/nuevo-repo.git
```

### Clonar este repositorio en otra máquina
```bash
git clone https://github.com/AlanFRL/microservicio_ia_prediccion.git
cd microservicio_ia_prediccion
```

---

## 📋 .gitignore

El archivo `.gitignore` ya está configurado para ignorar:

```
# Entornos virtuales
venv/
.venv/
env/

# Credenciales
.env

# Cache
__pycache__/
*.pyc

# IDEs
.vscode/
.idea/

# Logs
*.log

# Sistema
.DS_Store
Thumbs.db
```

Para agregar más patrones:
```bash
echo "nuevo_archivo_a_ignorar.txt" >> .gitignore
git add .gitignore
git commit -m "Actualizar .gitignore"
```

---

## 🚨 Problemas Comunes

### Error: "fatal: remote origin already exists"
```bash
git remote rm origin
git remote add origin https://github.com/AlanFRL/microservicio_ia_prediccion.git
```

### Error: "Your local changes would be overwritten"
```bash
# Guardar cambios temporalmente
git stash

# Actualizar
git pull origin main

# Recuperar cambios
git stash pop
```

### Error: Conflictos al hacer merge
```bash
# 1. Git marca los conflictos en los archivos
# 2. Editar manualmente los archivos con conflictos
# 3. Buscar las marcas: <<<<<<< HEAD y >>>>>>> rama
# 4. Resolver manualmente el conflicto
# 5. Agregar y commitear
git add archivo_con_conflicto.py
git commit -m "Resolver conflicto en archivo_con_conflicto.py"
```

---

## 📦 Subir Nuevo Archivo

```bash
# 1. Crear el archivo
# 2. Verificar que no esté en .gitignore
# 3. Agregar
git add nuevo_archivo.py

# 4. Commit
git commit -m "Agregar nuevo_archivo.py"

# 5. Push
git push origin main
```

---

## 🗑️ Eliminar Archivo del Repositorio

```bash
# Eliminar del repo y del disco
git rm archivo_viejo.py
git commit -m "Eliminar archivo_viejo.py"
git push origin main

# Eliminar solo del repo (mantener en disco)
git rm --cached archivo_local.py
git commit -m "Eliminar archivo_local.py del repositorio"
git push origin main
```

---

## 🔄 Workflow Recomendado

### Para cambios pequeños (hotfix):
```bash
git pull origin main
# ... hacer cambios ...
git add .
git commit -m "Fix: descripción del fix"
git push origin main
```

### Para nuevas features:
```bash
# Crear rama
git checkout -b feature/nueva-funcionalidad

# Hacer cambios
# ... trabajar en la feature ...

# Commit
git add .
git commit -m "Implementar nueva-funcionalidad"

# Actualizar main y fusionar
git checkout main
git pull origin main
git merge feature/nueva-funcionalidad

# Subir
git push origin main

# Eliminar rama local
git branch -d feature/nueva-funcionalidad
```

---

## 🔗 Enlaces Útiles

- **Repositorio:** https://github.com/AlanFRL/microservicio_ia_prediccion
- **Documentación Git:** https://git-scm.com/doc
- **GitHub Docs:** https://docs.github.com/

---

## 💡 Tips

1. **Commits frecuentes:** Haz commits pequeños y frecuentes
2. **Mensajes claros:** Usa mensajes descriptivos
3. **Pull antes de Push:** Siempre actualiza antes de subir
4. **Ramas para features:** Usa ramas para cambios grandes
5. **No subas .env:** Nunca subas credenciales

---

*Última actualización: 11 de Noviembre, 2025*
