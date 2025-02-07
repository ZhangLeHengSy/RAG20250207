# config/config.py

import os
from pathlib import Path

class Config:
    # 基础配置
    # BASE_DIR = Path(__file__).parent.parent
    # UPLOAD_FOLDER = BASE_DIR / "uploads"
    # VECTOR_STORE_PATH = BASE_DIR / "vector_store"
    # 使用绝对路径
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    VECTOR_STORE_PATH = os.path.join(BASE_DIR, 'vector_store')
    EMBEDDING_MODEL = os.path.join(BASE_DIR, 'models', 'text2vec-base-chinese')
    EMBEDDING_DEVICE = 'cpu'
    
    # 模型配置
    # MODEL_DIR = BASE_DIR / "models"
    # EMBEDDING_MODEL = str(MODEL_DIR / "text2vec-base-chinese")  # 使用完整路径
    # EMBEDDING_DEVICE = "cpu"
    
    # 智谱AI配置
    # ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_API_KEY = "0e435a624d187cba6c49f6fc471b9a48.UBvUOWCwWLh9WPz1"
    print(f"ZHIPU_API_KEY: {ZHIPU_API_KEY}")
    
    # 文档处理配置
    SUPPORTED_EXTENSIONS = {
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'md': 'text/markdown'
    }
    
    # Embedding 模型配置
    EMBEDDING_MODEL = "text2vec-base-chinese"
    EMBEDDING_DEVICE = "cpu"
    
    # 向量数据库配置
    VECTOR_DB_TYPE = "faiss"  # 或者其他支持的向量数据库
    
    # Chat配置
    CHAT_HISTORY_MAX_TURNS = 10
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000

    @classmethod
    def print_paths(cls):
        print(f"BASE_DIR: {cls.BASE_DIR}")
        # print(f"MODEL_DIR: {cls.MODEL_DIR}")
        print(f"EMBEDDING_MODEL: {cls.EMBEDDING_MODEL}")