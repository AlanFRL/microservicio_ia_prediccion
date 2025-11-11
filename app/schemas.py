"""
Schemas Pydantic para validación de requests y responses
VERSIÓN 4.0: Con MongoDB y datos completos del cliente
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class PredictRequest(BaseModel):
    """Request para el endpoint /predict - 11 features reales"""
    
    # IDs (no usados por el modelo, solo para identificación)
    venta_id: str = Field(..., description="ID de la venta")
    cliente_id: str = Field(..., description="ID del cliente")
    
    # Features de venta (7)
    monto_total: float = Field(..., gt=0, description="Monto total de la venta")
    es_temporada_alta: int = Field(..., ge=0, le=1, description="1 si es temporada alta (jul, ago, dic), 0 si no")
    dia_semana_reserva: int = Field(..., ge=0, le=6, description="Día de semana (0=Lun, 6=Dom)")
    metodo_pago_tarjeta: int = Field(..., ge=0, le=1, description="1 si pagó con tarjeta, 0 si no")
    tiene_paquete: int = Field(..., ge=0, le=1, description="1 si incluye paquete, 0 si no")
    duracion_dias: int = Field(..., ge=1, description="Duración del viaje en días")
    destino_categoria: int = Field(..., ge=0, le=2, description="0=playa, 1=ciudad, 2=aventura")
    
    # Features de cliente (4) - SIN edad_cliente
    total_compras_previas: int = Field(..., ge=0, description="Compras anteriores del cliente")
    total_cancelaciones_previas: int = Field(..., ge=0, description="Cancelaciones anteriores")
    tasa_cancelacion_historica: float = Field(..., ge=0, le=1, description="Tasa de cancelación (0-1)")
    monto_promedio_compras: float = Field(..., ge=0, description="Promedio de gasto histórico")
    
    class Config:
        json_schema_extra = {
            "example": {
                "venta_id": "venta_001",
                "cliente_id": "cli_001",
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
            }
        }


class PredictRequestFull(BaseModel):
    """Request completo desde Spring Boot con datos del cliente para MongoDB"""
    
    # IDs
    venta_id: str = Field(..., description="ID de la venta")
    cliente_id: str = Field(..., description="ID del cliente")
    
    # Datos del cliente (para MongoDB y emails)
    email_cliente: EmailStr = Field(..., description="Email del cliente")
    nombre_cliente: str = Field(..., description="Nombre completo del cliente")
    nombre_paquete: Optional[str] = Field(None, description="Nombre del paquete turístico")
    destino: Optional[str] = Field(None, description="Destino del viaje")
    fecha_venta: datetime = Field(..., description="Fecha de la venta")
    
    # Features de venta (7)
    monto_total: float = Field(..., gt=0, description="Monto total de la venta")
    es_temporada_alta: int = Field(..., ge=0, le=1, description="1 si es temporada alta, 0 si no")
    dia_semana_reserva: int = Field(..., ge=0, le=6, description="Día de semana (0=Lun, 6=Dom)")
    metodo_pago_tarjeta: int = Field(..., ge=0, le=1, description="1 si pagó con tarjeta, 0 si no")
    tiene_paquete: int = Field(..., ge=0, le=1, description="1 si incluye paquete, 0 si no")
    duracion_dias: int = Field(..., ge=1, description="Duración del viaje en días")
    destino_categoria: int = Field(..., ge=0, le=2, description="0=playa, 1=ciudad, 2=aventura")
    
    # Features de cliente (4)
    total_compras_previas: int = Field(..., ge=0, description="Compras anteriores del cliente")
    total_cancelaciones_previas: int = Field(..., ge=0, description="Cancelaciones anteriores")
    tasa_cancelacion_historica: float = Field(..., ge=0, le=1, description="Tasa de cancelación (0-1)")
    monto_promedio_compras: float = Field(..., ge=0, description="Promedio de gasto histórico")
    
    class Config:
        json_schema_extra = {
            "example": {
                "venta_id": "venta_001",
                "cliente_id": "cli_001",
                "email_cliente": "maria@ejemplo.com",
                "nombre_cliente": "María González",
                "nombre_paquete": "Caribe Paradisíaco",
                "destino": "Cancún",
                "fecha_venta": "2025-12-15T00:00:00Z",
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
            }
        }


class PredictResponse(BaseModel):
    """Response del endpoint /predict"""
    
    success: bool = Field(..., description="Si la predicción fue exitosa")
    venta_id: str = Field(..., description="ID de la venta")
    cliente_id: str = Field(..., description="ID del cliente")
    probabilidad_cancelacion: float = Field(..., ge=0, le=1, description="Probabilidad de cancelación")
    recomendacion: str = Field(..., description="Recomendación: sin_accion, revisar_manual, enviar_recordatorio")
    factores_riesgo: List[str] = Field(default=[], description="Lista de factores de riesgo detectados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "venta_id": "venta_001",
                "cliente_id": "cli_001",
                "probabilidad_cancelacion": 0.78,
                "recomendacion": "enviar_recordatorio",
                "factores_riesgo": [
                    "Historial de cancelaciones previas",
                    "Reserva con mucha anticipación"
                ]
            }
        }


class HealthResponse(BaseModel):
    """Response del endpoint /health"""
    
    status: str = Field(..., description="Estado del servicio")
    modelo_cargado: bool = Field(..., description="Si el modelo está cargado")
    version: str = Field(..., description="Versión del servicio")
