# run.py
import json
from flask import Flask
from app.routes.chat import chat_bp
from app.routes.knowledge import knowledge_bp
from app.routes.index import index_bp  # 添加这行
from app.services.chat import ChatService
from modules.llm_wrapper import LLMWrapper
from modules.vector_store import VectorStore
from config.config import Config
from dotenv import load_dotenv
from app.services.knowledge import KnowledgeService 
import os

def init_app(app):
    """初始化应用"""
    try:
        # 创建必要的目录
        directories = [
            app.config['UPLOAD_FOLDER'],
            app.config['VECTOR_STORE_PATH'],
            os.path.join(app.root_path, 'data'),
            os.path.join(app.root_path, 'models')
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                print(f"Creating directory: {directory}")
                os.makedirs(directory, exist_ok=True)
                
        print("Application directories initialized successfully")
    except Exception as e:
        print(f"Error initializing application directories: {e}")
        raise

def create_app():

    # 加载环境变量
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化应用目录
    init_app(app)
    
    # 创建必要的目录
    # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # os.makedirs(app.config['VECTOR_STORE_PATH'], exist_ok=True)

    # 初始化分类文件
    categories_file = os.path.join(app.instance_path, 'data', 'categories.json')
    if not os.path.exists(categories_file):
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)

    
    
    # 初始化服务
    vector_store = VectorStore(Config)
    llm_wrapper = LLMWrapper(Config)

    app.vector_store = vector_store  # 添加这行
    
    app.chat_service = ChatService(Config, llm_wrapper, vector_store)

    # 添加这行
    app.knowledge_service = KnowledgeService(Config, vector_store)
    
    # 注册蓝图
    app.register_blueprint(index_bp)  # 注册根路由蓝图
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=8066, debug=True)