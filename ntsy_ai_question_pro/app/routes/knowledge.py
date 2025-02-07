# app/routes/knowledge.py
import json
import logging
from pathlib import Path
from fastapi import logger
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 修改蓝图定义
knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/knowledge')

# 分类数据文件路径
CATEGORIES_FILE = Path('data/categories.json')

def get_categories_file_path():
    """获取分类文件路径"""
    return os.path.join(current_app.instance_path, 'data', 'categories.json')

def load_categories():
    """加载分类数据"""
    categories_file = get_categories_file_path()
    if os.path.exists(categories_file):
        try:
            with open(categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in categories file: {categories_file}")
            return []
        except Exception as e:
            logger.error(f"Error loading categories: {str(e)}")
            return []
    return []

def save_categories(categories):
    """保存分类数据"""
    categories_file = get_categories_file_path()
    try:
        os.makedirs(os.path.dirname(categories_file), exist_ok=True)
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving categories: {str(e)}")
        return False

@knowledge_bp.route('/')
def index():
    return render_template('knowledge.html')

# 添加获取分类列表的路由
@knowledge_bp.route('/api/knowledge/categories')
def list_categories():
    """获取所有分类"""
    try:
        categories = load_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 添加创建分类的路由
@knowledge_bp.route('/api/knowledge/categories/create', methods=['POST'])
def create_category():
    """创建新分类"""
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Category name is required"}), 400
            
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Category name cannot be empty"}), 400
            
        categories = load_categories()
        
        # 检查分类名是否已存在
        if any(category['name'] == name for category in categories):
            return jsonify({"error": "Category already exists"}), 400
            
        # 创建新分类
        new_category = {
            "id": str(len(categories) + 1),
            "name": name
        }
        
        categories.append(new_category)
        save_categories(categories)
        
        return jsonify(new_category)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 添加删除分类的路由
@knowledge_bp.route('/api/knowledge/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除分类"""
    try:
        categories = load_categories()
        categories = [cat for cat in categories if cat['id'] != category_id]
        save_categories(categories)
        return jsonify({"message": "Category deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@knowledge_bp.route('/api/knowledge/list')
def list_knowledge_bases():
    # 从向量存储中获取知识库列表
    bases = list(current_app.vector_store.vector_stores.keys())
    return jsonify([{"name": base} for base in bases])

@knowledge_bp.route('/api/knowledge/create', methods=['POST'])
async def create_knowledge_base():
    """创建知识库"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Knowledge base name is required"}), 400
            
        name = data['name'].strip()
        if not name:
            return jsonify({"error": "Knowledge base name cannot be empty"}), 400
        
        # 检查目录权限
        vector_store_path = current_app.config['VECTOR_STORE_PATH']
        logger.info(f"Checking vector store path: {vector_store_path}")
        if not os.path.exists(vector_store_path):
            os.makedirs(vector_store_path, exist_ok=True)
            logger.info(f"Created vector store directory: {vector_store_path}")
            
        # 检查目录是否可写
        if not os.access(vector_store_path, os.W_OK):
            logger.error(f"Directory not writable: {vector_store_path}")
            return jsonify({"error": "Vector store directory is not writable"}), 500
            
        # 创建知识库
        logger.info(f"Creating knowledge base: {name}")
        success = current_app.knowledge_service.create_knowledge_base(name)
        
        if success:
            logger.info(f"Successfully created knowledge base: {name}")
            return jsonify({"message": f"Knowledge base '{name}' created successfully"})
        else:
            logger.error(f"Failed to create knowledge base: {name}")
            return jsonify({"error": "Failed to create knowledge base"}), 500
            
    except Exception as e:
        logger.exception(f"Error creating knowledge base: {str(e)}")
        return jsonify({"error": str(e)}), 500

@knowledge_bp.route('/api/knowledge/upload', methods=['POST'])
async def upload_files():
    try:
        knowledge_base = request.form.get('knowledge_base')
        if not knowledge_base:
            return jsonify({"error": "Knowledge base name is required"}), 400
            
        if 'files[]' not in request.files:
            return jsonify({"error": "No files provided"}), 400
            
        files = request.files.getlist('files[]')
        file_data = []
        
        # 确保上传目录存在
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        try:
            # 处理上传的文件
            for file in files:
                if file and file.filename:
                    try:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(upload_folder, filename)
                        
                        # 保存文件
                        file.save(file_path)
                        print(f"Saved file to: {file_path}")
                        
                        file_data.append({
                            "filename": filename,
                            "path": file_path
                        })
                    except Exception as save_error:
                        print(f"Error saving file {file.filename}: {str(save_error)}")
                        return jsonify({
                            "error": f"Error saving file {file.filename}: {str(save_error)}"
                        }), 500

            # 处理文件内容
            try:
                results = await current_app.knowledge_service.process_files(knowledge_base, file_data)
                return jsonify(results)
            except Exception as process_error:
                print(f"Error processing files: {str(process_error)}")
                return jsonify({
                    "error": f"Error processing files: {str(process_error)}"
                }), 500

        finally:
            # 清理临时文件
            for file_info in file_data:
                try:
                    path = file_info.get('path')
                    if path and os.path.exists(path):
                        os.remove(path)
                        print(f"Removed temporary file: {path}")
                except Exception as e:
                    print(f"Error removing temporary file: {str(e)}")
            
    except Exception as e:
        print(f"Unexpected error in upload_files: {str(e)}")
        return jsonify({"error": str(e)}), 500

@knowledge_bp.route('/api/knowledge/delete', methods=['POST'])
async def delete_knowledge_base():
    """删除知识库"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Knowledge base name is required"}), 400
        
    try:
        if name in current_app.vector_store.vector_stores:
            del current_app.vector_store.vector_stores[name]
            # 删除向量存储文件
            storage_path = os.path.join(current_app.config['VECTOR_STORE_PATH'], name)
            if os.path.exists(storage_path):
                import shutil
                shutil.rmtree(storage_path)
            return jsonify({"message": f"Knowledge base '{name}' deleted successfully"})
        else:
            return jsonify({"error": "Knowledge base not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@knowledge_bp.route('/api/knowledge/<name>/info')
def get_knowledge_base_info(name):
    """获取知识库信息"""
    try:
        if name in current_app.vector_store.vector_stores:
            store = current_app.vector_store.vector_stores[name]
            return jsonify({
                "name": name,
                "document_count": len(store.index_to_docstore_id),
                "created_at": os.path.getctime(os.path.join(current_app.config['VECTOR_STORE_PATH'], name))
            })
        else:
            return jsonify({"error": "Knowledge base not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500