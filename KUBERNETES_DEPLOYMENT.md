# ☸️ Despliegue en Kubernetes (Digital Ocean)

Este documento explica cómo desplegar el microservicio en **Kubernetes** con **Digital Ocean** usando **Secrets** para las credenciales.

---

## 📋 Prerequisitos

1. ✅ Cluster de Kubernetes en Digital Ocean
2. ✅ `kubectl` configurado y conectado al cluster
3. ✅ Docker image del microservicio publicada en un registry
4. ✅ App Password de Gmail generado

---

## 🔐 Paso 1: Crear Kubernetes Secret

Los **Secrets** son la forma segura de manejar credenciales en Kubernetes.

```bash
# Crear el secret con todas las variables de entorno
kubectl create secret generic fastapi-secrets \
  --from-literal=MONGODB_URI="mongodb+srv://agencia_user:uagrm2025@agencia-database.8n7ayzu.mongodb.net/?appName=agencia-database" \
  --from-literal=MONGODB_DATABASE="agencia_viajes" \
  --from-literal=UMBRAL_RIESGO="0.70" \
  --from-literal=EMAIL_MODE="real" \
  --from-literal=SMTP_HOST="smtp.gmail.com" \
  --from-literal=SMTP_PORT="587" \
  --from-literal=SMTP_USER="alanfromerol@gmail.com" \
  --from-literal=SMTP_PASSWORD="TU_APP_PASSWORD_AQUI"
```

**IMPORTANTE:** Reemplaza `TU_APP_PASSWORD_AQUI` con tu App Password real de Gmail.

### Verificar el Secret:

```bash
# Listar secrets
kubectl get secrets

# Ver detalles (NO muestra los valores)
kubectl describe secret fastapi-secrets
```

---

## 📦 Paso 2: Crear Deployment

Crea un archivo `kubernetes-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: microservicio-ia-prediccion
  labels:
    app: prediccion-ia
spec:
  replicas: 2  # 2 pods para alta disponibilidad
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
        image: tu-registry/microservicio-ia-prediccion:latest
        ports:
        - containerPort: 8001
          name: http
        env:
        # Cargar TODAS las variables desde el Secret
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
        # Health checks
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
          initialDelaySeconds: 5
          periodSeconds: 5
        # Recursos
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
# Service (LoadBalancer para acceso externo)
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
  selector:
    app: prediccion-ia
```

### Aplicar el Deployment:

```bash
kubectl apply -f kubernetes-deployment.yaml
```

---

## 🔍 Paso 3: Verificar el Despliegue

### Ver los pods:

```bash
# Listar pods
kubectl get pods

# Ver logs de un pod
kubectl logs -f <nombre-del-pod>

# Buscar el mensaje de confirmación:
# ✅ Email Service - MODO REAL activado (alanfromerol@gmail.com)
```

### Ver el servicio:

```bash
# Obtener la IP externa (LoadBalancer)
kubectl get services

# Salida esperada:
# NAME                     TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)
# prediccion-ia-service    LoadBalancer   10.245.x.x      164.90.x.x       80:xxxxx/TCP
```

### Probar el servicio:

```bash
# Health check
curl http://<EXTERNAL-IP>/health

# Ver estadísticas
curl http://<EXTERNAL-IP>/recordatorios/estadisticas
```

---

## 🔄 Paso 4: Actualizar el Secret (Si es necesario)

Si necesitas cambiar el App Password u otra credencial:

```bash
# Opción 1: Eliminar y recrear
kubectl delete secret fastapi-secrets
kubectl create secret generic fastapi-secrets \
  --from-literal=EMAIL_MODE="real" \
  --from-literal=SMTP_PASSWORD="NUEVO_APP_PASSWORD"
  # ... resto de variables

# Opción 2: Editar directamente (más complejo)
kubectl edit secret fastapi-secrets
```

**Después de actualizar el secret, reinicia los pods:**

```bash
kubectl rollout restart deployment/microservicio-ia-prediccion
```

---

## 📊 Monitoreo en Producción

### Ver logs en tiempo real:

```bash
# Logs de todos los pods
kubectl logs -f -l app=prediccion-ia

# Filtrar solo emails enviados
kubectl logs -f -l app=prediccion-ia | grep "Email enviado"
```

### Ver eventos:

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Ver recursos:

```bash
kubectl top pods
```

---

## 🚨 Troubleshooting

### Problema: Pods no inician

```bash
# Ver detalles del pod
kubectl describe pod <nombre-del-pod>

# Ver logs de error
kubectl logs <nombre-del-pod>
```

### Problema: Secret no se carga

```bash
# Verificar que existe
kubectl get secret fastapi-secrets

# Ver las keys (NO los valores)
kubectl describe secret fastapi-secrets

# Verificar en el pod
kubectl exec -it <nombre-del-pod> -- env | grep SMTP
```

### Problema: Email no se envía

1. Verifica los logs:
   ```bash
   kubectl logs -f <nombre-del-pod> | grep "Email"
   ```

2. Verifica el modo:
   ```bash
   kubectl exec -it <nombre-del-pod> -- env | grep EMAIL_MODE
   # Debe mostrar: EMAIL_MODE=real
   ```

3. Verifica las credenciales SMTP:
   ```bash
   kubectl exec -it <nombre-del-pod> -- env | grep SMTP
   ```

---

## 🔒 Seguridad en Producción

### ✅ Buenas Prácticas:

1. **NUNCA** hardcodees credenciales en el código
2. **SIEMPRE** usa Kubernetes Secrets
3. **Limita** el acceso al Secret:
   ```bash
   kubectl create rolebinding secret-reader \
     --clusterrole=view \
     --serviceaccount=default:default \
     --namespace=default
   ```

4. **Encripta** los Secrets en reposo (Digital Ocean lo hace por defecto)

5. **Rotación** de credenciales:
   - Cambia el App Password cada 3-6 meses
   - Actualiza el Secret en Kubernetes
   - Reinicia los pods

---

## 🔄 Actualizar la Aplicación

### Construir nueva imagen:

```bash
# Build
docker build -t tu-registry/microservicio-ia-prediccion:v1.1 .

# Push al registry
docker push tu-registry/microservicio-ia-prediccion:v1.1
```

### Actualizar el deployment:

```bash
# Opción 1: Editar el YAML y aplicar
kubectl apply -f kubernetes-deployment.yaml

# Opción 2: Actualizar la imagen directamente
kubectl set image deployment/microservicio-ia-prediccion \
  fastapi=tu-registry/microservicio-ia-prediccion:v1.1

# Ver el progreso
kubectl rollout status deployment/microservicio-ia-prediccion
```

---

## 📈 Escalado

### Escalar manualmente:

```bash
# Aumentar a 5 pods
kubectl scale deployment microservicio-ia-prediccion --replicas=5

# Ver el resultado
kubectl get pods
```

### Auto-escalado (HPA):

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

```bash
kubectl apply -f hpa.yaml
```

---

## 🎯 Integración con Spring Boot

Desde Spring Boot, actualiza la URL del microservicio:

```java
// application.properties
ia.microservicio.url=http://<EXTERNAL-IP>/predict
```

O usa un nombre de dominio:

```java
ia.microservicio.url=https://ia-prediccion.tudominio.com/predict
```

---

## ✅ Checklist de Despliegue

- [ ] Cluster de Kubernetes creado en Digital Ocean
- [ ] `kubectl` configurado y conectado
- [ ] App Password de Gmail generado
- [ ] Secret `fastapi-secrets` creado con todas las variables
- [ ] Deployment aplicado (`kubernetes-deployment.yaml`)
- [ ] Pods en estado `Running`
- [ ] Service con `EXTERNAL-IP` asignada
- [ ] Health check respondiendo: `curl http://<IP>/health`
- [ ] Log muestra: "✅ Email Service - MODO REAL activado"
- [ ] Prueba de envío de email exitosa
- [ ] Spring Boot actualizado con nueva URL

---

## 📞 Comandos Útiles

```bash
# Ver todo
kubectl get all

# Logs en tiempo real
kubectl logs -f -l app=prediccion-ia --all-containers=true

# Entrar a un pod (debugging)
kubectl exec -it <pod-name> -- /bin/sh

# Ver configuración
kubectl get deployment microservicio-ia-prediccion -o yaml

# Ver endpoints
kubectl get endpoints

# Reiniciar deployment
kubectl rollout restart deployment/microservicio-ia-prediccion
```

---

*Guía de despliegue: 11 de Noviembre, 2025*  
*Plataforma: Digital Ocean Kubernetes*  
*Estado: ✅ LISTO PARA PRODUCCIÓN*
