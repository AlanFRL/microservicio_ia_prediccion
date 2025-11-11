# Script de Despliegue en Kubernetes - Digital Ocean
# Ejecutar: .\deploy.ps1

param(
    [string]$DockerUser = "tuusuario",
    [string]$Version = "v1.0"
)

Write-Host "🚀 Iniciando despliegue en Kubernetes..." -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
Write-Host "1️⃣  Verificando Docker..." -ForegroundColor Yellow
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker OK" -ForegroundColor Green
Write-Host ""

# Verificar kubectl
Write-Host "2️⃣  Verificando kubectl..." -ForegroundColor Yellow
if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ kubectl no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✅ kubectl OK" -ForegroundColor Green
Write-Host ""

# Build Docker image
Write-Host "3️⃣  Construyendo imagen Docker..." -ForegroundColor Yellow
$ImageName = "$DockerUser/microservicio-ia-prediccion:$Version"
docker build -t $ImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir la imagen" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Imagen construida: $ImageName" -ForegroundColor Green
Write-Host ""

# Push a Docker Hub
Write-Host "4️⃣  Subiendo imagen a Docker Hub..." -ForegroundColor Yellow
Write-Host "   Asegúrate de haber hecho 'docker login'" -ForegroundColor Gray
docker push $ImageName
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al subir la imagen" -ForegroundColor Red
    Write-Host "   Ejecuta: docker login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Imagen subida exitosamente" -ForegroundColor Green
Write-Host ""

# Actualizar deployment YAML
Write-Host "5️⃣  Actualizando k8s-deployment.yaml..." -ForegroundColor Yellow
$DeploymentContent = Get-Content k8s-deployment.yaml -Raw
$DeploymentContent = $DeploymentContent -replace "tuusuario/microservicio-ia-prediccion:v1.0", $ImageName
Set-Content k8s-deployment.yaml -Value $DeploymentContent
Write-Host "✅ Archivo actualizado con $ImageName" -ForegroundColor Green
Write-Host ""

# Verificar conexión a K8s
Write-Host "6️⃣  Verificando conexión a Kubernetes..." -ForegroundColor Yellow
kubectl cluster-info | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ No se pudo conectar al cluster" -ForegroundColor Red
    Write-Host "   Verifica tu kubeconfig: $HOME\.kube\config" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Conexión OK" -ForegroundColor Green
Write-Host ""

# Verificar/Crear Secret
Write-Host "7️⃣  Verificando Secret..." -ForegroundColor Yellow
$SecretExists = kubectl get secret fastapi-secrets 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Secret no existe. Debes crearlo manualmente:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "kubectl create secret generic fastapi-secrets \"
    Write-Host "  --from-literal=MONGODB_URI='tu-mongodb-uri' \"
    Write-Host "  --from-literal=MONGODB_DATABASE='agencia_viajes' \"
    Write-Host "  --from-literal=UMBRAL_RIESGO='0.70' \"
    Write-Host "  --from-literal=EMAIL_MODE='real' \"
    Write-Host "  --from-literal=SMTP_HOST='smtp.gmail.com' \"
    Write-Host "  --from-literal=SMTP_PORT='587' \"
    Write-Host "  --from-literal=SMTP_USER='tu-email@gmail.com' \"
    Write-Host "  --from-literal=SMTP_PASSWORD='tu-app-password'"
    Write-Host ""
    $Continue = Read-Host "¿Continuar sin el secret? (s/n)"
    if ($Continue -ne "s") {
        exit 1
    }
} else {
    Write-Host "✅ Secret existe" -ForegroundColor Green
}
Write-Host ""

# Aplicar Deployment
Write-Host "8️⃣  Aplicando Deployment..." -ForegroundColor Yellow
kubectl apply -f k8s-deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al aplicar el deployment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Deployment aplicado" -ForegroundColor Green
Write-Host ""

# Esperar a que los pods estén listos
Write-Host "9️⃣  Esperando a que los pods estén listos..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=prediccion-ia --timeout=120s
Write-Host "✅ Pods listos" -ForegroundColor Green
Write-Host ""

# Obtener EXTERNAL-IP
Write-Host "🔟 Obteniendo EXTERNAL-IP..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar 2-3 minutos)" -ForegroundColor Gray
$MaxAttempts = 20
$Attempt = 0
$ExternalIP = ""

while ($Attempt -lt $MaxAttempts -and $ExternalIP -eq "") {
    $Attempt++
    $Service = kubectl get service prediccion-ia-service -o json | ConvertFrom-Json
    $ExternalIP = $Service.status.loadBalancer.ingress[0].ip
    
    if ($ExternalIP -eq "" -or $null -eq $ExternalIP) {
        Write-Host "   Intento $Attempt/$MaxAttempts - Esperando..." -ForegroundColor Gray
        Start-Sleep -Seconds 10
    }
}

if ($ExternalIP -ne "" -and $null -ne $ExternalIP) {
    Write-Host "✅ EXTERNAL-IP: $ExternalIP" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "🎉 ¡DESPLIEGUE EXITOSO!" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📍 URL del microservicio:" -ForegroundColor Yellow
    Write-Host "   http://$ExternalIP" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Actualiza Spring Boot:" -ForegroundColor Yellow
    Write-Host "   ia.microservicio.url=http://$ExternalIP/predict" -ForegroundColor White
    Write-Host ""
    Write-Host "🧪 Probar:" -ForegroundColor Yellow
    Write-Host "   curl http://$ExternalIP/health" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Ver logs:" -ForegroundColor Yellow
    Write-Host "   kubectl logs -f -l app=prediccion-ia" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  No se pudo obtener EXTERNAL-IP automáticamente" -ForegroundColor Yellow
    Write-Host "   Ejecuta: kubectl get services" -ForegroundColor White
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
