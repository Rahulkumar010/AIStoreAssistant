import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Config:
    # SQL Server
    SERVER_NAME = os.environ.get('SERVER_NAME')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')
    USERNAME = os.environ.get('SQL_USERNAME')
    PASSWORD = os.environ.get('SQL_PASSWORD')
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY', '')
    AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    # Azure OpenAI Deployments
    AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT')
    AZURE_OPENAI_MODEL = os.environ.get('AZURE_OPENAI_MODEL')
    AZURE_EMBEDDING_MODEL = os.environ.get('AZURE_EMBEDDING_MODEL')
    
    # Vector DB
    CHROMA_DB_DIR = os.environ.get('CHROMA_DB_DIR')

    # Serp API
    SERP_API_KEY = os.environ.get('SERP_API_KEY')
    
    # File upload settings
    UPLOAD_DIR = Path(__file__).parent / 'uploads'
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv'}
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    @classmethod
    def is_azure_configured(cls):
        return bool(cls.AZURE_OPENAI_ENDPOINT and cls.AZURE_OPENAI_API_KEY)
    
    @classmethod
    def is_serpapi_configured(cls):
        return bool(cls.SERP_API_KEY)

config = Config()

# Create upload directory if it doesn't exist
config.UPLOAD_DIR.mkdir(exist_ok=True)
