# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "Survey Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configuración de Ollama
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_TEMPERATURE: float = 0.7
    
    # Configuración de rutas
    BASE_DIR: Path = Path(__file__).resolve().parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    
    # Configuración de la encuesta
    QUESTIONS_PER_PAGE: int = 5
    
    # Categorías de preguntas
    QUESTION_CATEGORIES: dict = {
        "Usabilidad": [0, 1, 2, 3, 4],
        "Rendimiento": [5, 6, 7],
        "Diseño": [8, 9, 10, 11],
        "Satisfacción": [12, 13, 14, 15]
    }
    
    # Lista de preguntas
    QUESTIONS: list = [
        "El programa es fácil de usar.",
        "La interfaz es clara y comprensible.",
        "Las instrucciones son suficientes.",
        "La navegación es intuitiva.",
        "La funcionalidad satisface mis necesidades.",
        "El programa responde rápidamente.",
        "El programa tiene las características esperadas.",
        "Los errores son mínimos o inexistentes.",
        "La interfaz es visualmente atractiva.",
        "El uso de colores es apropiado.",
        "La tipografía es legible.",
        "El diseño general es moderno.",
        "Recomendaría este programa a otros.",
        "Estoy satisfecho con mi experiencia general.",
        "Es probable que vuelva a usar este programa.",
        "El programa agrega valor a mis actividades."
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de las configuraciones
    """
    return Settings()

# Instancia global de configuración
settings = get_settings()