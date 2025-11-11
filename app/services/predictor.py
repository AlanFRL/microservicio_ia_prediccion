"""
Servicio de predicción que carga el modelo y realiza predicciones

VERSIÓN FINAL: Solo 11 features reales disponibles en MongoDB
edad_cliente ELIMINADA: fechaNacimiento es OPCIONAL en MongoDB
"""

import joblib
import pandas as pd
import numpy as np
from typing import Dict, List
import os


class PredictorService:
    """Servicio para cargar el modelo y hacer predicciones con 11 features"""
    
    def __init__(self, modelo_path='app/ml/modelo.pkl'):
        self.modelo_path = modelo_path
        self.modelo = None
        # 11 features reales disponibles en MongoDB (SIN edad_cliente)
        self.feature_names = [
            'monto_total', 'es_temporada_alta', 'dia_semana_reserva',
            'metodo_pago_tarjeta', 'tiene_paquete', 'duracion_dias',
            'destino_categoria', 'total_compras_previas',
            'total_cancelaciones_previas', 'tasa_cancelacion_historica',
            'monto_promedio_compras'
        ]
        self._cargar_modelo()
    
    def _cargar_modelo(self):
        """Carga el modelo desde el archivo .pkl"""
        if not os.path.exists(self.modelo_path):
            raise FileNotFoundError(f"Modelo no encontrado en: {self.modelo_path}")
        
        self.modelo = joblib.load(self.modelo_path)
        print(f"✅ Modelo cargado desde: {self.modelo_path} (11 features)")
    
    def predecir(self, data: Dict) -> Dict:
        """
        Realiza una predicción de cancelación con 11 features
        
        Args:
            data: Diccionario con los datos del request (11 features)
        
        Returns:
            Diccionario con la predicción y recomendación
        """
        # Preparar features en el orden correcto (11 features, SIN edad_cliente)
        features = {
            'monto_total': data['monto_total'],
            'es_temporada_alta': data['es_temporada_alta'],
            'dia_semana_reserva': data['dia_semana_reserva'],
            'metodo_pago_tarjeta': data['metodo_pago_tarjeta'],
            'tiene_paquete': data['tiene_paquete'],
            'duracion_dias': data['duracion_dias'],
            'destino_categoria': data['destino_categoria'],
            'total_compras_previas': data['total_compras_previas'],
            'total_cancelaciones_previas': data['total_cancelaciones_previas'],
            'tasa_cancelacion_historica': data['tasa_cancelacion_historica'],
            'monto_promedio_compras': data['monto_promedio_compras']
        }
        
        # Convertir a DataFrame (el modelo espera un DataFrame)
        df = pd.DataFrame([features])
        
        # Asegurar el orden correcto de columnas
        df = df[self.feature_names]
        
        # Hacer predicción
        probabilidad = self.modelo.predict_proba(df)[0][1]  # Probabilidad de clase 1 (cancelada)
        
        # Determinar recomendación
        if probabilidad >= 0.70:
            recomendacion = "enviar_recordatorio"
        elif probabilidad >= 0.50:
            recomendacion = "revisar_manual"
        else:
            recomendacion = "sin_accion"
        
        # Identificar factores de riesgo
        factores_riesgo = self._identificar_factores_riesgo(features)
        
        resultado = {
            'probabilidad_cancelacion': round(probabilidad, 4),
            'recomendacion': recomendacion,
            'factores_riesgo': factores_riesgo
        }
        
        return resultado
    
    def _identificar_factores_riesgo(self, features: Dict) -> List[str]:
        """
        Identifica factores de riesgo basados en los 11 features
        (SIN edad_cliente - fechaNacimiento es opcional en MongoDB)
        
        Args:
            features: Diccionario con los features calculados
        
        Returns:
            Lista de strings describiendo los factores de riesgo
        """
        factores = []
        
        # Sin pago confirmado (CRÍTICO)
        if features['metodo_pago_tarjeta'] == 0:
            factores.append("Método de pago no confirmado")
        
        # Historial de cancelaciones
        if features['tasa_cancelacion_historica'] > 0.3:
            factores.append("Alta tasa de cancelaciones previas (>30%)")
        
        # Cliente nuevo
        if features['total_compras_previas'] == 0:
            factores.append("Cliente nuevo (sin historial)")
        
        # Monto muy alto
        if features['monto_total'] > 2500:
            factores.append("Monto de venta elevado (>$2500)")
        
        # Múltiples cancelaciones
        if features['total_cancelaciones_previas'] > 2:
            factores.append("Historial con múltiples cancelaciones")
        
        # Viaje muy largo
        if features['duracion_dias'] > 10:
            factores.append("Viaje de larga duración (>10 días)")
        
        return factores
    
    def is_loaded(self) -> bool:
        """Verifica si el modelo está cargado"""
        return self.modelo is not None


# Instancia global del servicio (singleton)
predictor = None


def get_predictor() -> PredictorService:
    """Obtiene la instancia del predictor"""
    global predictor
    if predictor is None:
        predictor = PredictorService()
    return predictor
