"""
API FastAPI para el Microservicio de Predicción de Cancelaciones
VERSIÓN 4.0: Con MongoDB Atlas y sistema de recordatorios
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging

from app.database import connect_db, close_db
from app.routers import prediccion, recordatorios
from app.services.prediccion_service import PrediccionService
from app.services.email_service import EmailService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Scheduler para cron jobs
scheduler = AsyncIOScheduler()
email_service = EmailService()


async def cron_enviar_recordatorios():
    """
    Cron job que se ejecuta diariamente a las 10:00 AM
    Envía recordatorios a clientes con reservas próximas (24 horas)
    """
    logger.info("🔔 Cron job: Enviando recordatorios automáticos...")
    
    try:
        alertas = PrediccionService.obtener_alertas_proximas()
        logger.info(f"📊 Alertas próximas encontradas: {len(alertas)}")
        
        enviados = 0
        for alerta in alertas:
            if await email_service.enviar_recordatorio(alerta):
                PrediccionService.marcar_enviado(alerta["venta_id"])
                enviados += 1
        
        logger.info(f"✅ Recordatorios automáticos enviados: {enviados}/{len(alertas)}")
        
    except Exception as e:
        logger.error(f"❌ Error en cron job: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto del ciclo de vida de la aplicación
    - Startup: Conecta a MongoDB y configura cron jobs
    - Shutdown: Cierra conexiones
    """
    # Startup
    logger.info("🚀 Iniciando Microservicio de Predicción de Cancelaciones v4.0...")
    
    try:
        # Conectar a MongoDB
        connect_db()
        
        # Configurar cron job (diariamente a las 10:00 AM)
        scheduler.add_job(
            cron_enviar_recordatorios,
            'cron',
            hour=10,
            minute=0,
            id='enviar_recordatorios'
        )
        scheduler.start()
        logger.info("✅ Cron job configurado: Recordatorios automáticos a las 10:00 AM")
        
        logger.info("✅ Microservicio listo")
        
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("🔌 Cerrando microservicio...")
    scheduler.shutdown()
    close_db()
    logger.info("👋 Microservicio cerrado")


# Crear aplicación FastAPI
app = FastAPI(
    title="IA Predicción de Cancelaciones",
    description="Microservicio con ML + MongoDB + Recordatorios",
    version="4.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominio de Spring Boot
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(prediccion.router, tags=["Predicción"])
app.include_router(recordatorios.router, tags=["Recordatorios"])


@app.get("/", tags=["Root"])
def root():
    """Endpoint raíz con información del servicio"""
    return {
        "message": "Microservicio IA - Predicción de Cancelaciones",
        "version": "4.0",
        "features": [
            "Predicción con ML (Random Forest)",
            "MongoDB Atlas integrado",
            "Sistema de recordatorios automáticos",
            "Cron job diario (10:00 AM)"
        ],
        "endpoints": {
            "predict": "POST /predict",
            "recordatorios": "POST /recordatorios/enviar",
            "alertas": "GET /recordatorios/alertas",
            "estadisticas": "GET /recordatorios/estadisticas",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check del servicio"""
    try:
        from app.services.predictor import get_predictor
        from app.database import get_db
        
        # Verificar modelo
        predictor = get_predictor()
        modelo_ok = predictor.is_loaded()
        
        # Verificar MongoDB
        db = get_db()
        db.command('ping')
        mongo_ok = True
        
        return {
            "status": "healthy" if (modelo_ok and mongo_ok) else "unhealthy",
            "version": "4.0",
            "modelo_cargado": modelo_ok,
            "mongodb_conectado": mongo_ok,
            "cron_activo": scheduler.running
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
