# 🤖 Microservicio IA - Predicción de Cancelaciones

Microservicio de Machine Learning para predecir cancelaciones de reservas en agencia de viajes, integrado con MongoDB Atlas y sistema de recordatorios automáticos.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Características

- ✅ **Predicción ML**: Random Forest con 89.5% de accuracy
- ✅ **MongoDB Atlas**: Integración con base de datos compartida
- ✅ **Recordatorios automáticos**: Cron job diario (10:00 AM)
- ✅ **Sistema de emails**: Modo simulación y producción
- ✅ **FastAPI**: API REST con documentación automática
- ✅ **11 Features**: Optimizado sin campos poco confiables

## 🚀 Inicio Rápido

### 1. Requisitos Previos

- Python 3.11+
- MongoDB Atlas (conexión proporcionada)
- Git

### 2. Clonar el Repositorio

```bash
git clone https://github.com/AlanFRL/microservicio_ia_prediccion.git
cd microservicio_ia_prediccion
```

### 3. Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# El archivo ya tiene valores por defecto que funcionan
```

### 6. Iniciar el Microservicio

**Opción 1 - Directo:**
```bash
python main_v4.py
```

**Opción 2 - Con uvicorn:**
```bash
uvicorn main_v4:app --host 0.0.0.0 --port 8001 --reload
```

### 7. Verificar

Abre tu navegador en:
- **Health Check**: http://localhost:8001/health
- **Documentación**: http://localhost:8001/docs
- **Swagger UI**: http://localhost:8001/redoc

## 📁 Estructura del Proyecto

```
microservicio_ia_prediccion/
│
├── app/
│   ├── ml/
│   │   └── modelo.pkl                    # Modelo Random Forest entrenado
│   ├── routers/
│   │   ├── prediccion.py                 # Endpoint de predicción
│   │   └── recordatorios.py              # Endpoints de recordatorios
│   ├── services/
│   │   ├── predictor.py                  # Servicio de predicción ML
│   │   ├── prediccion_service.py         # Servicio MongoDB
│   │   └── email_service.py              # Servicio de emails
│   ├── database.py                       # Conexión MongoDB
│   └── schemas.py                        # Modelos Pydantic
│
├── data/
│   └── dataset_sintetico.csv             # Dataset de entrenamiento (1000 registros)
│
├── scripts/
│   ├── generate_dataset.py               # Generador de datos sintéticos
│   ├── train_model.py                    # Entrenamiento del modelo
│   └── test_api.py                       # Script de pruebas
│
├── .env.example                          # Ejemplo de configuración
├── .gitignore                            # Archivos ignorados por Git
├── main_v4.py                            # Aplicación FastAPI v4.0
├── requirements.txt                      # Dependencias Python
└── README.md                             # Este archivo
```

## 🔧 Configuración (.env)

```env
# MongoDB
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?appName=app
MONGODB_DATABASE=agencia_viajes

# Predicción
UMBRAL_RIESGO=0.70

# Email (dejar vacío para modo simulación)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

## 📡 API Endpoints

### 🎯 POST `/predict` - Predicción de Cancelación

Acepta dos formatos:

**Formato 1 - Solo features (11 campos):**
```json
{
  "venta_id": "venta001",
  "cliente_id": "cli001",
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
```

**Formato 2 - Completo (con datos para MongoDB):**
```json
{
  "venta_id": "venta001",
  "cliente_id": "cli001",
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
```

**Respuesta:**
```json
{
  "cancelara": true,
  "probabilidad": 0.82,
  "recomendacion": "enviar_recordatorio",
  "factores_riesgo": [
    "Método de pago no confirmado",
    "Historial de cancelaciones previas"
  ]
}
```

### 📧 Endpoints de Recordatorios

- **GET** `/recordatorios/alertas` - Listar alertas pendientes
- **POST** `/recordatorios/enviar` - Enviar recordatorios manualmente
- **GET** `/recordatorios/estadisticas` - Ver estadísticas

### 🏥 GET `/health` - Health Check

```json
{
  "status": "healthy",
  "modelo_cargado": true,
  "mongodb_conectado": true,
  "cron_activo": true,
  "version": "4.0"
}
```

## 📊 Features del Modelo (11)

1. **monto_total**: Monto total de la compra
2. **es_temporada_alta**: 1=temporada alta, 0=baja
3. **dia_semana_reserva**: 0=lunes ... 6=domingo
4. **metodo_pago_tarjeta**: 1=tarjeta, 0=otro
5. **tiene_paquete**: 1=sí, 0=no
6. **duracion_dias**: Duración del viaje
7. **destino_categoria**: 0=playa, 1=ciudad, 2=aventura, 3=cultural
8. **total_compras_previas**: Número de compras anteriores
9. **total_cancelaciones_previas**: Número de cancelaciones anteriores
10. **tasa_cancelacion_historica**: Tasa histórica (0.0-1.0)
11. **monto_promedio_compras**: Promedio de compras previas

> **Nota:** El campo `edad_cliente` fue removido en v3.0 por baja confiabilidad (fechaNacimiento es opcional en MongoDB).

## 🗄️ Colección MongoDB

El microservicio gestiona la colección `predicciones_cancelacion`:

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
  "fecha_venta": ISODate("2025-12-15"),
  "probabilidad_cancelacion": 0.82,
  "recomendacion": "enviar_recordatorio",
  "features": { /* 11 features */ },
  "factores_riesgo": ["..."],
  "recordatorio_enviado": false,
  "fecha_envio_recordatorio": null,
  "created_at": ISODate("2025-11-10")
}
```

## ⏰ Cron Jobs

- **Frecuencia**: Diario a las 10:00 AM
- **Función**: `cron_enviar_recordatorios()`
- **Acción**: Busca alertas próximas (24h) y envía recordatorios

## 📧 Sistema de Emails

### Modo Simulación (Desarrollo)

Los emails se muestran en consola:

```
╔════════════════════════════════════════════════════════════════════╗
║                   📧 EMAIL RECORDATORIO (SIMULACIÓN)                ║
╠════════════════════════════════════════════════════════════════════╣
║ Para:      maria@ejemplo.com                                       ║
║ Cliente:   María González                                          ║
║ Paquete:   Caribe Paradisíaco                                      ║
║ Destino:   Cancún                                                  ║
║ Monto:     $1,850.00                                               ║
║ Riesgo:    82.0%                                                   ║
╚════════════════════════════════════════════════════════════════════╝
```

### Modo Producción

Configura SMTP en `.env` para enviar emails reales.

## 🧪 Testing

### Script de Pruebas Automático

```bash
python scripts/test_api.py
```

### cURL (Linux/Mac/Git Bash)

```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "venta_id": "test001",
    "cliente_id": "cli001",
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
  }'
```

### PowerShell (Windows)

```powershell
$body = @{
    venta_id="test001"
    cliente_id="cli001"
    monto_total=1850.0
    es_temporada_alta=1
    dia_semana_reserva=2
    metodo_pago_tarjeta=0
    tiene_paquete=1
    duracion_dias=7
    destino_categoria=0
    total_compras_previas=3
    total_cancelaciones_previas=1
    tasa_cancelacion_historica=0.33
    monto_promedio_compras=1200.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/predict" -Method Post -Body $body -ContentType "application/json"
```

## 📈 Métricas del Modelo

```
Accuracy:  89.5%
Precision: 89.4%
Recall:    80.8%
F1-Score:  84.9%
```

**Matriz de Confusión:**
```
                  Predicho
                  0    1
Actual 0        123   4
       1         14  59
```

## 🔄 Versionamiento

| Versión | Features | MongoDB | Recordatorios | Cron | Accuracy | Estado |
|---------|----------|---------|---------------|------|----------|--------|
| v1.0 | 20 | ❌ | ❌ | ❌ | 66.5% | Obsoleto |
| v2.0 | 12 | ❌ | ❌ | ❌ | 62.0% | Obsoleto |
| v3.0 | 11 | ❌ | ❌ | ❌ | 89.5% | Funcional |
| **v4.0** | **11** | **✅** | **✅** | **✅** | **89.5%** | **ACTUAL** |

## 🤝 Integración con Spring Boot

Spring Boot debe enviar `PredictRequestFull`:

```java
@Service
public class IAService {
    
    private final RestTemplate restTemplate;
    
    public PredictResponse predecirCancelacion(Venta venta, Cliente cliente, PaqueteTuristico paquete) {
        String url = "http://localhost:8001/predict";
        
        // Calcular 11 features
        IAFeatureCalculator calculator = new IAFeatureCalculator();
        PredictRequestDTO request = calculator.calcularFeatures(venta, cliente.getId());
        
        // Añadir datos para MongoDB
        request.setEmailCliente(cliente.getEmail());
        request.setNombreCliente(cliente.getNombre() + " " + cliente.getApellidos());
        request.setNombrePaquete(paquete != null ? paquete.getNombre() : null);
        request.setDestino(paquete != null ? paquete.getDestinoPrincipal() : null);
        request.setFechaVenta(venta.getFechaVenta());
        
        return restTemplate.postForEntity(url, request, PredictResponse.class).getBody();
    }
}
```

## 🐛 Troubleshooting

### Error de conexión a MongoDB
```bash
pip install dnspython==2.4.2
```

### Modelo no encontrado
```bash
python scripts/train_model.py
```

### Puerto 8001 ocupado
```powershell
# Windows
taskkill /F /IM python.exe
```

## 📚 Documentación Adicional

- `guia_ia.md` - Guía original del proyecto
- `IMPLEMENTACION_V4_COMPLETA.md` - Cambios versión 4.0
- `/docs` - Swagger UI automática en http://localhost:8001/docs

## 👥 Autor

**Alan Fernando Rivera Loayza**  
Ingeniería de Software 2 - UAGRM 2025

## 📄 Licencia

Este proyecto es parte del curso de Ingeniería de Software 2.

---

🎉 **¡Microservicio listo para producción!** 🎉


```powershell
python scripts/train.py
```

**Output:**
- `app/ml/modelo.pkl` → Modelo entrenado con 12 features
- `app/ml/reporte_entrenamiento.txt` → Métricas del modelo (62% accuracy)

**Métricas actuales:**
- ✅ Accuracy: 66.5%
- ✅ Precision: 62.5%
- ✅ Recall: 57.5%
- ✅ F1-Score: 59.9%

### 5️⃣ Levantar el servidor

```powershell
python main.py
```

**El servidor estará corriendo en:** `http://localhost:8001`

### 6️⃣ Probar el API

```powershell
python scripts/test_api.py
```

O visita la documentación interactiva: **http://localhost:8001/docs**

---

## 📡 Endpoints disponibles

### 🏥 GET `/health` - Health Check

Verifica que el servicio esté funcionando.

**Response:**
```json
{
  "status": "healthy",
  "modelo_cargado": true,
  "version": "1.0.0"
}
```

---

### 🎯 POST `/predict` - Predicción de Cancelación

Realiza una predicción de cancelación.

**Request:**
```json
{
  "venta_id": "venta_001",
  "cliente_id": "cli_001",
  
  // Features de Venta (7)
  "monto_total": 1500.0,
  "es_temporada_alta": 1,
  "dia_semana_reserva": 2,
  "metodo_pago_tarjeta": 1,
  "tiene_paquete": 1,
  "duracion_dias": 7,
  "destino_categoria": 1,
  
  // Features de Cliente (5)
  "total_compras_previas": 3,
  "total_cancelaciones_previas": 1,
  "tasa_cancelacion_historica": 0.33,
  "monto_promedio_compras": 1200.0,
  "edad_cliente": 35
}
```

**Response:**
```json
{
  "success": true,
  "venta_id": "venta_001",
  "cliente_id": "cli_001",
  "probabilidad_cancelacion": 0.65,
  "recomendacion": "revisar_manual",
  "factores_riesgo": [
    "Alta tasa de cancelaciones previas",
    "Reserva con mucha anticipación"
  ]
}
```

**Recomendaciones posibles:**
- `sin_accion` → Probabilidad < 50%
- `revisar_manual` → Probabilidad 50% - 70%
- `enviar_recordatorio` → Probabilidad > 70%

---

## 📊 Features del modelo (12 en total)

> ⚠️ **CORREGIDO:** Originalmente el modelo usaba 20 features, pero 8 no existían en MongoDB.  
> El modelo fue actualizado para usar solo las 12 features disponibles.

### Features de Venta (7)
Estas se obtienen directamente de la colección `Venta` en MongoDB:

1. `monto_total` - Monto total de la venta
2. `es_temporada_alta` - Si es temporada alta (0/1)
3. `dia_semana_reserva` - Día de la semana (0=Lunes, 6=Domingo)
4. `metodo_pago_tarjeta` - Si pagó con tarjeta (0/1)
5. `tiene_paquete` - Si incluye paquete (0/1)
6. `duracion_dias` - Duración del viaje en días
7. `destino_categoria` - Categoría del destino (0/1/2)

### Features de Cliente (5)
Estas se calculan agregando el historial del cliente desde MongoDB:

8. `total_compras_previas` - Número total de compras anteriores
9. `total_cancelaciones_previas` - Número de cancelaciones previas
10. `tasa_cancelacion_historica` - Porcentaje de cancelaciones (calculado)
11. `monto_promedio_compras` - Promedio de montos de compras anteriores
12. `edad_cliente` - Edad del cliente

### ❌ Features eliminadas (no existen en MongoDB)
- `dias_anticipacion`, `hora_reserva`, `num_servicios`, `precio_por_dia`
- `monto_total_historico`, `dias_desde_ultima_compra`, `dias_desde_registro`, `frecuencia_compra_mensual`

Ver detalles completos en: [`CORRECCIONES_12_FEATURES.md`](CORRECCIONES_12_FEATURES.md)

---

## 🔗 Integración con Spring Boot

Spring Boot debe:
1. Consultar MongoDB para obtener datos de `Venta` y `Usuario`
2. Calcular las 5 features del cliente (agregando su historial de ventas)
3. Enviar las 12 features al endpoint `POST /predict`
4. Recibir la predicción y actuar según la recomendación

```java
@Service
public class IAService {
    
    private final RestTemplate restTemplate;
    private final String iaUrl = "http://localhost:8001";
    
    public PredictResponse predecirCancelacion(Venta venta, Usuario cliente) {
        String url = iaUrl + "/predict";
        
        // Construir request con las 12 features
        PredictRequest request = new PredictRequest();
        
        // Features de Venta (7) - Directas de MongoDB
        request.setVentaId(venta.getId());
        request.setClienteId(cliente.getId());
        request.setMontoTotal(venta.getMontoTotal());
        request.setEsTemporadaAlta(venta.esTemporadaAlta() ? 1 : 0);
        request.setDiaSemanaReserva(venta.getFechaVenta().getDayOfWeek().getValue() - 1);
        request.setMetodoPagoTarjeta(venta.usaTarjeta() ? 1 : 0);
        request.setTienePaquete(venta.tienePaquete() ? 1 : 0);
        request.setDuracionDias(venta.getDuracionDias());
        request.setDestinoCategoria(venta.getDestino().getCategoria());
        
        // Features de Cliente (5) - Calcular desde historial
        List<Venta> historial = ventaRepository.findByClienteIdAndEstadoCancelada(cliente.getId());
        request.setTotalComprasPrevias(historial.size());
        request.setTotalCancelacionesPrevias((int) historial.stream().filter(Venta::isCancelada).count());
        request.setTasaCancelacionHistorica(calcularTasaCancelacion(historial));
        request.setMontoPromedioCompras(calcularPromedioMontos(historial));
        request.setEdadCliente(cliente.getEdad());
        
        ResponseEntity<PredictResponse> response = 
            restTemplate.postForEntity(url, request, PredictResponse.class);
        
        return response.getBody();
    }
}
```

**¿Cuándo llamar al microservicio?**
- ✅ Cuando se crea una reserva nueva (estado: Pendiente)
- ✅ Cuando se actualiza una reserva
- ❌ NO cuando la reserva ya está confirmada o cancelada

---

## 📁 Estructura del proyecto

```
IA_predicción/
│
├── app/                          # Código de la API
│   ├── __init__.py
│   ├── schemas.py               # Pydantic models
│   ├── ml/
│   │   ├── modelo.pkl           # Modelo entrenado ✅
│   │   └── reporte_entrenamiento.txt
│   ├── routers/
│   │   └── __init__.py
│   └── services/
│       ├── __init__.py
│       └── predictor.py         # Lógica de predicción
│
├── data/                         # Datos
│   └── dataset_sintetico.csv    # Dataset generado ✅
│
├── scripts/                      # Scripts utilitarios
│   ├── generar_datos_sinteticos.py  # Genera dataset
│   ├── train.py                     # Entrena modelo
│   └── test_api.py                  # Prueba el API
│
├── venv/                         # Entorno virtual
│
├── main.py                       # Aplicación FastAPI ✅
├── requirements.txt              # Dependencias ✅
├── guia_ia.md                    # Documentación técnica
└── README.md                     # Este archivo
```

---

## 🧪 Pruebas realizadas

### ✅ Caso 1: ALTO RIESGO
- Cliente nuevo
- Sin pago confirmado
- Mucha anticipación (120 días)
- Monto alto ($2800)
- **Resultado:** 65.8% probabilidad → `revisar_manual`

### ✅ Caso 2: BAJO RIESGO
- Cliente frecuente (8 compras)
- Pago confirmado
- Poca anticipación (15 días)
- Sin cancelaciones previas
- **Resultado:** 21.2% probabilidad → `sin_accion`

### ✅ Caso 3: RIESGO MEDIO
- Cliente con historial mixto
- 2 cancelaciones de 4 compras
- Pago confirmado
- **Resultado:** 40.4% probabilidad → `sin_accion`

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Lenguaje | Python | 3.11 |
| Framework | FastAPI | 0.104.1 |
| Server | Uvicorn | 0.24.0 |
| ML Framework | scikit-learn | 1.3.2 |
| Data Processing | Pandas | 2.1.3 |
| Numerical | NumPy | 1.26.2 |
| Model Serialization | Joblib | 1.3.2 |

---

## 🔮 Próximos pasos

1. **Re-entrenar con datos reales**
   - Exportar ventas desde MongoDB
   - Incluir datos históricos reales
   - Mejorar el accuracy

2. **Agregar persistencia (PostgreSQL)**
   - Guardar predicciones
   - Tracking de precisión del modelo
   - Feedback loop

3. **Dockerizar**
   - Crear `Dockerfile`
   - Crear `docker-compose.yml`
   - Deploy en servidor

4. **Conectar con n8n**
   - Trigger automático al crear venta
   - Enviar notificación si prob > 70%

---

## 📚 Recursos útiles

- **Documentación interactiva:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc
- **Health check:** http://localhost:8001/health
- **Guía técnica:** `guia_ia.md`

---

## 💡 Notas importantes

- ⚠️ El modelo actual está entrenado con **datos sintéticos**
- ⚠️ La precisión mejorará con **datos reales**
- ✅ El microservicio está **listo para integrarse con Spring Boot**
- ✅ Los endpoints están **validados con Pydantic**
- ✅ El código es **simple y fácil de entender**

---

## 👨‍💻 Autor

**Desarrollo IA - Agencia de Viajes**  
Fecha: Noviembre 2025  
Versión: 1.0.0

---

**¿Dudas?** Revisa `guia_ia.md` para detalles técnicos completos.
