"""
Router para gestión de predicciones con MongoDB
"""

from fastapi import APIRouter, HTTPException
from app.schemas import PredictRequestFull, PredictResponse
from app.services.predictor import get_predictor
from app.services.prediccion_service import PrediccionService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=PredictResponse)
def predecir(request: PredictRequestFull):
    """
    Realiza una predicción de cancelación
    
    Recibe PredictRequestFull (con email, nombre, etc.) desde Spring Boot
    Guarda en MongoDB si riesgo >= 70%
    """
    try:
        logger.info(f"📊 Predicción solicitada para venta: {request.venta_id}")
        
        # Obtener predictor
        predictor = get_predictor()
        
        # Preparar features para el modelo
        features = {
            "monto_total": request.monto_total,
            "es_temporada_alta": request.es_temporada_alta,
            "dia_semana_reserva": request.dia_semana_reserva,
            "metodo_pago_tarjeta": request.metodo_pago_tarjeta,
            "tiene_paquete": request.tiene_paquete,
            "duracion_dias": request.duracion_dias,
            "destino_categoria": request.destino_categoria,
            "total_compras_previas": request.total_compras_previas,
            "total_cancelaciones_previas": request.total_cancelaciones_previas,
            "tasa_cancelacion_historica": request.tasa_cancelacion_historica,
            "monto_promedio_compras": request.monto_promedio_compras
        }
        
        # Realizar predicción
        resultado = predictor.predecir(features)
        
        logger.info(f"✅ Predicción exitosa: {resultado['probabilidad_cancelacion']*100:.2f}% - {resultado['recomendacion']}")
        
        # Siempre intentar guardar en MongoDB si riesgo >= 70%
        logger.info(f"📝 Request tipo: PredictRequestFull detectado - Evaluando para MongoDB...")
        doc_guardado = PrediccionService.guardar_prediccion(request.dict(), resultado)
        if doc_guardado:
            logger.info(f"💾 GUARDADO EN MONGODB: {request.venta_id} - {resultado['probabilidad_cancelacion']*100:.2f}%")
        else:
            logger.info(f"⚠️  NO se guardó en MongoDB: {request.venta_id} (probabilidad < 70% o ya existe)")
        
        # Retornar respuesta
        return PredictResponse(
            success=True,
            venta_id=request.venta_id,
            cliente_id=request.cliente_id,
            probabilidad_cancelacion=resultado["probabilidad_cancelacion"],
            recomendacion=resultado["recomendacion"],
            factores_riesgo=resultado.get("factores_riesgo", [])
        )
        
    except Exception as e:
        logger.error(f"❌ Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))
