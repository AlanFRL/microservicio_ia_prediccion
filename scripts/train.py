"""
Script para entrenar el modelo de predicción de cancelaciones

VERSIÓN CORREGIDA: Solo 12 features reales disponibles en MongoDB

Este script:
1. Carga el dataset sintético (12 features)
2. Prepara los datos (train/test split)
3. Entrena un Random Forest Classifier
4. Evalúa el modelo
5. Guarda el modelo entrenado (.pkl)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
from datetime import datetime
import os

# Crear directorio para modelos si no existe
os.makedirs('app/ml', exist_ok=True)


def cargar_dataset(ruta='data/dataset_sintetico.csv'):
    """Carga el dataset desde CSV"""
    print(f"📂 Cargando dataset desde: {ruta}")
    df = pd.read_csv(ruta)
    print(f"✅ Dataset cargado: {len(df)} registros, {len(df.columns)} columnas")
    return df


def preparar_datos(df, test_size=0.2):
    """
    Separa features y target, y divide en train/test
    
    Args:
        df: DataFrame con los datos (12 features + 1 target)
        test_size: Proporción del test set (default 20%)
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    print(f"\n🔄 Preparando datos para entrenamiento...")
    
    # Separar features (X) y target (y)
    X = df.drop('fue_cancelada', axis=1)
    y = df['fue_cancelada']
    
    print(f"   • Total de features: {X.shape[1]} (12 features reales)")
    print(f"   • Features: {list(X.columns)}")
    print(f"   • Distribución del target:")
    print(f"     - Canceladas: {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
    print(f"     - No canceladas: {len(y) - y.sum()} ({(len(y)-y.sum())/len(y)*100:.1f}%)")
    
    # Dividir en train y test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=42,
        stratify=y  # Mantener proporción de clases
    )
    
    print(f"   • Train set: {len(X_train)} registros")
    print(f"   • Test set: {len(X_test)} registros")
    
    return X_train, X_test, y_train, y_test


def entrenar_modelo(X_train, y_train):
    """
    Entrena un Random Forest Classifier
    
    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
    
    Returns:
        modelo entrenado
    """
    print(f"\n🤖 Entrenando Random Forest Classifier...")
    
    # Configuración del modelo
    modelo = RandomForestClassifier(
        n_estimators=100,        # 100 árboles
        max_depth=10,            # Profundidad máxima
        min_samples_split=10,    # Mínimo para dividir nodo
        min_samples_leaf=5,      # Mínimo en hoja
        random_state=42,
        class_weight='balanced', # Importante: balancear clases
        n_jobs=-1                # Usar todos los cores
    )
    
    # Entrenar
    modelo.fit(X_train, y_train)
    
    print(f"✅ Modelo entrenado exitosamente")
    
    return modelo


def evaluar_modelo(modelo, X_train, X_test, y_train, y_test):
    """
    Evalúa el modelo en train y test sets
    
    Args:
        modelo: Modelo entrenado
        X_train, X_test: Features
        y_train, y_test: Targets
    
    Returns:
        dict con métricas
    """
    print(f"\n📊 Evaluando modelo...\n")
    
    # Predicciones
    y_pred_train = modelo.predict(X_train)
    y_pred_test = modelo.predict(X_test)
    
    # Métricas en TRAIN
    print("="*60)
    print("📈 MÉTRICAS EN TRAIN SET")
    print("="*60)
    acc_train = accuracy_score(y_train, y_pred_train)
    prec_train = precision_score(y_train, y_pred_train)
    rec_train = recall_score(y_train, y_pred_train)
    f1_train = f1_score(y_train, y_pred_train)
    
    print(f"Accuracy:  {acc_train:.4f} ({acc_train*100:.2f}%)")
    print(f"Precision: {prec_train:.4f} ({prec_train*100:.2f}%)")
    print(f"Recall:    {rec_train:.4f} ({rec_train*100:.2f}%)")
    print(f"F1-Score:  {f1_train:.4f} ({f1_train*100:.2f}%)")
    
    # Métricas en TEST
    print("\n" + "="*60)
    print("📈 MÉTRICAS EN TEST SET (LO QUE REALMENTE IMPORTA)")
    print("="*60)
    acc_test = accuracy_score(y_test, y_pred_test)
    prec_test = precision_score(y_test, y_pred_test)
    rec_test = recall_score(y_test, y_pred_test)
    f1_test = f1_score(y_test, y_pred_test)
    
    print(f"Accuracy:  {acc_test:.4f} ({acc_test*100:.2f}%)")
    print(f"Precision: {prec_test:.4f} ({prec_test*100:.2f}%)")
    print(f"Recall:    {rec_test:.4f} ({rec_test*100:.2f}%)")
    print(f"F1-Score:  {f1_test:.4f} ({f1_test*100:.2f}%)")
    
    # Matriz de confusión
    print("\n" + "="*60)
    print("📊 MATRIZ DE CONFUSIÓN (TEST SET)")
    print("="*60)
    cm = confusion_matrix(y_test, y_pred_test)
    print(f"\n                  Predicho")
    print(f"                No Cancel  Cancelada")
    print(f"Real No Cancel      {cm[0,0]:3d}        {cm[0,1]:3d}")
    print(f"Real Cancelada      {cm[1,0]:3d}        {cm[1,1]:3d}")
    
    # Interpretación
    print("\n" + "="*60)
    print("💡 INTERPRETACIÓN")
    print("="*60)
    print(f"• Verdaderos Negativos (TN): {cm[0,0]} - Correctamente predijo NO cancelación")
    print(f"• Falsos Positivos (FP): {cm[0,1]} - Predijo cancelación pero NO canceló")
    print(f"• Falsos Negativos (FN): {cm[1,0]} - Predijo NO cancelación pero SÍ canceló")
    print(f"• Verdaderos Positivos (TP): {cm[1,1]} - Correctamente predijo cancelación")
    
    # ¿El modelo es bueno?
    print("\n" + "="*60)
    print("✅ CONCLUSIÓN")
    print("="*60)
    
    if acc_test >= 0.75 and f1_test >= 0.70:
        print("🎉 ¡EXCELENTE! El modelo tiene buen desempeño")
    elif acc_test >= 0.65:
        print("👍 ACEPTABLE. El modelo funciona decentemente")
    else:
        print("⚠️ MEJORABLE. Considerar más datos o ajustar hiperparámetros")
    
    print(f"\nPrecision {prec_test*100:.1f}%: De las que predice como canceladas, {prec_test*100:.1f}% realmente lo son")
    print(f"Recall {rec_test*100:.1f}%: De las que realmente cancelan, detecta {rec_test*100:.1f}%")
    
    # Retornar métricas
    metricas = {
        'accuracy': acc_test,
        'precision': prec_test,
        'recall': rec_test,
        'f1_score': f1_test,
        'confusion_matrix': cm.tolist()
    }
    
    return metricas


def mostrar_feature_importance(modelo, feature_names):
    """Muestra las features más importantes del modelo"""
    print("\n" + "="*60)
    print("🔍 IMPORTANCIA DE FEATURES (Top 10)")
    print("="*60)
    
    importances = modelo.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    
    for i, idx in enumerate(indices, 1):
        print(f"{i:2d}. {feature_names[idx]:30s} {importances[idx]:.4f}")
    
    print("\n💡 Estas features son las que más influyen en la predicción")


def guardar_modelo(modelo, ruta='app/ml/modelo.pkl'):
    """Guarda el modelo entrenado"""
    joblib.dump(modelo, ruta)
    print(f"\n💾 Modelo guardado en: {ruta}")


def guardar_reporte(metricas, ruta='app/ml/reporte_entrenamiento.txt'):
    """Guarda un reporte del entrenamiento"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("REPORTE DE ENTRENAMIENTO - MODELO PREDICCIÓN CANCELACIONES\n")
        f.write("="*60 + "\n\n")
        f.write(f"Fecha: {timestamp}\n")
        f.write(f"Modelo: Random Forest Classifier\n\n")
        f.write("MÉTRICAS:\n")
        f.write(f"  • Accuracy:  {metricas['accuracy']:.4f}\n")
        f.write(f"  • Precision: {metricas['precision']:.4f}\n")
        f.write(f"  • Recall:    {metricas['recall']:.4f}\n")
        f.write(f"  • F1-Score:  {metricas['f1_score']:.4f}\n\n")
        f.write("Matriz de Confusión:\n")
        f.write(f"  {metricas['confusion_matrix']}\n")
    
    print(f"📄 Reporte guardado en: {ruta}")


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🚀 ENTRENAMIENTO DEL MODELO DE PREDICCIÓN DE CANCELACIONES")
    print("="*60 + "\n")
    
    # 1. Cargar dataset
    df = cargar_dataset()
    
    # 2. Preparar datos
    X_train, X_test, y_train, y_test = preparar_datos(df, test_size=0.2)
    
    # 3. Entrenar modelo
    modelo = entrenar_modelo(X_train, y_train)
    
    # 4. Evaluar modelo
    metricas = evaluar_modelo(modelo, X_train, X_test, y_train, y_test)
    
    # 5. Feature importance
    mostrar_feature_importance(modelo, X_train.columns.tolist())
    
    # 6. Guardar modelo
    guardar_modelo(modelo)
    
    # 7. Guardar reporte
    guardar_reporte(metricas)
    
    print("\n" + "="*60)
    print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print("\n🎯 Siguiente paso: Crear la API FastAPI para hacer predicciones\n")


if __name__ == "__main__":
    main()
