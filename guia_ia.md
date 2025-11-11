# 🤖 MICROSERVICIO IA #1: PREDICCIÓN DE CANCELACIONES
## Guía Completa para Implementación en Python

**Proyecto:** Agencia de Viajes - Sistema de Predicción de Cancelación de Reservas  
**Objetivo:** Predecir la probabilidad de cancelación de reservas/ventas pendientes para enviar recordatorios preventivos  
**Tecnología:** Python + FastAPI + PostgreSQL + scikit-learn  
**Fecha:** Noviembre 2025

---

## 📋 ÍNDICE

1. [Contexto del Sistema Actual](#1-contexto-del-sistema-actual)
2. [Arquitectura del Microservicio](#2-arquitectura-del-microservicio)
3. [Base de Datos del Microservicio](#3-base-de-datos-del-microservicio)
4. [Features para el Modelo ML](#4-features-para-el-modelo-ml)
5. [Estructura del Proyecto Python](#5-estructura-del-proyecto-python)
6. [Endpoints de la API](#6-endpoints-de-la-api)
7. [Proceso de Entrenamiento](#7-proceso-de-entrenamiento)
8. [Integración con Spring Boot](#8-integración-con-spring-boot)
9. [Stack Tecnológico](#9-stack-tecnológico)
10. [Próximos Pasos](#10-próximos-pasos)

---

## 1. CONTEXTO DEL SISTEMA ACTUAL

### 1.1 Base de Datos Principal (MongoDB)

El sistema principal Spring Boot usa **MongoDB** con las siguientes colecciones relevantes:

#### Colección `ventas`
```javascript
{
  "_id": "venta001",
  "clienteId": "cli001",
  "agenteId": "age001",
  "paqueteId": "paq001",  // Puede ser null
  "fechaVenta": ISODate("2025-11-10T14:30:00Z"),
  "montoTotal": 1850.0,
  "estadoVenta": "Pendiente",  // Pendiente, Confirmada, Cancelada
  "metodoPago": "TARJETA"      // TARJETA, PENDIENTE, Efectivo
}
```

#### Colección `detalleVenta`
```javascript
{
  "_id": "det001",
  "ventaId": "venta001",
  "servicioId": "serv001",  // Puede ser null
  "paqueteId": "paq001",    // Puede ser null
  "cantidad": 1,
  "precioUnitarioVenta": 1850.0,
  "subtotal": 1850.0
}
```

#### Colección `clientes`
```javascript
{
  "_id": "cli001",
  "usuarioId": "user001",
  "direccion": "Calle Principal 123",
  "fechaNacimiento": ISODate("1990-05-15"),
  "numeroPasaporte": "AB123456"
}
```

#### Colección `usuarios`
```javascript
{
  "_id": "user001",
  "nombre": "María",
  "apellido": "González",
  "email": "maria@ejemplo.com",
  "telefono": "78901234",
  "isCliente": true,
  "isAgente": false
}
```

### 1.2 Estados de Venta

- **Pendiente**: Reserva creada, no confirmada (puede cancelarse)
- **Confirmada**: Reserva/compra pagada (no puede cancelarse)
- **Cancelada**: Reserva cancelada por el cliente

### 1.3 Problema a Resolver

El sistema actual **NO guarda** probabilidades de cancelación ni historial analítico.  
**Objetivo:** Crear un modelo que prediga qué reservas en estado "Pendiente" tienen alta probabilidad de ser canceladas.

---

## 2. ARQUITECTURA DEL MICROSERVICIO

### 2.1 Diagrama de Arquitectura

```
┌─────────────────┐
│   Flutter App   │
└────────┬────────┘
         │ HTTP Request
         ▼
┌─────────────────────────────┐
│   Spring Boot Backend       │
│   (Java + MongoDB)          │
│                             │
│   Endpoint:                 │
│   POST /api/ia/cancelacion/ │
│        predict              │
└────────┬────────────────────┘
         │ HTTP Request
         │ (Datos de venta +
         │  historial cliente)
         ▼
┌─────────────────────────────┐
│  Microservicio IA Python    │
│  (FastAPI)                  │
│                             │
│  Puerto: 8001               │
│  Endpoints:                 │
│  - POST /predict            │
│  - POST /train              │
│  - GET /health              │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  PostgreSQL                 │
│  (Base de datos IA)         │
│                             │
│  Tablas:                    │
│  - predicciones             │
│  - historial_entrenamiento  │
│  - features_cache           │
└─────────────────────────────┘
```

### 2.2 Flujo de Datos

1. **Cliente crea una reserva** en Flutter (estado: Pendiente)
2. **Spring Boot** guarda la venta en MongoDB
3. **Spring Boot** llama al microservicio IA: `POST /predict`
4. **Microservicio IA**:
   - Recibe datos de la venta
   - Calcula features
   - Ejecuta modelo ML
   - Guarda predicción en PostgreSQL
   - Retorna probabilidad
5. **Spring Boot** devuelve resultado a Flutter
6. **Si probabilidad > 70%**: Sistema envía notificación push

---

## 3. BASE DE DATOS DEL MICROSERVICIO

### 3.1 ¿Por qué PostgreSQL y no MongoDB?

✅ **Razones para usar PostgreSQL:**
- Datos analíticos con estructura fija
- Necesidad de agregaciones y consultas complejas
- Mejor para datos tabulares (features del modelo)
- Soporte nativo para tipos numéricos y estadísticas
- Facilita análisis temporal (fechas, tendencias)

### 3.2 Esquema de Base de Datos

#### Tabla: `predicciones`
Guarda cada predicción realizada para auditoría y análisis.

```sql
CREATE TABLE predicciones (
    id SERIAL PRIMARY KEY,
    venta_id VARCHAR(50) NOT NULL,
    cliente_id VARCHAR(50) NOT NULL,
    fecha_prediccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Features usados
    dias_anticipacion INTEGER,
    monto_total DECIMAL(10, 2),
    destino VARCHAR(100),
    es_temporada_alta BOOLEAN,
    metodo_pago VARCHAR(50),
    
    -- Historial del cliente
    total_compras_previas INTEGER,
    total_cancelaciones_previas INTEGER,
    tasa_cancelacion_historica DECIMAL(5, 4),
    monto_promedio_compras DECIMAL(10, 2),
    dias_desde_ultima_compra INTEGER,
    
    -- Resultado del modelo
    probabilidad_cancelacion DECIMAL(5, 4),
    recomendacion VARCHAR(50), -- 'enviar_recordatorio', 'revisar_manual', 'sin_accion'
    
    -- Estado real (se actualiza después)
    fue_cancelada BOOLEAN DEFAULT NULL,
    fecha_actualizacion_estado TIMESTAMP,
    
    UNIQUE(venta_id, fecha_prediccion)
);

CREATE INDEX idx_venta_id ON predicciones(venta_id);
CREATE INDEX idx_cliente_id ON predicciones(cliente_id);
CREATE INDEX idx_fecha_prediccion ON predicciones(fecha_prediccion);
```

#### Tabla: `historial_entrenamiento`
Guarda información de cada vez que se entrena el modelo.

```sql
CREATE TABLE historial_entrenamiento (
    id SERIAL PRIMARY KEY,
    fecha_entrenamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num_registros INTEGER,
    accuracy DECIMAL(5, 4),
    precision_score DECIMAL(5, 4),
    recall DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    modelo_version VARCHAR(50),
    hiperparametros JSONB,
    ruta_modelo VARCHAR(255)
);
```

#### Tabla: `features_cache`
Cachea features calculados de clientes para optimizar predicciones.

```sql
CREATE TABLE features_cache (
    cliente_id VARCHAR(50) PRIMARY KEY,
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    total_compras INTEGER,
    total_cancelaciones INTEGER,
    tasa_cancelacion DECIMAL(5, 4),
    monto_promedio DECIMAL(10, 2),
    monto_total_historico DECIMAL(10, 2),
    dias_desde_ultima_compra INTEGER,
    dias_desde_registro INTEGER,
    destinos_favoritos JSONB,
    
    -- Actualizar cada 24 horas
    CONSTRAINT chk_fecha_valida CHECK (fecha_calculo <= CURRENT_TIMESTAMP)
);
```

### 3.3 ¿Guardar por Venta o por Cliente?

**Respuesta: AMBOS**

- **Tabla `predicciones`**: Por venta (cada reserva tiene su predicción)
- **Tabla `features_cache`**: Por cliente (features reutilizables)

**Ventajas:**
- Cada venta tiene su propia predicción (auditable)
- Features del cliente se calculan 1 vez y se cachean
- Permite analizar precisión del modelo por venta
- Permite analizar comportamiento del cliente en el tiempo

---

## 4. FEATURES PARA EL MODELO ML

### 4.1 Features de la Venta (11 features)

| Feature | Descripción | Tipo | Fuente |
|---------|-------------|------|--------|
| `dias_anticipacion` | Días entre fecha_venta y fecha_inicio_viaje | int | Calculado |
| `monto_total` | Monto total de la reserva | float | MongoDB |
| `es_temporada_alta` | Si la fecha es temporada alta (dic, jul, ago) | bool | Calculado |
| `dia_semana_reserva` | Día de la semana (0=Lun, 6=Dom) | int | Calculado |
| `hora_reserva` | Hora del día (0-23) | int | Calculado |
| `metodo_pago` | Método de pago (TARJETA=1, PENDIENTE=0) | int | MongoDB |
| `tiene_paquete` | Si la venta incluye paquete (1) o solo servicios (0) | bool | MongoDB |
| `num_servicios` | Cantidad de servicios en la venta | int | Conteo |
| `destino_categoria` | Tipo de destino (playa, ciudad, aventura) | int | Clasificación |
| `duracion_dias` | Duración del paquete en días | int | MongoDB |
| `precio_por_dia` | monto_total / duracion_dias | float | Calculado |

### 4.2 Features del Cliente (9 features)

| Feature | Descripción | Tipo | Fuente |
|---------|-------------|------|--------|
| `total_compras_previas` | Cantidad de ventas del cliente | int | MongoDB |
| `total_cancelaciones_previas` | Cantidad de cancelaciones del cliente | int | MongoDB |
| `tasa_cancelacion_historica` | cancelaciones / total_compras | float | Calculado |
| `monto_promedio_compras` | Promedio de monto de compras | float | Calculado |
| `monto_total_historico` | Suma total gastado | float | Calculado |
| `dias_desde_ultima_compra` | Días desde su última venta | int | Calculado |
| `dias_desde_registro` | Días desde que se registró | int | Calculado |
| `edad_cliente` | Edad en años | int | Calculado |
| `frecuencia_compra_mensual` | Compras por mes promedio | float | Calculado |

### 4.3 Total de Features

**20 features** en total (11 de venta + 9 de cliente)

### 4.4 Variable Target

```python
target = 'fue_cancelada'  # 0 = No cancelada, 1 = Cancelada
```

---

## 5. ESTRUCTURA DEL PROYECTO PYTHON

### 5.1 Estructura de Directorios

```
ia-prediccion-cancelaciones/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuración (DB, modelos)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── feature_engineering.py  # Cálculo de features
│   │   ├── predictor.py            # Predicción
│   │   └── trainer.py              # Entrenamiento
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── predict.py          # POST /predict
│   │   ├── train.py            # POST /train
│   │   └── health.py           # GET /health
│   │
│   └── ml/
│       ├── __init__.py
│       ├── modelo.pkl          # Modelo entrenado (generado)
│       └── scaler.pkl          # Escalador (generado)
│
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_training.ipynb
│
├── data/
│   ├── raw/
│   │   └── ventas_export.json  # Export desde MongoDB
│   ├── processed/
│   │   └── dataset_training.csv
│   └── synthetic/
│       └── datos_sinteticos.csv  # Para pruebas iniciales
│
├── tests/
│   ├── __init__.py
│   ├── test_features.py
│   └── test_predictor.py
│
├── scripts/
│   ├── export_data_from_mongo.py  # Exportar datos de MongoDB
│   ├── sync_features_cache.py     # Actualizar cache
│   └── generate_synthetic_data.py # Generar datos de prueba
│
├── requirements.txt
├── .env.example
├── .env
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 5.2 Dependencias (requirements.txt)

```txt
# Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

# Base de datos
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Machine Learning
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
joblib==1.3.2

# Utilidades
python-multipart==0.0.6
httpx==0.25.2  # Para llamar a MongoDB API si es necesario

# Logging y monitoreo
loguru==0.7.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

---

## 6. ENDPOINTS DE LA API

### 6.1 POST /predict - Predicción de Cancelación

**Objetivo:** Recibir datos de una venta y retornar probabilidad de cancelación.

#### Request

```json
POST http://localhost:8001/predict
Content-Type: application/json

{
  "venta_id": "venta001",
  "cliente_id": "cli001",
  "fecha_venta": "2025-11-10T14:30:00",
  "fecha_inicio_viaje": "2025-12-15",
  "monto_total": 1850.0,
  "metodo_pago": "TARJETA",
  "destino": "Cancún",
  "tiene_paquete": true,
  "duracion_dias": 7,
  "num_servicios": 2,
  
  "historial_cliente": {
    "total_compras_previas": 3,
    "total_cancelaciones_previas": 1,
    "monto_promedio_compras": 1200.0,
    "dias_desde_ultima_compra": 45,
    "edad_cliente": 35
  }
}
```

#### Response

```json
{
  "success": true,
  "venta_id": "venta001",
  "cliente_id": "cli001",
  "probabilidad_cancelacion": 0.78,
  "recomendacion": "enviar_recordatorio",
  "factores_riesgo": [
    "Alta tasa de cancelaciones previas",
    "Reserva con mucha anticipación",
    "Método de pago pendiente"
  ],
  "fecha_prediccion": "2025-11-10T14:35:00"
}
```

#### Lógica de Recomendación

```python
if probabilidad >= 0.70:
    recomendacion = "enviar_recordatorio"
elif probabilidad >= 0.50:
    recomendacion = "revisar_manual"
else:
    recomendacion = "sin_accion"
```

---

### 6.2 POST /train - Entrenar Modelo

**Objetivo:** Re-entrenar el modelo con datos actualizados.

#### Request

```json
POST http://localhost:8001/train
Content-Type: application/json

{
  "fecha_inicio": "2024-01-01",
  "fecha_fin": "2025-11-01",
  "test_size": 0.2,
  "hiperparametros": {
    "n_estimators": 100,
    "max_depth": 10
  }
}
```

#### Response

```json
{
  "success": true,
  "mensaje": "Modelo entrenado exitosamente",
  "metricas": {
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.79,
    "f1_score": 0.80
  },
  "num_registros": 1250,
  "fecha_entrenamiento": "2025-11-10T15:00:00",
  "modelo_version": "v1.2"
}
```

---

### 6.3 GET /health - Health Check

```json
GET http://localhost:8001/health

{
  "status": "healthy",
  "modelo_cargado": true,
  "modelo_version": "v1.2",
  "fecha_ultimo_entrenamiento": "2025-11-10T15:00:00",
  "db_conectada": true
}
```

---

## 7. PROCESO DE ENTRENAMIENTO

### 7.1 Obtención de Datos

**Opción A: Export directo desde MongoDB**

```python
# scripts/export_data_from_mongo.py
from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017")
db = client["agencia_db"]

# Obtener todas las ventas con estado conocido
ventas = list(db.ventas.find({}))
clientes = list(db.clientes.find({}))
detalles = list(db.detalleVenta.find({}))

# Convertir a DataFrame
df_ventas = pd.DataFrame(ventas)
df_clientes = pd.DataFrame(clientes)
df_detalles = pd.DataFrame(detalles)

# Guardar
df_ventas.to_csv("data/raw/ventas_export.csv", index=False)
```

**Opción B: Endpoint en Spring Boot que exporte datos**

```java
GET /api/admin/export-data-for-training?fechaInicio=2024-01-01&fechaFin=2025-11-01
```

### 7.2 Feature Engineering

```python
def calcular_features(venta, historial_cliente):
    features = {}
    
    # Features de venta
    features['dias_anticipacion'] = (venta['fecha_inicio_viaje'] - venta['fecha_venta']).days
    features['monto_total'] = venta['monto_total']
    features['es_temporada_alta'] = venta['fecha_inicio_viaje'].month in [7, 8, 12]
    features['dia_semana_reserva'] = venta['fecha_venta'].weekday()
    features['metodo_pago_tarjeta'] = 1 if venta['metodo_pago'] == 'TARJETA' else 0
    
    # Features de cliente
    features['total_compras_previas'] = historial_cliente['total_compras']
    features['tasa_cancelacion'] = (
        historial_cliente['cancelaciones'] / historial_cliente['total_compras'] 
        if historial_cliente['total_compras'] > 0 else 0
    )
    
    return features
```

### 7.3 Algoritmo Recomendado

**Random Forest Classifier**

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Entrenar
modelo = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=10,
    random_state=42,
    class_weight='balanced'  # Importante para desbalanceo
)

modelo.fit(X_train, y_train)
```

**¿Por qué Random Forest?**
- ✅ Maneja features categóricos y numéricos
- ✅ Robusto a outliers
- ✅ No requiere normalización
- ✅ Proporciona importancia de features
- ✅ Buen desempeño con pocos datos

### 7.4 Datos Sintéticos para Inicio

Como no tienes datos históricos reales todavía, generarás datos sintéticos:

```python
import numpy as np
import pandas as pd

def generar_datos_sinteticos(n=1000):
    np.random.seed(42)
    
    data = {
        'dias_anticipacion': np.random.randint(1, 180, n),
        'monto_total': np.random.uniform(500, 3000, n),
        'metodo_pago_tarjeta': np.random.choice([0, 1], n, p=[0.3, 0.7]),
        'total_compras_previas': np.random.randint(0, 20, n),
        'tasa_cancelacion': np.random.uniform(0, 0.5, n),
        # ... más features
    }
    
    # Target con lógica
    cancelacion_prob = (
        (data['dias_anticipacion'] > 90) * 0.3 +
        (data['tasa_cancelacion'] > 0.3) * 0.4 +
        (data['metodo_pago_tarjeta'] == 0) * 0.2
    )
    
    data['fue_cancelada'] = (cancelacion_prob + np.random.uniform(-0.2, 0.2, n)) > 0.5
    
    return pd.DataFrame(data)
```

---

## 8. INTEGRACIÓN CON SPRING BOOT

### 8.1 Flujo Completo

```
1. Cliente crea reserva en Flutter
   └─> POST /api/ventas
       └─> Spring Boot guarda en MongoDB (estado: Pendiente)
           └─> Spring Boot llama a IA: POST http://localhost:8001/predict
               └─> Microservicio IA:
                   1. Calcula features
                   2. Ejecuta modelo
                   3. Guarda predicción en PostgreSQL
                   4. Retorna probabilidad
               └─> Spring Boot recibe resultado
                   └─> Si prob > 0.70:
                       └─> Enviar push notification (Firebase/n8n)
```

### 8.2 Código Spring Boot (IAIntegrationService.java)

```java
@Service
public class IAIntegrationService {
    
    @Value("${ia.cancelacion.url}")
    private String iaCancelacionUrl;  // http://localhost:8001
    
    private final RestTemplate restTemplate;
    private final VentaRepository ventaRepository;
    private final ClienteRepository clienteRepository;
    
    public PredictCancelacionResponse predictCancelacion(String ventaId) {
        // 1. Obtener venta de MongoDB
        Venta venta = ventaRepository.findById(ventaId).orElseThrow();
        
        // 2. Calcular historial del cliente
        List<Venta> historial = ventaRepository.findByClienteId(venta.getClienteId());
        
        // 3. Armar request para IA
        PredictRequest request = PredictRequest.builder()
            .ventaId(venta.getId())
            .clienteId(venta.getClienteId())
            .montoTotal(venta.getMontoTotal())
            .metodoPago(venta.getMetodoPago())
            .historialCliente(calcularHistorial(historial))
            .build();
        
        // 4. Llamar al microservicio
        String url = iaCancelacionUrl + "/predict";
        ResponseEntity<PredictResponse> response = restTemplate.postForEntity(
            url, request, PredictResponse.class
        );
        
        // 5. Si probabilidad alta, enviar notificación
        if (response.getBody().getProbabilidadCancelacion() > 0.70) {
            enviarNotificacionRecordatorio(venta.getClienteId());
        }
        
        return response.getBody();
    }
}
```

### 8.3 Sincronización de Datos

**¿Cómo mantener PostgreSQL actualizado?**

**Opción 1: Sincronización en tiempo real (Recomendada)**
```python
# Cuando Spring crea/actualiza una venta
POST http://localhost:8001/sync/venta
{
  "venta_id": "venta001",
  "estado_final": "Cancelada"
}

# Microservicio actualiza tabla predicciones
UPDATE predicciones 
SET fue_cancelada = true, 
    fecha_actualizacion_estado = NOW()
WHERE venta_id = 'venta001';
```

**Opción 2: Batch nocturno**
```python
# Cron job que se ejecuta cada noche
# scripts/sync_features_cache.py
```

---

## 9. STACK TECNOLÓGICO

### 9.1 Frameworks y Librerías

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework Web | FastAPI | 0.104.1 |
| ASGI Server | Uvicorn | 0.24.0 |
| ORM | SQLAlchemy | 2.0.23 |
| Base de Datos | PostgreSQL | 15 |
| ML Framework | scikit-learn | 1.3.2 |
| Data Processing | Pandas | 2.1.3 |
| Numerical | NumPy | 1.26.2 |
| Validation | Pydantic | 2.5.0 |
| Environment | python-dotenv | 1.0.0 |

### 9.2 Configuración Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  ia-api:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ia_db
    depends_on:
      - postgres
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ia_user
      POSTGRES_PASSWORD: ia_password
      POSTGRES_DB: ia_predicciones
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

volumes:
  postgres_data:
```

---

## 10. PRÓXIMOS PASOS

### 10.1 Fase 1: Setup Inicial (Semana 1)
- [ ] Crear proyecto Python
- [ ] Instalar dependencias
- [ ] Configurar PostgreSQL
- [ ] Crear tablas (SQL schema)
- [ ] Implementar modelos SQLAlchemy
- [ ] Setup FastAPI básico

### 10.2 Fase 2: Datos Sintéticos (Semana 2)
- [ ] Generar 1000 registros sintéticos
- [ ] Entrenar modelo inicial
- [ ] Probar predicción con datos fake
- [ ] Implementar endpoint /predict
- [ ] Implementar endpoint /train

### 10.3 Fase 3: Integración (Semana 3)
- [ ] Exportar datos reales desde MongoDB
- [ ] Re-entrenar con datos reales
- [ ] Integrar con Spring Boot
- [ ] Probar flujo end-to-end
- [ ] Implementar sincronización

### 10.4 Fase 4: Producción (Semana 4)
- [ ] Dockerizar microservicio
- [ ] Deploy en servidor
- [ ] Configurar n8n para notificaciones
- [ ] Monitoreo de métricas
- [ ] Logs y alertas

---

## 📊 MÉTRICAS DE ÉXITO

### Métricas del Modelo
- **Accuracy**: > 75%
- **Precision**: > 70% (evitar falsos positivos)
- **Recall**: > 80% (no perder cancelaciones)
- **F1-Score**: > 75%

### Métricas de Negocio
- **Reducción de cancelaciones**: 20% en 3 meses
- **Tasa de respuesta a recordatorios**: > 40%
- **Tiempo de predicción**: < 500ms

---

## 🔐 VARIABLES DE ENTORNO (.env)

```env
# Base de datos
DATABASE_URL=postgresql://ia_user:ia_password@localhost:5433/ia_predicciones

# API
API_HOST=0.0.0.0
API_PORT=8001
API_ENV=development

# Modelo ML
MODELO_PATH=app/ml/modelo.pkl
SCALER_PATH=app/ml/scaler.pkl
MIN_PROBABILIDAD_ALERTA=0.70

# Spring Boot Backend
SPRING_BACKEND_URL=http://localhost:8080

# Logging
LOG_LEVEL=INFO
```

---

## 📚 RECURSOS ADICIONALES

### Documentación
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [scikit-learn Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)

### Tutoriales Recomendados
1. "Machine Learning for Churn Prediction" (Kaggle)
2. "FastAPI + PostgreSQL + Machine Learning" (YouTube)
3. "Feature Engineering for Customer Behavior" (Medium)

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

```markdown
### Setup
- [ ] Crear repositorio Git
- [ ] Instalar Python 3.11
- [ ] Crear virtual environment
- [ ] Instalar dependencias
- [ ] Configurar PostgreSQL

### Base de Datos
- [ ] Crear database
- [ ] Ejecutar schema.sql
- [ ] Verificar conexión
- [ ] Crear índices

### Modelo ML
- [ ] Generar datos sintéticos
- [ ] Feature engineering
- [ ] Train/test split
- [ ] Entrenar Random Forest
- [ ] Evaluar métricas
- [ ] Guardar modelo (.pkl)

### API
- [ ] Implementar POST /predict
- [ ] Implementar POST /train
- [ ] Implementar GET /health
- [ ] Validar schemas Pydantic
- [ ] Manejo de errores

### Integración
- [ ] Probar con Postman
- [ ] Integrar con Spring Boot
- [ ] Probar flujo completo
- [ ] Dockerizar
- [ ] Deploy
```

---

## 🎯 CONCLUSIÓN

Este microservicio será la **primera IA del proyecto**, enfocada en predecir cancelaciones de reservas.

**Características clave:**
- ✅ Base de datos propia (PostgreSQL)
- ✅ 20 features (venta + cliente)
- ✅ Modelo Random Forest
- ✅ API REST con FastAPI
- ✅ Integración transparente con Spring Boot
- ✅ Cache de features para optimización

**Próximo paso:** Implementar estructura básica del proyecto Python y comenzar con datos sintéticos.

---

**Fecha de creación:** 10 de Noviembre, 2025  
**Versión del documento:** 1.0  
**Estado:** ✅ LISTO PARA IMPLEMENTACIÓN

