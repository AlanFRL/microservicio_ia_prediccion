# 📧 Guía: Configurar Gmail para Envío de Emails

**Fecha:** 11 de Noviembre, 2025  
**Email:** alanfromerol@gmail.com

---

## 🎯 Objetivo

Configurar Gmail para que el microservicio pueda enviar emails **REALES** de recordatorios a los clientes.

---

## 📋 Requisitos Previos

- ✅ Cuenta de Gmail: `alanfromerol@gmail.com`
- ✅ Verificación en dos pasos activada
- ✅ Generar "App Password" (contraseña de aplicación)

---

## 🔧 Paso 1: Activar Verificación en Dos Pasos

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. En el menú lateral, selecciona **"Seguridad"**
3. Busca la sección **"Verificación en dos pasos"**
4. Si NO está activada:
   - Click en **"Verificación en dos pasos"**
   - Sigue los pasos para activarla (SMS, llamada o app Authenticator)
   - **IMPORTANTE:** Debe estar activada para generar App Passwords

---

## 🔑 Paso 2: Generar App Password (Contraseña de Aplicación)

1. Una vez activada la verificación en dos pasos, regresa a **"Seguridad"**
2. Busca **"Contraseñas de aplicaciones"** o **"App Passwords"**
   - URL directa: https://myaccount.google.com/apppasswords
3. Es posible que te pida tu contraseña de Gmail nuevamente
4. En la página de App Passwords:
   - **Nombre de la aplicación:** `Microservicio IA Agencia`
   - Click en **"Crear"** o **"Generate"**
5. Google generará una contraseña de **16 caracteres** con este formato:
   ```
   abcd efgh ijkl mnop
   ```
6. **COPIA ESTA CONTRASEÑA** - Solo se muestra una vez
7. Click en **"Listo"**

---

## ⚙️ Paso 3: Configurar .env

Abre tu archivo `.env` (NO el `.env.example`) y configura:

```bash
# Email Configuration - MODO REAL
EMAIL_MODE=real
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alanfromerol@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
```

**Reemplaza:** `abcd efgh ijkl mnop` con tu App Password real de 16 caracteres.

---

## 🧪 Paso 4: Probar el Envío

### Opción A: Reiniciar el servidor

1. Detén el servidor FastAPI (Ctrl+C)
2. Inicia nuevamente:
   ```powershell
   python main_v4.py
   ```
3. Deberías ver:
   ```
   ✅ Email Service - MODO REAL activado (alanfromerol@gmail.com)
   ```

### Opción B: Envío forzado desde Angular

1. Ve a tu aplicación Angular
2. Busca el botón **"Enviar Recordatorios"**
3. Click en el botón
4. Observa los logs de FastAPI

### Opción C: Prueba manual con curl

```powershell
curl -X POST http://localhost:8001/recordatorios/enviar-forzado
```

---

## ✅ Verificación de Éxito

### En los Logs de FastAPI:

**ANTES (Modo Simulación):**
```
⚠️  Email Service - Modo SIMULACIÓN activado
📧 EMAIL RECORDATORIO (SIMULACIÓN)
```

**DESPUÉS (Modo Real - Éxito):**
```
✅ Email Service - MODO REAL activado (alanfromerol@gmail.com)
📧 Enviando email REAL a: cliente@ejemplo.com (Venta: 69133dea...)
✅ Email enviado exitosamente a cliente@ejemplo.com
```

### En tu Gmail:

1. Abre Gmail en tu navegador
2. Ve a **"Enviados"**
3. Deberías ver los emails enviados a los clientes

---

## 🚨 Problemas Comunes

### Error: "Authentication Failed"

```
❌ Error de autenticación SMTP - Verifica SMTP_USER y SMTP_PASSWORD
   Gmail requiere 'App Password', no tu contraseña normal
```

**Solución:**
- ✅ Verifica que usaste el **App Password** (16 caracteres)
- ✅ NO uses tu contraseña normal de Gmail
- ✅ Verifica que la verificación en dos pasos está ACTIVA

### Error: "Connection refused"

**Solución:**
- Verifica que `SMTP_HOST=smtp.gmail.com`
- Verifica que `SMTP_PORT=587`
- Verifica tu conexión a internet

### Email no llega al destinatario

**Posibles causas:**
1. El email del cliente es inválido (sin `@`)
2. El email cayó en SPAM
3. El email del cliente no existe

**Revisa los logs:**
```
⚠️  Email inválido o faltante para venta xxx: 'email' - OMITIENDO
```

---

## 🔒 Seguridad

### ✅ Buenas Prácticas:

1. **NUNCA** compartas tu App Password
2. **NUNCA** subas tu `.env` a GitHub (ya está en `.gitignore`)
3. Si crees que tu App Password se filtró:
   - Ve a https://myaccount.google.com/apppasswords
   - Revoca la contraseña comprometida
   - Genera una nueva

### ✅ Para Kubernetes/Producción:

NO uses archivos `.env`. Usa **Kubernetes Secrets**:

```bash
kubectl create secret generic fastapi-secrets \
  --from-literal=EMAIL_MODE="real" \
  --from-literal=SMTP_HOST="smtp.gmail.com" \
  --from-literal=SMTP_PORT="587" \
  --from-literal=SMTP_USER="alanfromerol@gmail.com" \
  --from-literal=SMTP_PASSWORD="tu-app-password"
```

---

## 📊 Monitoreo

### Ver estadísticas de recordatorios:

```powershell
curl http://localhost:8001/recordatorios/estadisticas
```

**Response:**
```json
{
  "success": true,
  "total_predicciones": 5,
  "recordatorios_pendientes": 3,
  "recordatorios_enviados": 2
}
```

### Ver alertas pendientes:

```powershell
curl http://localhost:8001/recordatorios/alertas
```

---

## 🎨 Diseño del Email

El email que recibirán los clientes tiene:

✅ **Diseño HTML profesional**
- Gradiente en header
- Tabla con información de la reserva
- Responsive (se ve bien en móviles)
- Colores corporativos

✅ **Contenido:**
- Saludo personalizado con nombre del cliente
- Detalles de la reserva (paquete, destino, monto, fecha)
- Llamado a la acción (confirmar reserva)
- Footer con información de la agencia

✅ **Fallback:**
- Si el cliente no puede ver HTML, se muestra versión de texto plano

---

## 🔄 Cambiar entre Modos

### Volver a Modo Simulación (Desarrollo):

En tu `.env`:
```bash
EMAIL_MODE=simulacion
```

### Activar Modo Real (Producción):

En tu `.env`:
```bash
EMAIL_MODE=real
```

Luego reinicia el servidor.

---

## 📞 Límites de Gmail

- **Gratis:** Hasta **500 emails por día**
- Si necesitas más, considera:
  - SendGrid (100/día gratis)
  - Mailgun
  - AWS SES

---

## ✅ Checklist Final

- [ ] Verificación en dos pasos activada en Gmail
- [ ] App Password generada (16 caracteres)
- [ ] `.env` configurado con App Password
- [ ] `EMAIL_MODE=real` en `.env`
- [ ] Servidor reiniciado
- [ ] Log muestra: "✅ Email Service - MODO REAL activado"
- [ ] Email de prueba enviado exitosamente
- [ ] Email recibido en la bandeja de salida de Gmail

---

## 🎯 Próximos Pasos

1. ✅ Configura Gmail siguiendo esta guía
2. ✅ Prueba el envío con el botón de Angular
3. ✅ Verifica que los emails lleguen
4. ✅ Prepara para despliegue en Kubernetes

---

*Guía creada: 11 de Noviembre, 2025*  
*Email: alanfromerol@gmail.com*  
*Estado: ✅ LISTO PARA CONFIGURAR*
