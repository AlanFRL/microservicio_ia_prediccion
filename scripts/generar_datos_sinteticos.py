"""
Script para generar datos sintéticos de entrenamiento
VERSIÓN FINAL: 11 features (SIN edad_cliente - fechaNacimiento es opcional en MongoDB)
"""

import pandas as pd
import numpy as np
import os

def generar_datos_sinteticos(n_samples=1000):
    """
    Genera dataset sintético con 11 features para entrenar el modelo
    
    Features:
    - 7 de venta: monto_total, es_temporada_alta, dia_semana_reserva, 
                  metodo_pago_tarjeta, tiene_paquete, duracion_dias, destino_categoria
    - 4 de cliente: total_compras_previas, total_cancelaciones_previas,
                    tasa_cancelacion_historica, monto_promedio_compras
    """
    
    np.random.seed(42)
    
    print(f"🔄 Generando {n_samples} registros sintéticos con 11 features...")
    
    # Features de venta (7)
    monto_total = np.random.uniform(500, 4000, n_samples)
    es_temporada_alta = np.random.choice([0, 1], n_samples, p=[0.65, 0.35])
    dia_semana_reserva = np.random.randint(0, 7, n_samples)
    metodo_pago_tarjeta = np.random.choice([0, 1], n_samples, p=[0.25, 0.75])
    tiene_paquete = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    duracion_dias = np.random.randint(3, 15, n_samples)
    destino_categoria = np.random.choice([0, 1, 2], n_samples, p=[0.4, 0.3, 0.3])
    
    # Features de cliente (4) - SIN edad_cliente
    total_compras_previas = np.random.randint(0, 15, n_samples)
    total_cancelaciones_previas = np.random.randint(0, 5, n_samples)
    
    # Calcular tasa_cancelacion_historica
    tasa_cancelacion_historica = np.where(
        total_compras_previas > 0,
        total_cancelaciones_previas / total_compras_previas,
        0
    )
    
    monto_promedio_compras = np.random.uniform(800, 3000, n_samples)
    
    # Crear DataFrame
    df = pd.DataFrame({
        'monto_total': monto_total,
        'es_temporada_alta': es_temporada_alta,
        'dia_semana_reserva': dia_semana_reserva,
        'metodo_pago_tarjeta': metodo_pago_tarjeta,
        'tiene_paquete': tiene_paquete,
        'duracion_dias': duracion_dias,
        'destino_categoria': destino_categoria,
        'total_compras_previas': total_compras_previas,
        'total_cancelaciones_previas': total_cancelaciones_previas,
        'tasa_cancelacion_historica': tasa_cancelacion_historica,
        'monto_promedio_compras': monto_promedio_compras
    })
    
    # Generar target (fue_cancelada) basado en lógica de negocio
    # Factores de riesgo de cancelación
    probabilidad_cancelacion = (
        # Cliente con historial de cancelaciones
        (df['tasa_cancelacion_historica'] > 0.3) * 0.35 +
        
        # Método de pago no confirmado (no tarjeta)
        (df['metodo_pago_tarjeta'] == 0) * 0.25 +
        
        # Múltiples cancelaciones previas
        (df['total_cancelaciones_previas'] > 2) * 0.20 +
        
        # Monto alto (mayor riesgo)
        (df['monto_total'] > 2500) * 0.15 +
        
        # Cliente nuevo (sin historial)
        (df['total_compras_previas'] == 0) * 0.10 +
        
        # Viajes largos (más tiempo para arrepentirse)
        (df['duracion_dias'] > 10) * 0.10 +
        
        # Temporada alta (más opciones, más competencia)
        (df['es_temporada_alta'] == 1) * 0.08
    )
    
    # Añadir ruido aleatorio
    probabilidad_cancelacion += np.random.uniform(-0.15, 0.15, n_samples)
    probabilidad_cancelacion = np.clip(probabilidad_cancelacion, 0, 1)
    
    # Generar variable target
    df['fue_cancelada'] = (probabilidad_cancelacion > 0.5).astype(int)
    
    return df


if __name__ == "__main__":
    # Crear directorio data si no existe
    os.makedirs("data", exist_ok=True)
    
    # Generar dataset
    df = generar_datos_sinteticos(n_samples=1000)
    
    # Guardar a CSV
    output_path = "data/dataset_sintetico.csv"
    df.to_csv(output_path, index=False)
    
    # Estadísticas
    print("\n" + "="*60)
    print("✅ Dataset generado exitosamente")
    print("="*60)
    print(f"📁 Archivo: {output_path}")
    print(f"📊 Total registros: {len(df)}")
    print(f"📊 Features: 11")
    print(f"\n🔢 Distribución de la variable target:")
    print(f"   - Canceladas: {df['fue_cancelada'].sum()} ({df['fue_cancelada'].mean()*100:.1f}%)")
    print(f"   - No canceladas: {(1-df['fue_cancelada']).sum()} ({(1-df['fue_cancelada']).mean()*100:.1f}%)")
    print(f"\n📋 Features incluidas:")
    print(f"   Venta (7): monto_total, es_temporada_alta, dia_semana_reserva,")
    print(f"              metodo_pago_tarjeta, tiene_paquete, duracion_dias, destino_categoria")
    print(f"   Cliente (4): total_compras_previas, total_cancelaciones_previas,")
    print(f"                tasa_cancelacion_historica, monto_promedio_compras")
    print(f"\n❌ Feature eliminada: edad_cliente (fechaNacimiento es opcional en MongoDB)")
    print("="*60)
    print("\n🚀 Siguiente paso: python scripts/train.py")
