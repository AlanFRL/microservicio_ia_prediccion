# 🔄 GUÍA COMPLETA: MONGODB EN MICROSERVICIO IA #1

**Fecha:** 11 de Noviembre, 2025  
**Versión:** 4.0 - MongoDB Integrado  
**Para:** VS Code + FastAPI

---

## 🎯 RESUMEN

✅ FastAPI usará **MongoDB Atlas** (misma BD que Spring Boot)  
✅ Nueva colección: `predicciones_cancelacion`  
✅ Spring Boot envía datos completos  
✅ FastAPI guarda y gestiona recordatorios  

---

## 📊 COLECCIÓN: `predicciones_cancelacion`

```javascript
{
  "_id": ObjectId("..."),
  "venta_id": "venta001",
  "cliente_id": "cli001",
  "email_cliente": "maria@ejemplo.com",
  "nombre_cliente": "María González",
  "nombre_paquete": "Caribe Paradisíaco",
  "destino": "Cancún",
  "monto_total": 1850.0,
  "fecha_venta": ISODate("2025-12-15T00:00:00.000Z"),
  "probabilidad_cancelacion": 0.82,
  "recomendacion": "enviar_recordatorio",
  "fecha_prediccion": ISODate("2025-11-10T15:30:00.000Z"),
  "features": {
    "monto_total": 1850.0,
    "es_temporada_alta": 1,
    "dia_semana_reserva": 2,
    "metodo_pago_tarjeta": 0,
    "tiene_paquete": 1,
    "duracion_dias": 7,
    "destino_categoria": 0,
    "total_compras_previas": 3,
    "total_cancelaciones_previas": 1,
    "tasa_cancelacion_historica": 0.33,
    "monto_promedio_compras": 1200.0
  },
  "recordatorio_enviado": false,
  "fecha_envio_recordatorio": null,
  "created_at": ISODate("2025-11-10T15:30:00.000Z")
}
```

---

## 🔧 IMPLEMENTACIÓN FASTAPI

### 1. Actualizar `requirements.txt`

```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
joblib==1.3.2
pymongo==4.6.0
dnspython==2.4.2
aiosmtplib==3.0.1
email-validator==2.1.0
apscheduler==3.10.4
python-dotenv==1.0.0
```

### 2. Crear `.env`

```env
MONGODB_URI=mongodb+srv://agencia_user:uagrm2025@agencia-database.8n7ayzu.mongodb.net/?appName=agencia-database
MONGODB_DATABASE=agencia_viajes
UMBRAL_RIESGO=0.70
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

### 3. Crear `app/database.py`

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = None
db = None

def connect_db():
    global client, db
    uri = os.getenv("MONGODB_URI")
    database = os.getenv("MONGODB_DATABASE", "agencia_viajes")
    client = MongoClient(uri)
    db = client[database]
    print(f"✅ MongoDB conectado: {database}")
    return db

def get_db():
    if db is None:
        connect_db()
    return db

def close_db():
    if client:
        client.close()
```

### 4. Actualizar `app/schemas.py`

```python
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class PredictRequestFull(BaseModel):
    venta_id: str
    cliente_id: str
    email_cliente: EmailStr
    nombre_cliente: str
    nombre_paquete: Optional[str] = None
    destino: Optional[str] = None
    fecha_venta: datetime
    monto_total: float
    es_temporada_alta: int
    dia_semana_reserva: int
    metodo_pago_tarjeta: int
    tiene_paquete: int
    duracion_dias: int
    destino_categoria: int
    total_compras_previas: int
    total_cancelaciones_previas: int
    tasa_cancelacion_historica: float
    monto_promedio_compras: float

class PredictRequest(BaseModel):
    venta_id: str
    cliente_id: str
    monto_total: float
    es_temporada_alta: int
    dia_semana_reserva: int
    metodo_pago_tarjeta: int
    tiene_paquete: int
    duracion_dias: int
    destino_categoria: int
    total_compras_previas: int
    total_cancelaciones_previas: int
    tasa_cancelacion_historica: float
    monto_promedio_compras: float

class PredictResponse(BaseModel):
    success: bool
    venta_id: str
    cliente_id: str
    probabilidad_cancelacion: float
    recomendacion: str
    factores_riesgo: List[str]
```

### 5. Crear `app/services/prediccion_service.py`

```python
from app.database import get_db
from datetime import datetime, timedelta
import os

UMBRAL = float(os.getenv("UMBRAL_RIESGO", 0.70))

class PrediccionService:
    
    @staticmethod
    def guardar_prediccion(data, resultado):
        db = get_db()
        col = db.predicciones_cancelacion
        
        if resultado["probabilidad_cancelacion"] < UMBRAL:
            return None
        
        if col.find_one({"venta_id": data["venta_id"]}):
            return None
        
        doc = {
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
            "features": {k: data.get(k) for k in [
                "monto_total", "es_temporada_alta", "dia_semana_reserva",
                "metodo_pago_tarjeta", "tiene_paquete", "duracion_dias",
                "destino_categoria", "total_compras_previas",
                "total_cancelaciones_previas", "tasa_cancelacion_historica",
                "monto_promedio_compras"
            ]},
            "recordatorio_enviado": False,
            "fecha_envio_recordatorio": None,
            "created_at": datetime.utcnow()
        }
        
        col.insert_one(doc)
        print(f"⚠️ ALERTA: {data['venta_id']} - {resultado['probabilidad_cancelacion']*100:.0f}%")
        return doc
    
    @staticmethod
    def obtener_alertas_pendientes():
        db = get_db()
        return list(db.predicciones_cancelacion.find({"recordatorio_enviado": False}))
    
    @staticmethod
    def obtener_alertas_proximas():
        db = get_db()
        ahora = datetime.utcnow()
        manana = ahora + timedelta(days=1)
        return list(db.predicciones_cancelacion.find({
            "recordatorio_enviado": False,
            "fecha_venta": {"$gte": ahora, "$lte": manana}
        }))
    
    @staticmethod
    def marcar_enviado(venta_id):
        db = get_db()
        db.predicciones_cancelacion.update_one(
            {"venta_id": venta_id},
            {"$set": {
                "recordatorio_enviado": True,
                "fecha_envio_recordatorio": datetime.utcnow()
            }}
        )
```

### 6. Crear `app/services/email_service.py`

```python
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    
    def __init__(self):
        self.smtp_configured = bool(os.getenv("SMTP_HOST"))
    
    async def enviar_recordatorio(self, alerta) -> bool:
        try:
            logger.info(f"""
📧 EMAIL SIMULADO:
Para: {alerta.get('email_cliente')}
Cliente: {alerta.get('nombre_cliente')}
Paquete: {alerta.get('nombre_paquete')}
Destino: {alerta.get('destino')}
Monto: ${alerta.get('monto_total', 0):.2f}
""")
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
```

### 7. Actualizar `app/routers/prediccion.py`

```python
from fastapi import APIRouter
from app.schemas import PredictRequestFull, PredictRequest, PredictResponse
from app.services.predictor import Predictor
from app.services.prediccion_service import PrediccionService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
predictor = Predictor()

@router.post("/predict", response_model=PredictResponse)
def predecir(request: PredictRequestFull | PredictRequest):
    try:
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
        
        resultado = predictor.predecir(features)
        logger.info(f"Predicción {request.venta_id}: {resultado['probabilidad_cancelacion']*100:.1f}%")
        
        if isinstance(request, PredictRequestFull):
            PrediccionService.guardar_prediccion(request.dict(), resultado)
        
        return PredictResponse(
            success=True,
            venta_id=request.venta_id,
            cliente_id=request.cliente_id,
            probabilidad_cancelacion=resultado["probabilidad_cancelacion"],
            recomendacion=resultado["recomendacion"],
            factores_riesgo=resultado["factores_riesgo"]
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

### 8. Crear `app/routers/recordatorios.py`

```python
from fastapi import APIRouter
from app.services.prediccion_service import PrediccionService
from app.services.email_service import EmailService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
email = EmailService()

@router.post("/recordatorios/enviar")
async def enviar_manual():
    try:
        alertas = PrediccionService.obtener_alertas_pendientes()
        enviados = 0
        for alerta in alertas:
            if await email.enviar_recordatorio(alerta):
                PrediccionService.marcar_enviado(alerta["venta_id"])
                enviados += 1
        return {"success": True, "enviados": enviados, "total": len(alertas)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/recordatorios/estadisticas")
def estadisticas():
    alertas = PrediccionService.obtener_alertas_pendientes()
    return {"success": True, "alertas_pendientes": len(alertas)}

@router.get("/recordatorios/alertas")
def listar():
    alertas = PrediccionService.obtener_alertas_pendientes()
    return {
        "success": True,
        "total": len(alertas),
        "alertas": [
            {
                "venta_id": a.get("venta_id"),
                "email": a.get("email_cliente"),
                "prob": float(a.get("probabilidad_cancelacion", 0))
            }
            for a in alertas
        ]
    }
```

### 9. Actualizar `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging

from app.database import connect_db, close_db
from app.routers import prediccion, recordatorios
from app.services.prediccion_service import PrediccionService
from app.services.email_service import EmailService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
email = EmailService()

async def cron_recordatorios():
    logger.info("🔔 Cron: Recordatorios")
    try:
        alertas = PrediccionService.obtener_alertas_proximas()
        for alerta in alertas:
            if await email.enviar_recordatorio(alerta):
                PrediccionService.marcar_enviado(alerta["venta_id"])
    except Exception as e:
        logger.error(f"Error cron: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    scheduler.add_job(cron_recordatorios, 'cron', hour=10, minute=0)
    scheduler.start()
    logger.info("✅ Cron: 10:00 AM")
    yield
    scheduler.shutdown()
    close_db()

app = FastAPI(title="IA Predicción", version="4.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(prediccion.router)
app.include_router(recordatorios.router)

@app.get("/health")
def health():
    return {"status": "healthy", "version": "4.0", "database": "MongoDB"}
```

---

## ✅ TESTING

```bash
# Instalar
pip install -r requirements.txt

# Iniciar
python main.py

# Probar
curl http://localhost:8001/health
```

---

## 📋 CHECKLIST

- [ ] Actualizar requirements.txt
- [ ] Crear .env
- [ ] Crear app/database.py
- [ ] Actualizar app/schemas.py
- [ ] Crear app/services/prediccion_service.py
- [ ] Crear app/services/email_service.py
- [ ] Actualizar app/routers/prediccion.py
- [ ] Crear app/routers/recordatorios.py
- [ ] Actualizar main.py
- [ ] Probar

---

**Estado:** ✅ COMPLETO

