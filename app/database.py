"""
Conexión a MongoDB Atlas
Base de datos compartida con Spring Boot
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Cliente global de MongoDB
client = None
db = None


def connect_db():
    """Conecta a MongoDB Atlas"""
    global client, db
    
    try:
        uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("MONGODB_DATABASE", "agencia_viajes")
        
        if not uri:
            raise ValueError("❌ MONGODB_URI no configurado en .env")
        
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Verificar conexión
        client.admin.command('ping')
        
        db = client[database_name]
        
        logger.info(f"✅ MongoDB conectado: {database_name}")
        logger.info(f"✅ Colecciones disponibles: {db.list_collection_names()}")
        
        return db
        
    except Exception as e:
        logger.error(f"❌ Error conectando a MongoDB: {e}")
        raise


def get_db():
    """Obtiene la instancia de la base de datos"""
    global db
    
    if db is None:
        connect_db()
    
    return db


def close_db():
    """Cierra la conexión a MongoDB"""
    global client
    
    if client:
        client.close()
        logger.info("🔌 MongoDB desconectado")
