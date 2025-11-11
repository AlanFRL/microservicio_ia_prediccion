"""
API FastAPI para el Microservicio de Predicción de Cancelaciones

Este microservicio recibe datos de una venta y predice la probabilidad
de que sea cancelada utilizando un modelo de Random Forest.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PredictRequest, PredictResponse, HealthResponse
from app.services.predictor import get_predictor
from loguru import logger
import sys

# Configurar logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio IA - Predicción de Cancelaciones",
    description="API para predecir la probabilidad de cancelación de reservas de viajes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS (para que Spring Boot pueda llamar a esta API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio de Spring Boot
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    logger.info("🚀 Iniciando Microservicio de Predicción de Cancelaciones...")
    try:
        # Cargar el modelo al iniciar
        predictor = get_predictor()
        logger.info("✅ Modelo cargado correctamente")
    except Exception as e:
        logger.error(f"❌ Error al cargar el modelo: {e}")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "Microservicio IA - Predicción de Cancelaciones",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check del servicio
    
    Verifica que el servicio esté funcionando y el modelo esté cargado.
    """
    try:
        predictor = get_predictor()
        modelo_cargado = predictor.is_loaded()
        
        return HealthResponse(
            status="healthy" if modelo_cargado else "unhealthy",
            modelo_cargado=modelo_cargado,
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return HealthResponse(
            status="unhealthy",
            modelo_cargado=False,
            version="1.0.0"
        )


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(request: PredictRequest):
    """
    Predice la probabilidad de cancelación de una venta
    
    Args:
        request: Datos de la venta y del cliente
    
    Returns:
        Predicción con probabilidad y recomendación
    
    Raises:
        HTTPException: Si hay error en la predicción
    """
    try:
        logger.info(f"📊 Predicción solicitada para venta: {request.venta_id}")
        
        # Obtener predictor
        predictor = get_predictor()
        
        # Convertir request a dict
        data = request.model_dump()
        
        # Realizar predicción
        resultado = predictor.predecir(data)
        
        # Crear response
        response = PredictResponse(
            success=True,
            venta_id=request.venta_id,
            cliente_id=request.cliente_id,
            probabilidad_cancelacion=resultado['probabilidad_cancelacion'],
            recomendacion=resultado['recomendacion'],
            factores_riesgo=resultado['factores_riesgo']
        )
        
        logger.info(f"✅ Predicción exitosa: {resultado['probabilidad_cancelacion']:.2%} - {resultado['recomendacion']}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
