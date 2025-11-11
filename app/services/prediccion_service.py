"""
Servicio para gestionar predicciones en MongoDB
Guarda predicciones de alto riesgo y gestiona recordatorios
"""

from app.database import get_db
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# Umbral de riesgo para guardar en MongoDB
UMBRAL_RIESGO = float(os.getenv("UMBRAL_RIESGO", 0.70))


class PrediccionService:
    """Servicio para gestionar predicciones de alto riesgo"""
    
    @staticmethod
    def guardar_prediccion(data: dict, resultado: dict) -> dict:
        """
        Guarda una predicción de alto riesgo en MongoDB
        
        Args:
            data: Datos completos del request (con email, nombre, etc.)
            resultado: Resultado de la predicción (probabilidad, recomendación, factores)
        
        Returns:
            Documento guardado o None si no se guardó
        """
        try:
            prob = resultado["probabilidad_cancelacion"]
            logger.info(f"🔍 Verificando si guardar: {data['venta_id']} - Probabilidad: {prob*100:.2f}% - Umbral: {UMBRAL_RIESGO*100:.0f}%")
            
            # Solo guardar si supera el umbral de riesgo
            if prob < UMBRAL_RIESGO:
                logger.info(f"⚪ {data['venta_id']}: {prob*100:.0f}% - Por debajo del umbral ({UMBRAL_RIESGO*100:.0f}%) - NO se guarda")
                return None
            
            logger.info(f"🟢 {data['venta_id']}: {prob*100:.2f}% >= {UMBRAL_RIESGO*100:.0f}% - SÍ se guardará")
            
            db = get_db()
            logger.info(f"📦 Database obtenida: {db.name}")
            
            col = db.predicciones_cancelacion
            logger.info(f"📁 Colección: predicciones_cancelacion")
            
            # No duplicar si ya existe
            existe = col.find_one({"venta_id": data["venta_id"]})
            if existe:
                logger.warning(f"⚠️  {data['venta_id']}: Ya existe en MongoDB (duplicado evitado)")
                return None
            
            logger.info(f"✅ No existe duplicado, procediendo a insertar...")
            
            logger.info(f"✅ No existe duplicado, procediendo a insertar...")
            
            # Crear documento
            documento = {
                "venta_id": data["venta_id"],
                "cliente_id": data["cliente_id"],
                "email_cliente": data.get("email_cliente"),
                "nombre_cliente": data.get("nombre_cliente"),
                "nombre_paquete": data.get("nombre_paquete"),
                "destino": data.get("destino"),
                "monto_total": data.get("monto_total"),
                "fecha_venta": data.get("fecha_venta"),
                "probabilidad_cancelacion": resultado["probabilidad_cancelacion"],
                "recomendacion": resultado["recomendacion"],
                "fecha_prediccion": datetime.utcnow(),
                "features": {
                    "monto_total": data.get("monto_total"),
                    "es_temporada_alta": data.get("es_temporada_alta"),
                    "dia_semana_reserva": data.get("dia_semana_reserva"),
                    "metodo_pago_tarjeta": data.get("metodo_pago_tarjeta"),
                    "tiene_paquete": data.get("tiene_paquete"),
                    "duracion_dias": data.get("duracion_dias"),
                    "destino_categoria": data.get("destino_categoria"),
                    "total_compras_previas": data.get("total_compras_previas"),
                    "total_cancelaciones_previas": data.get("total_cancelaciones_previas"),
                    "tasa_cancelacion_historica": data.get("tasa_cancelacion_historica"),
                    "monto_promedio_compras": data.get("monto_promedio_compras")
                },
                "factores_riesgo": resultado.get("factores_riesgo", []),
                "recordatorio_enviado": False,
                "fecha_envio_recordatorio": None,
                "created_at": datetime.utcnow()
            }
            
            logger.info(f"📄 Documento creado con {len(documento)} campos")
            
            # Insertar en MongoDB
            logger.info(f"💾 Insertando en MongoDB...")
            result = col.insert_one(documento)
            documento["_id"] = str(result.inserted_id)
            
            logger.warning(f"🚨 ✅ ALERTA GUARDADA EXITOSAMENTE: {data['venta_id']} - ID: {result.inserted_id} - {resultado['probabilidad_cancelacion']*100:.0f}% riesgo")
            
            return documento
            
        except Exception as e:
            logger.error(f"❌ ERROR CRÍTICO guardando predicción: {e}")
            logger.error(f"❌ Tipo de error: {type(e).__name__}")
            logger.error(f"❌ Detalles: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback:\n{traceback.format_exc()}")
            return None
    
    @staticmethod
    def obtener_alertas_pendientes():
        """Obtiene todas las alertas sin recordatorio enviado"""
        try:
            db = get_db()
            alertas = list(db.predicciones_cancelacion.find(
                {"recordatorio_enviado": False}
            ).sort("probabilidad_cancelacion", -1))
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo alertas: {e}")
            return []
    
    @staticmethod
    def obtener_alertas_proximas():
        """
        Obtiene alertas de ventas que ocurren en las próximas 24 horas
        y que aún no tienen recordatorio enviado
        """
        try:
            db = get_db()
            ahora = datetime.utcnow()
            manana = ahora + timedelta(days=1)
            
            alertas = list(db.predicciones_cancelacion.find({
                "recordatorio_enviado": False,
                "fecha_venta": {
                    "$gte": ahora,
                    "$lte": manana
                }
            }).sort("probabilidad_cancelacion", -1))
            
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo alertas próximas: {e}")
            return []
    
    @staticmethod
    def marcar_enviado(venta_id: str):
        """Marca una alerta como 'recordatorio enviado'"""
        try:
            db = get_db()
            result = db.predicciones_cancelacion.update_one(
                {"venta_id": venta_id},
                {"$set": {
                    "recordatorio_enviado": True,
                    "fecha_envio_recordatorio": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Recordatorio marcado como enviado: {venta_id}")
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error marcando recordatorio: {e}")
            return False
    
    @staticmethod
    def obtener_estadisticas():
        """Obtiene estadísticas de las predicciones"""
        try:
            db = get_db()
            col = db.predicciones_cancelacion
            
            total = col.count_documents({})
            pendientes = col.count_documents({"recordatorio_enviado": False})
            enviados = col.count_documents({"recordatorio_enviado": True})
            
            return {
                "total_predicciones": total,
                "recordatorios_pendientes": pendientes,
                "recordatorios_enviados": enviados
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {
                "total_predicciones": 0,
                "recordatorios_pendientes": 0,
                "recordatorios_enviados": 0
            }
