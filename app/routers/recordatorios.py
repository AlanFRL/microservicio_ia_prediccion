"""
Router para gestión de recordatorios
"""

from fastapi import APIRouter
from app.services.prediccion_service import PrediccionService
from app.services.email_service import EmailService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
email_service = EmailService()


@router.post("/recordatorios/enviar")
async def enviar_recordatorios_manual():
    """Envía recordatorios a todas las alertas pendientes (manualmente)"""
    try:
        logger.info("📨 Enviando recordatorios manualmente...")
        
        alertas = PrediccionService.obtener_alertas_pendientes()
        enviados = 0
        
        for alerta in alertas:
            if await email_service.enviar_recordatorio(alerta):
                PrediccionService.marcar_enviado(alerta["venta_id"])
                enviados += 1
        
        logger.info(f"✅ Recordatorios enviados: {enviados}/{len(alertas)}")
        
        return {
            "success": True,
            "enviados": enviados,
            "total": len(alertas)
        }
        
    except Exception as e:
        logger.error(f"❌ Error enviando recordatorios: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/recordatorios/estadisticas")
def obtener_estadisticas():
    """Obtiene estadísticas de recordatorios"""
    try:
        stats = PrediccionService.obtener_estadisticas()
        
        return {
            "success": True,
            **stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/recordatorios/alertas")
def listar_alertas():
    """Lista todas las alertas pendientes"""
    try:
        alertas = PrediccionService.obtener_alertas_pendientes()
        
        alertas_simplificadas = [
            {
                "venta_id": a.get("venta_id"),
                "cliente_id": a.get("cliente_id"),
                "email": a.get("email_cliente"),
                "nombre": a.get("nombre_cliente"),
                "paquete": a.get("nombre_paquete"),
                "destino": a.get("destino"),
                "monto": float(a.get("monto_total", 0)),
                "probabilidad": float(a.get("probabilidad_cancelacion", 0)),
                "recomendacion": a.get("recomendacion"),
                "fecha_prediccion": str(a.get("fecha_prediccion", ""))
            }
            for a in alertas
        ]
        
        return {
            "success": True,
            "total": len(alertas_simplificadas),
            "alertas": alertas_simplificadas
        }
        
    except Exception as e:
        logger.error(f"❌ Error listando alertas: {e}")
        return {
            "success": False,
            "error": str(e)
        }
