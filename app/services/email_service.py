"""
Servicio para enviar recordatorios por email
Soporta dos modos:
- SIMULACIÓN: Solo registra en logs (útil para desarrollo)
- REAL: Envía emails reales vía SMTP (producción)
"""

import logging
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import asyncio

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails de recordatorio con manejo robusto de errores"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        self.email_mode = os.getenv("EMAIL_MODE", "simulacion").lower()
        
        # Determinar si SMTP está configurado
        self.smtp_configured = bool(self.smtp_host and self.smtp_user and self.smtp_password)
        
        # Modo de operación
        if self.email_mode == "real" and self.smtp_configured:
            self.modo_real = True
            logger.info(f"✅ Email Service - MODO REAL activado ({self.smtp_user})")
        else:
            self.modo_real = False
            if self.email_mode == "real" and not self.smtp_configured:
                logger.warning("⚠️  EMAIL_MODE=real pero SMTP no configurado - Usando SIMULACIÓN")
            else:
                logger.warning("⚠️  Email Service - Modo SIMULACIÓN activado")
    
    def _crear_html_email(self, nombre: str, paquete: str, destino: str, monto: float, 
                          probabilidad: float, fecha_venta: str) -> str:
        """Crea el contenido HTML del email"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                      padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .info-table {{ width: 100%; margin: 20px 0; }}
        .info-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .info-table td:first-child {{ font-weight: bold; width: 40%; }}
        .footer {{ text-align: center; margin-top: 20px; color: #777; font-size: 12px; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Recordatorio de Reserva</h1>
        </div>
        <div class="content">
            <p>Estimado(a) <strong>{nombre}</strong>,</p>
            
            <div class="alert-box">
                <strong>⏰ Recordatorio importante:</strong> Tiene una reserva pendiente de confirmación.
            </div>
            
            <p>Le recordamos los detalles de su reserva:</p>
            
            <table class="info-table">
                <tr>
                    <td>📦 Paquete:</td>
                    <td>{paquete}</td>
                </tr>
                <tr>
                    <td>🌍 Destino:</td>
                    <td>{destino}</td>
                </tr>
                <tr>
                    <td>💰 Monto Total:</td>
                    <td><strong>${monto:,.2f}</strong></td>
                </tr>
                <tr>
                    <td>📅 Fecha de Venta:</td>
                    <td>{fecha_venta}</td>
                </tr>
            </table>
            
            <p><strong>Por favor, confirme su reserva lo antes posible</strong> para asegurar su lugar 
            y evitar la pérdida de su reserva.</p>
            
            <p>Si tiene alguna pregunta o necesita asistencia, no dude en contactarnos.</p>
            
            <div class="footer">
                <p>Este es un mensaje automático del sistema de recordatorios de la Agencia de Viajes.</p>
                <p>© 2025 Agencia de Viajes - Todos los derechos reservados</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    async def _enviar_email_real(self, destinatario: str, nombre: str, paquete: str, 
                                  destino: str, monto: float, probabilidad: float,
                                  fecha_venta: str) -> bool:
        """
        Envía un email real vía SMTP
        
        Args:
            destinatario: Email del cliente
            nombre: Nombre del cliente
            paquete: Nombre del paquete turístico
            destino: Destino del viaje
            monto: Monto total de la reserva
            probabilidad: Probabilidad de cancelación (para logs)
            fecha_venta: Fecha de la venta
            
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        try:
            # Validar email del destinatario
            if not destinatario or "@" not in destinatario:
                logger.warning(f"⚠️  Email inválido: {destinatario} - OMITIENDO")
                return False
            
            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = f"⚠️ Recordatorio: Confirmación de su Reserva - {paquete}"
            message["From"] = self.smtp_user
            message["To"] = destinatario
            
            # Crear contenido HTML
            html_content = self._crear_html_email(
                nombre, paquete, destino, monto, probabilidad, fecha_venta
            )
            
            # Crear contenido de texto plano (fallback)
            text_content = f"""
Estimado(a) {nombre},

Le recordamos que tiene una reserva pendiente de confirmación.

Detalles de su reserva:
• Paquete: {paquete}
• Destino: {destino}
• Monto Total: ${monto:,.2f}
• Fecha de Venta: {fecha_venta}

Por favor, confirme su reserva lo antes posible para asegurar su lugar.

Gracias,
Agencia de Viajes
"""
            
            # Adjuntar ambas partes
            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part1)
            message.attach(part2)
            
            # Enviar email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=False,  # Inicialmente sin TLS
                start_tls=True   # Luego iniciar TLS con STARTTLS
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)
            
            logger.info(f"✅ Email enviado exitosamente a: {destinatario}")
            return True
            
        except aiosmtplib.SMTPAuthenticationError:
            logger.error(f"❌ Error de autenticación SMTP - Verifica SMTP_USER y SMTP_PASSWORD")
            logger.error(f"   Gmail requiere 'App Password', no tu contraseña normal")
            return False
        except aiosmtplib.SMTPException as e:
            logger.error(f"❌ Error SMTP enviando a {destinatario}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado enviando email a {destinatario}: {e}")
            return False
    
    async def enviar_recordatorio(self, alerta: dict) -> bool:
        """
        Envía un recordatorio por email al cliente
        
        - MODO REAL: Envía email real vía SMTP
        - MODO SIMULACIÓN: Solo registra en logs
        
        Manejo robusto de errores: Si el email es inválido o falla el envío,
        registra el error pero retorna True para no bloquear otros procesos.
        
        Args:
            alerta: Documento de MongoDB con datos de la predicción
        
        Returns:
            True si se procesó (enviado o simulado), False solo en errores críticos
        """
        try:
            # Extraer datos del cliente
            email = alerta.get("email_cliente", "").strip()
            nombre = alerta.get("nombre_cliente", "Cliente")
            paquete = alerta.get("nombre_paquete", "Paquete Turístico")
            destino = alerta.get("destino", "Destino")
            monto = alerta.get("monto_total", 0)
            probabilidad = alerta.get("probabilidad_cancelacion", 0)
            venta_id = alerta.get("venta_id", "")
            fecha_venta = alerta.get("fecha_venta", datetime.now().strftime("%Y-%m-%d"))
            
            # Si es fecha en formato datetime, convertir a string
            if isinstance(fecha_venta, datetime):
                fecha_venta = fecha_venta.strftime("%Y-%m-%d")
            
            # Validar que tengamos un email
            if not email or "@" not in email:
                logger.warning(f"⚠️  Email inválido o faltante para venta {venta_id}: '{email}' - OMITIENDO")
                return True  # No es un error crítico, solo omitimos este email
            
            # MODO REAL - Enviar email vía SMTP
            if self.modo_real:
                logger.info(f"📧 Enviando email REAL a: {email} (Venta: {venta_id})")
                resultado = await self._enviar_email_real(
                    email, nombre, paquete, destino, monto, probabilidad, fecha_venta
                )
                
                if resultado:
                    logger.info(f"✅ Email enviado exitosamente a {email}")
                else:
                    logger.warning(f"⚠️  No se pudo enviar email a {email} - Continuando...")
                
                return True  # Siempre retornamos True para no bloquear otros emails
            
            # MODO SIMULACIÓN - Solo logs
            else:
                logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║           📧 EMAIL RECORDATORIO (SIMULACIÓN)            ║
╠══════════════════════════════════════════════════════════╣
║ Para:        {email:<43} ║
║ Cliente:     {nombre:<43} ║
║ Paquete:     {paquete:<43} ║
║ Destino:     {destino:<43} ║
║ Monto:       ${monto:>8.2f}                                   ║
║ Riesgo:      {probabilidad*100:>5.1f}%                                    ║
║ Venta ID:    {venta_id:<43} ║
╠══════════════════════════════════════════════════════════╣
║ Asunto: ⚠️  Recordatorio: Confirmación de su Reserva    ║
║                                                          ║
║ Hola {nombre},                                         ║
║                                                          ║
║ Le recordamos que tiene una reserva pendiente:          ║
║ • Paquete: {paquete}                                   ║
║ • Destino: {destino}                                   ║
║ • Monto: ${monto:.2f}                                      ║
║ • Fecha: {fecha_venta}                                   ║
║                                                          ║
║ Por favor, confirme su reserva lo antes posible.        ║
║                                                          ║
║ Gracias,                                                 ║
║ Agencia de Viajes                                        ║
╚══════════════════════════════════════════════════════════╝
""")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando recordatorio: {e}")
            # Importante: retornamos True para no bloquear el resto de recordatorios
            return True
    
    def enviar_recordatorio_sync(self, alerta: dict) -> bool:
        """Versión sincrónica del envío de recordatorio"""
        import asyncio
        return asyncio.run(self.enviar_recordatorio(alerta))
