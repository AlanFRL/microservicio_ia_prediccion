# ⚡ INICIO RÁPIDO - Despliegue en Digital Ocean

**Tiempo total: ~1 hora**

---

## 📋 Pre-requisitos (5 min)

1. ✅ Cuenta de Docker Hub: https://hub.docker.com/signup
2. ✅ Cuenta de Digital Ocean: https://cloud.digitalocean.com/registrations/new
3. ✅ Docker Desktop instalado y corriendo
4. ✅ Git Bash o PowerShell

---

## 🚀 Pasos Rápidos

### 1. Docker Hub (2 min)

```powershell
# Login en Docker Hub
docker login
# Usuario: tu-usuario
# Password: tu-password
```

### 2. Build y Push (5 min)

```powershell
# Build imagen (reemplaza 'tuusuario' con tu usuario de Docker Hub)
docker build -t tuusuario/microservicio-ia-prediccion:v1.0 .

# Push a Docker Hub
docker push tuusuario/microservicio-ia-prediccion:v1.0
```

### 3. Crear Cluster en Digital Ocean (10 min)

1. Ve a: https://cloud.digitalocean.com/kubernetes/clusters/new
2. **Region:** New York 1
3. **Node Pool:** 2 GB RAM / 1 vCPU - 2 nodes
4. **Nombre:** microservicio-ia-cluster
5. Click **"Create Cluster"**
6. Espera 5 minutos
7. **Download Config File** → guarda como `k8s-config.yaml`

### 4. Configurar kubectl (2 min)

```powershell
# Copiar config
mkdir $HOME\.kube -Force
copy k8s-config.yaml $HOME\.kube\config

# Verificar
kubectl cluster-info
kubectl get nodes
```

### 5. Crear Secret (3 min)

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

# Verificar
kubectl get secrets
```

### 6. Actualizar Deployment (1 min)

Edita `k8s-deployment.yaml`, línea 23:

```yaml
# ANTES
image: tuusuario/microservicio-ia-prediccion:v1.0

# DESPUÉS (reemplaza con tu usuario)
image: alanfrl/microservicio-ia-prediccion:v1.0
```

### 7. Desplegar (5 min)

```powershell
# Aplicar deployment
kubectl apply -f k8s-deployment.yaml

# Ver pods (espera a que estén Running)
kubectl get pods -w

# Ver servicio (espera a que aparezca EXTERNAL-IP)
kubectl get services -w
```

### 8. Obtener EXTERNAL-IP (2 min)

```powershell
kubectl get services

# Salida:
# NAME                     TYPE           EXTERNAL-IP
# prediccion-ia-service    LoadBalancer   164.90.123.45
```

**Copia el EXTERNAL-IP** (ejemplo: `164.90.123.45`)

### 9. Probar (1 min)

```powershell
# Reemplaza con tu EXTERNAL-IP
curl http://164.90.123.45/health

# Debe retornar:
# {"status":"healthy","modelo_cargado":true,"mongodb_conectado":true,...}
```

### 10. Actualizar Spring Boot (1 min)

En `application.properties`:

```properties
ia.microservicio.url=http://164.90.123.45/predict
```

---

## ✅ Verificación

```powershell
# Ver logs
kubectl logs -f -l app=prediccion-ia

# Debe mostrar:
# ✅ Email Service - MODO REAL activado
# ✅ MongoDB conectado: agencia_viajes
# ✅ Microservicio listo
```

---

## 🎯 ¡Listo!

Tu microservicio está desplegado en producción.

**Siguiente:** Prueba desde Angular y verifica que los emails se envíen.

---

## 🚨 Problemas?

Ver guía completa: `DESPLIEGUE_DIGITAL_OCEAN.md`

---

## 📊 Comandos Útiles

```powershell
# Ver todo
kubectl get all

# Logs en tiempo real
kubectl logs -f -l app=prediccion-ia

# Reiniciar
kubectl rollout restart deployment/microservicio-ia-prediccion

# Escalar
kubectl scale deployment microservicio-ia-prediccion --replicas=4

# Eliminar todo
kubectl delete -f k8s-deployment.yaml
```

---

**Costo:** ~$36/mes (2 nodes + LoadBalancer)
