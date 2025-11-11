# 🚀 Guía Completa: Desplegar en Digital Ocean Kubernetes

**Fecha:** 11 de Noviembre, 2025  
**Objetivo:** Desplegar el microservicio de IA en Digital Ocean con Kubernetes

---

## 📋 PARTE 1: Preparación Previa (15 min)

### ✅ Requisitos:
- [ ] Cuenta de Digital Ocean (puedes usar $200 crédito gratis con GitHub Student Pack)
- [ ] Cuenta de Docker Hub (gratis)
- [ ] Git instalado
- [ ] Docker Desktop instalado y corriendo

---

## 🐳 PARTE 2: Crear Docker Image (10 min)

### Paso 1: Crear Dockerfile

Crea el archivo `Dockerfile` en la raíz del proyecto:

```dockerfile
# Usar Python 3.11 slim
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . .

# Exponer puerto
EXPOSE 8001

# Comando para iniciar
CMD ["python", "main_v4.py"]
```

### Paso 2: Crear .dockerignore

Crea el archivo `.dockerignore`:

```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.env
.git
.gitignore
*.md
.vscode/
.idea/
*.log
```

### Paso 3: Build de la imagen

```powershell
# Build de la imagen
docker build -t microservicio-ia-prediccion:v1.0 .

# Verificar que se creó
docker images | grep microservicio
```

### Paso 4: Probar localmente (Opcional)

```powershell
# Probar la imagen localmente
docker run -p 8001:8001 `
  -e MONGODB_URI="mongodb+srv://agencia_user:uagrm2025@agencia-database.8n7ayzu.mongodb.net/?appName=agencia-database" `
  -e MONGODB_DATABASE="agencia_viajes" `
  -e UMBRAL_RIESGO="0.70" `
  -e EMAIL_MODE="real" `
  -e SMTP_HOST="smtp.gmail.com" `
  -e SMTP_PORT="587" `
  -e SMTP_USER="alanfromerol@gmail.com" `
  -e SMTP_PASSWORD="tu-app-password" `
  microservicio-ia-prediccion:v1.0

# Probar: curl http://localhost:8001/health
# Ctrl+C para detener
```

---

## 🌐 PARTE 3: Subir a Docker Hub (5 min)

### Paso 1: Login en Docker Hub

```powershell
# Login
docker login

# Ingresa tu usuario y contraseña de Docker Hub
```

### Paso 2: Tag y Push

```powershell
# Reemplaza 'tuusuario' con tu usuario de Docker Hub
docker tag microservicio-ia-prediccion:v1.0 tuusuario/microservicio-ia-prediccion:v1.0

# Push al registry
docker push tuusuario/microservicio-ia-prediccion:v1.0
```

**Ejemplo:**
```powershell
docker tag microservicio-ia-prediccion:v1.0 alanfrl/microservicio-ia-prediccion:v1.0
docker push alanfrl/microservicio-ia-prediccion:v1.0
```

---

## ☸️ PARTE 4: Crear Cluster en Digital Ocean (10 min)

### Paso 1: Acceder a Digital Ocean

1. Ve a: https://cloud.digitalocean.com/
2. Login con tu cuenta
3. Si no tienes cuenta, créala (puedes obtener $200 gratis con GitHub Student Pack)

### Paso 2: Crear Kubernetes Cluster

1. En el menú lateral, click en **"Kubernetes"**
2. Click en **"Create a Kubernetes cluster"**
3. Configura:

   **Región:**
   - Selecciona la más cercana (ejemplo: `New York 1` o `San Francisco 3`)

   **Versión:**
   - Usa la versión más reciente de Kubernetes (ejemplo: `1.28.x`)

   **Node Pool:**
   - **Machine Type:** `Basic nodes`
   - **Node Plan:** `2 GB RAM / 1 vCPU` ($12/mes)
   - **Node Count:** `2` (para alta disponibilidad)

   **Nombre:**
   - `microservicio-ia-cluster`

4. Click en **"Create Cluster"**

**Tiempo de creación:** ~5 minutos

### Paso 3: Descargar kubeconfig

Una vez creado el cluster:

1. Click en tu cluster (`microservicio-ia-cluster`)
2. Click en **"Download Config File"**
3. Guarda el archivo como: `k8s-config.yaml`

### Paso 4: Configurar kubectl

```powershell
# Crear directorio .kube si no existe
mkdir $HOME\.kube -Force

# Copiar el config
copy k8s-config.yaml $HOME\.kube\config

# Verificar conexión
kubectl cluster-info

# Ver nodos
kubectl get nodes
```

**Salida esperada:**
```
NAME                  STATUS   ROLES    AGE   VERSION
node-1                Ready    <none>   5m    v1.28.x
node-2                Ready    <none>   5m    v1.28.x
```

---

## 🔐 PARTE 5: Crear Secrets en Kubernetes (5 min)

### Crear el Secret con todas las credenciales:

```powershell
kubectl create secret generic fastapi-secrets `
  --from-literal=MONGODB_URI="mongodb+srv://agencia_user:uagrm2025@agencia-database.8n7ayzu.mongodb.net/?appName=agencia-database" `
  --from-literal=MONGODB_DATABASE="agencia_viajes" `
  --from-literal=UMBRAL_RIESGO="0.70" `
  --from-literal=EMAIL_MODE="real" `
  --from-literal=SMTP_HOST="smtp.gmail.com" `
  --from-literal=SMTP_PORT="587" `
  --from-literal=SMTP_USER="alanfromerol@gmail.com" `
  --from-literal=SMTP_PASSWORD="xzbg jgqx acyo ocws"
```

**Verificar:**
```powershell
# Ver el secret creado
kubectl get secrets

# Ver detalles (NO muestra valores)
kubectl describe secret fastapi-secrets
```

---

## 📦 PARTE 6: Crear Deployment (5 min)

### Crear archivo `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: microservicio-ia-prediccion
  labels:
    app: prediccion-ia
spec:
  replicas: 2
  selector:
    matchLabels:
      app: prediccion-ia
  template:
    metadata:
      labels:
        app: prediccion-ia
    spec:
      containers:
      - name: fastapi
        image: tuusuario/microservicio-ia-prediccion:v1.0
        ports:
        - containerPort: 8001
          name: http
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: MONGODB_URI
        - name: MONGODB_DATABASE
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: MONGODB_DATABASE
        - name: UMBRAL_RIESGO
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: UMBRAL_RIESGO
        - name: EMAIL_MODE
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: EMAIL_MODE
        - name: SMTP_HOST
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: SMTP_HOST
        - name: SMTP_PORT
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: SMTP_PORT
        - name: SMTP_USER
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: SMTP_USER
        - name: SMTP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: SMTP_PASSWORD
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: prediccion-ia-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8001
    protocol: TCP
    name: http
  selector:
    app: prediccion-ia
```

**IMPORTANTE:** Reemplaza `tuusuario` con tu usuario de Docker Hub.

### Aplicar el Deployment:

```powershell
kubectl apply -f k8s-deployment.yaml
```

---

## 🔍 PARTE 7: Verificar el Despliegue (5 min)

### Ver los Pods:

```powershell
# Listar pods
kubectl get pods

# Ver logs de un pod
kubectl logs -f <nombre-del-pod>
```

**Busca en los logs:**
```
✅ Email Service - MODO REAL activado (alanfromerol@gmail.com)
✅ MongoDB conectado: agencia_viajes
✅ Microservicio listo
```

### Ver el Service:

```powershell
kubectl get services
```

**Salida esperada:**
```
NAME                     TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)
prediccion-ia-service    LoadBalancer   10.245.x.x      164.90.x.x       80:xxxxx/TCP
```

**Copia la `EXTERNAL-IP`** (ejemplo: `164.90.123.45`)

### Probar el Servicio:

```powershell
# Health check (reemplaza con tu EXTERNAL-IP)
curl http://164.90.123.45/health

# Ver estadísticas
curl http://164.90.123.45/recordatorios/estadisticas
```

---

## 🔗 PARTE 8: Configurar Spring Boot (2 min)

En tu proyecto Spring Boot, actualiza `application.properties`:

```properties
# Antes (local)
# ia.microservicio.url=http://localhost:8001/predict

# Después (producción)
ia.microservicio.url=http://164.90.123.45/predict
```

**Reemplaza `164.90.123.45`** con tu EXTERNAL-IP real.

---

## 📊 PARTE 9: Monitoreo en Producción

### Ver logs en tiempo real:

```powershell
# Todos los pods
kubectl logs -f -l app=prediccion-ia

# Filtrar solo emails
kubectl logs -f -l app=prediccion-ia | Select-String "Email"
```

### Ver eventos:

```powershell
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Ver recursos:

```powershell
kubectl top pods
```

### Ver todos los recursos:

```powershell
kubectl get all
```

---

## 🔄 PARTE 10: Actualizar la Aplicación

### Cuando hagas cambios en el código:

```powershell
# 1. Build nueva versión
docker build -t tuusuario/microservicio-ia-prediccion:v1.1 .

# 2. Push al registry
docker push tuusuario/microservicio-ia-prediccion:v1.1

# 3. Actualizar en K8s
kubectl set image deployment/microservicio-ia-prediccion `
  fastapi=tuusuario/microservicio-ia-prediccion:v1.1

# 4. Ver el progreso
kubectl rollout status deployment/microservicio-ia-prediccion
```

---

## 🚨 PARTE 11: Troubleshooting

### Problema: Pods no inician

```powershell
# Ver detalles
kubectl describe pod <nombre-del-pod>

# Ver logs de error
kubectl logs <nombre-del-pod>
```

### Problema: LoadBalancer sin EXTERNAL-IP

```powershell
# Espera 2-3 minutos, luego:
kubectl get services -w

# Si sigue sin IP, verifica:
kubectl describe service prediccion-ia-service
```

### Problema: Error de autenticación SMTP

```powershell
# Verificar el secret
kubectl get secret fastapi-secrets -o yaml

# Actualizar el secret
kubectl delete secret fastapi-secrets
kubectl create secret generic fastapi-secrets --from-literal=SMTP_PASSWORD="nueva-password"

# Reiniciar pods
kubectl rollout restart deployment/microservicio-ia-prediccion
```

### Problema: MongoDB no conecta

```powershell
# Verificar que MongoDB Atlas permite IPs de DO
# En MongoDB Atlas > Network Access > Add IP Address
# Agrega: 0.0.0.0/0 (permite todas las IPs)
```

---

## 🔐 PARTE 12: Seguridad en Producción

### ✅ Mejores Prácticas:

1. **Network Policies:** Limita el tráfico entre pods
2. **Resource Limits:** Ya están configurados (256Mi-512Mi RAM)
3. **Health Checks:** Ya están configurados (liveness + readiness)
4. **Secrets:** NUNCA hardcodees credenciales en el código
5. **RBAC:** Limita permisos de acceso al cluster

### Opcional: Configurar dominio personalizado

```powershell
# Agregar DNS record en tu proveedor:
# Type: A
# Name: ia-prediccion
# Value: <EXTERNAL-IP>

# Actualizar Spring Boot:
# ia.microservicio.url=https://ia-prediccion.tudominio.com/predict
```

---

## 📈 PARTE 13: Escalado

### Escalar manualmente:

```powershell
# Aumentar a 4 pods
kubectl scale deployment microservicio-ia-prediccion --replicas=4

# Verificar
kubectl get pods
```

### Auto-escalado (HPA):

Crea `k8s-hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: prediccion-ia-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: microservicio-ia-prediccion
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

```powershell
kubectl apply -f k8s-hpa.yaml
```

---

## 💰 PARTE 14: Costos Aproximados

### Digital Ocean Kubernetes:

- **2 Nodes (2GB RAM / 1 vCPU):** $24/mes
- **LoadBalancer:** $12/mes
- **Total:** ~$36/mes

### Alternativas más económicas:

- **1 Node (2GB RAM):** $12/mes (sin alta disponibilidad)
- **Usar NodePort en lugar de LoadBalancer:** $12/mes (solo 1 node)

---

## ✅ CHECKLIST COMPLETO

### Pre-despliegue:
- [ ] Docker Desktop instalado y corriendo
- [ ] Cuenta de Docker Hub creada
- [ ] Cuenta de Digital Ocean creada
- [ ] `Dockerfile` creado
- [ ] `.dockerignore` creado

### Docker:
- [ ] Imagen construida localmente
- [ ] Imagen probada localmente (opcional)
- [ ] Login en Docker Hub exitoso
- [ ] Imagen pusheada a Docker Hub

### Kubernetes:
- [ ] Cluster creado en Digital Ocean
- [ ] `kubectl` configurado
- [ ] Secret `fastapi-secrets` creado
- [ ] `k8s-deployment.yaml` creado
- [ ] Deployment aplicado

### Verificación:
- [ ] Pods en estado `Running`
- [ ] Service con `EXTERNAL-IP` asignada
- [ ] Health check respondiendo
- [ ] MongoDB conectado (ver logs)
- [ ] Email service en modo REAL (ver logs)

### Integración:
- [ ] Spring Boot actualizado con nueva URL
- [ ] Prueba de predicción exitosa
- [ ] Email enviado correctamente
- [ ] Estadísticas funcionando

---

## 🎯 Comandos Rápidos de Referencia

```powershell
# Ver todo
kubectl get all

# Logs en tiempo real
kubectl logs -f -l app=prediccion-ia --all-containers=true

# Reiniciar deployment
kubectl rollout restart deployment/microservicio-ia-prediccion

# Ver recursos
kubectl top pods

# Entrar a un pod (debugging)
kubectl exec -it <pod-name> -- /bin/sh

# Eliminar todo (si necesitas empezar de nuevo)
kubectl delete -f k8s-deployment.yaml
kubectl delete secret fastapi-secrets
```

---

## 📞 Próximos Pasos

1. ✅ **Sigue esta guía paso a paso**
2. ✅ **Copia el EXTERNAL-IP y actualiza Spring Boot**
3. ✅ **Prueba desde Angular**
4. ✅ **Monitorea los logs**
5. ✅ **Celebra tu despliegue exitoso 🎉**

---

*Guía creada: 11 de Noviembre, 2025*  
*Plataforma: Digital Ocean Kubernetes*  
*Estado: ✅ LISTA PARA SEGUIR*  
*Tiempo estimado total: ~1 hora*
