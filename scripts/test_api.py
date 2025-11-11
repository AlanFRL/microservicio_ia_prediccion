"""
Script para probar el endpoint /predict del microservicio

VERSIÓN FINAL: Solo 11 features reales disponibles en MongoDB
edad_cliente ELIMINADA: fechaNacimiento es OPCIONAL en MongoDB
Este script simula una llamada desde Spring Boot al microservicio de IA
"""

import requests
import json

# URL del microservicio
BASE_URL = "http://localhost:8001"


def test_health():
    """Prueba el endpoint /health"""
    print("\n" + "="*60)
    print("🏥 PROBANDO ENDPOINT /health")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 200


def test_predict_alto_riesgo():
    """Prueba con un caso de ALTO riesgo de cancelación"""
    print("\n" + "="*60)
    print("🔴 CASO 1: ALTO RIESGO DE CANCELACIÓN")
    print("="*60)
    
    # Cliente nuevo, sin pago confirmado, monto alto (11 features - SIN edad_cliente)
    data = {
        "venta_id": "venta_test_001",
        "cliente_id": "cli_test_001",
        # Features de venta (7)
        "monto_total": 2800.0,  # Monto alto
        "es_temporada_alta": 1,
        "dia_semana_reserva": 2,
        "metodo_pago_tarjeta": 0,  # Sin pago confirmado
        "tiene_paquete": 1,
        "duracion_dias": 12,  # Viaje largo
        "destino_categoria": 0,
        # Features de cliente (4) - SIN edad_cliente
        "total_compras_previas": 0,  # Cliente nuevo
        "total_cancelaciones_previas": 0,
        "tasa_cancelacion_historica": 0.0,
        "monto_promedio_compras": 0.0
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n💡 INTERPRETACIÓN:")
    print(f"   Probabilidad: {result['probabilidad_cancelacion']*100:.1f}%")
    print(f"   Recomendación: {result['recomendacion']}")
    print(f"   Factores de riesgo: {len(result['factores_riesgo'])}")
    
    return response.status_code == 200


def test_predict_bajo_riesgo():
    """Prueba con un caso de BAJO riesgo de cancelación"""
    print("\n" + "="*60)
    print("🟢 CASO 2: BAJO RIESGO DE CANCELACIÓN")
    print("="*60)
    
    # Cliente frecuente, con pago confirmado (11 features - SIN edad_cliente)
    data = {
        "venta_id": "venta_test_002",
        "cliente_id": "cli_test_002",
        # Features de venta (7)
        "monto_total": 1200.0,  # Monto razonable
        "es_temporada_alta": 0,
        "dia_semana_reserva": 3,
        "metodo_pago_tarjeta": 1,  # Pagó con tarjeta
        "tiene_paquete": 1,
        "duracion_dias": 5,
        "destino_categoria": 1,
        # Features de cliente (4) - SIN edad_cliente
        "total_compras_previas": 8,  # Cliente frecuente
        "total_cancelaciones_previas": 0,  # Sin cancelaciones
        "tasa_cancelacion_historica": 0.0,
        "monto_promedio_compras": 1100.0
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n💡 INTERPRETACIÓN:")
    print(f"   Probabilidad: {result['probabilidad_cancelacion']*100:.1f}%")
    print(f"   Recomendación: {result['recomendacion']}")
    print(f"   Factores de riesgo: {len(result['factores_riesgo'])}")
    
    return response.status_code == 200


def test_predict_riesgo_medio():
    """Prueba con un caso de RIESGO MEDIO de cancelación"""
    print("\n" + "="*60)
    print("🟡 CASO 3: RIESGO MEDIO DE CANCELACIÓN")
    print("="*60)
    
    # Cliente con historial mixto (11 features - SIN edad_cliente)
    data = {
        "venta_id": "venta_test_003",
        "cliente_id": "cli_test_003",
        # Features de venta (7)
        "monto_total": 1800.0,
        "es_temporada_alta": 1,
        "dia_semana_reserva": 5,
        "metodo_pago_tarjeta": 1,
        "tiene_paquete": 1,
        "duracion_dias": 7,
        "destino_categoria": 1,
        # Features de cliente (4) - SIN edad_cliente
        "total_compras_previas": 4,
        "total_cancelaciones_previas": 2,  # Historial de cancelaciones
        "tasa_cancelacion_historica": 0.5,
        "monto_promedio_compras": 1500.0
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n💡 INTERPRETACIÓN:")
    print(f"   Probabilidad: {result['probabilidad_cancelacion']*100:.1f}%")
    print(f"   Recomendación: {result['recomendacion']}")
    print(f"   Factores de riesgo: {len(result['factores_riesgo'])}")
    
    return response.status_code == 200


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🧪 PROBANDO MICROSERVICIO DE PREDICCIÓN DE CANCELACIONES")
    print("="*60)
    
    try:
        # Test 1: Health check
        health_ok = test_health()
        
        if not health_ok:
            print("\n❌ El servicio no está saludable. Abortando pruebas.")
            return
        
        # Test 2: Predicción alto riesgo
        test_predict_alto_riesgo()
        
        # Test 3: Predicción bajo riesgo
        test_predict_bajo_riesgo()
        
        # Test 4: Predicción riesgo medio
        test_predict_riesgo_medio()
        
        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*60)
        print("\n📌 El microservicio está funcionando correctamente")
        print("📌 Spring Boot puede consumir el endpoint: POST http://localhost:8001/predict")
        print("📌 Documentación interactiva: http://localhost:8001/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al microservicio")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
