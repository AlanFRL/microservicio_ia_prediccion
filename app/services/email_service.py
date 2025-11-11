"""
Servicio para enviar recordatorios por email
Modo simulación: solo registra en logs (no envía emails reales)
"""

import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails de recordatorio"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = os.getenv("SMTP_PORT", 587)
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        self.smtp_configured = bool(self.smtp_host and self.smtp_user)
        
        if not self.smtp_configured:
            logger.warning("⚠️  SMTP no configurado - Modo SIMULACIÓN activado")
    
    async def enviar_recordatorio(self, alerta: dict) -> bool:
        """
        Envía un recordatorio por email al cliente
        En modo simulación: solo registra en logs
        
        Args:
            alerta: Documento de MongoDB con datos de la predicción
        
        Returns:
            True si se envió (o simuló) exitosamente
        """
        try:
            email = alerta.get("email_cliente", "sin-email@ejemplo.com")
            nombre = alerta.get("nombre_cliente", "Cliente")
            paquete = alerta.get("nombre_paquete", "Paquete")
            destino = alerta.get("destino", "Destino")
            monto = alerta.get("monto_total", 0)
            probabilidad = alerta.get("probabilidad_cancelacion", 0)
            venta_id = alerta.get("venta_id", "")
            
            # Modo simulación (no envía email real)
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
║                                                          ║
║ Por favor, confirme su reserva lo antes posible.        ║
║                                                          ║
║ Gracias,                                                 ║
║ Agencia de Viajes                                        ║
╚══════════════════════════════════════════════════════════╝
""")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando recordatorio: {e}")
            return False
    
    def enviar_recordatorio_sync(self, alerta: dict) -> bool:
        """Versión sincrónica del envío de recordatorio"""
        import asyncio
        return asyncio.run(self.enviar_recordatorio(alerta))
