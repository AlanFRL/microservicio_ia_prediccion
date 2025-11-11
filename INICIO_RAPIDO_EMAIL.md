# ⚡ INICIO RÁPIDO - Activar Envío Real de Emails

**5 minutos para activar el envío real de correos**

---

## 📋 Paso 1: Generar App Password (2 min)

1. Abre: https://myaccount.google.com/apppasswords
2. Inicia sesión con `alanfromerol@gmail.com`
3. Crea nueva contraseña:
   - Nombre: **"Microservicio IA Agencia"**
   - Click **"Crear"**
4. **COPIA** la contraseña de 16 caracteres que aparece
   - Formato: `xxxx xxxx xxxx xxxx`
   - Solo se muestra UNA VEZ

---

## 📝 Paso 2: Editar .env (1 min)

Abre tu archivo `.env` (en la raíz del proyecto) y agrega/edita:

```bash
# Email Configuration - MODO REAL
EMAIL_MODE=real
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alanfromerol@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

**Reemplaza `xxxx xxxx xxxx xxxx`** con la App Password que copiaste.

---

## 🔄 Paso 3: Reiniciar FastAPI (30 seg)

En la terminal donde corre FastAPI:

1. Presiona **Ctrl+C** (detener)
2. Ejecuta:
   ```powershell
   python main_v4.py
   ```

---

## ✅ Paso 4: Verificar (30 seg)

### Busca este mensaje en los logs:

```
✅ Email Service - MODO REAL activado (alanfromerol@gmail.com)
```

**Si ves este mensaje:** ✅ Todo está configurado correctamente!

**Si NO lo ves:** ⚠️ Verifica el paso 2 (revisa tu `.env`)

---

## 🧪 Paso 5: Probar (1 min)

### Opción A: Desde Angular
- Busca el botón **"Enviar Recordatorios"**
- Click

### Opción B: Desde curl
```powershell
curl -X POST http://localhost:8001/recordatorios/enviar-forzado
```

### Verifica en logs:
```
📧 Enviando email REAL a: cliente@ejemplo.com
✅ Email enviado exitosamente a cliente@ejemplo.com
```

---

## 🎯 Paso 6: Verificar Gmail

1. Abre Gmail: https://mail.google.com
2. Ve a **"Enviados"**
3. Deberías ver los emails enviados a los clientes

---

## 🚨 ¿Problemas?

### Error: "Authentication Failed"
- ❌ Estás usando tu contraseña normal de Gmail
- ✅ Usa el **App Password** de 16 caracteres

### Error: "Import aiosmtplib not found"
- El paquete ya está instalado en `requirements.txt`
- Solo es un warning del editor, ignóralo

### No llegan los emails
1. Verifica que `EMAIL_MODE=real` (sin espacios)
2. Verifica que el email del cliente tiene `@`
3. Revisa la carpeta de SPAM del destinatario

---

## 📖 Más Información

- **Guía completa:** `CONFIGURAR_GMAIL.md`
- **Despliegue K8s:** `KUBERNETES_DEPLOYMENT.md`
- **Resumen técnico:** `IMPLEMENTACION_EMAIL_REAL.md`

---

## ✅ Checklist

- [ ] App Password generado de Gmail
- [ ] `.env` editado con credenciales
- [ ] FastAPI reiniciado
- [ ] Log muestra "MODO REAL activado"
- [ ] Email de prueba enviado
- [ ] Email recibido en Gmail

---

**¡Listo! Ahora tus emails se envían de verdad. 📧✅**
