# # modules/knowledge_base.py
# import os
# import json
# import time
# from typing import List, Dict
# from pathlib import Path
# from config.config import Config
# from modules.file_processor import FileProcessor
# from modules.vector_store import VectorStore

# class KnowledgeBase:
#     def __init__(self):
#         self.base_path = Config.VECTOR_STORE_PATH
#         self.base_path.mkdir(exist_ok=True)
#         self.metadata_file = self.base_path / "metadata.json"
#         self.categories_file = self.base_path / "categories.json"
#         self.file_processor = FileProcessor()
#         self.vector_store = VectorStore()
#         self._init_metadata_files()

#     def _init_metadata_files(self):
#         """初始化元数据文件"""
#         if not self.metadata_file.exists():
#             self._save_metadata({})
#         if not self.categories_file.exists():
#             self._save_categories([])

#     def _save_metadata(self, data: Dict):
#         """保存知识库元数据"""
#         with open(self.metadata_file, 'w', encoding='utf-8') as f:
#             json.dump(data, f, ensure_ascii=False, indent=2)

#     def _load_metadata(self) -> Dict:
#         """加载知识库元数据"""
#         with open(self.metadata_file, 'r', encoding='utf-8') as f:
#             return json.load(f)

#     def _save_categories(self, categories: List):
#         """保存分类数据"""
#         with open(self.categories_file, 'w', encoding='utf-8') as f:
#             json.dump(categories, f, ensure_ascii=False, indent=2)

#     def _load_categories(self) -> List:
#         """加载分类数据"""
#         with open(self.categories_file, 'r', encoding='utf-8') as f:
#             return json.load(f)

#     def create_category(self, name: str) -> Dict:
#         """创建新的知识库分类"""
#         categories = self._load_categories()
#         category_id = str(int(time.time()))
#         new_category = {
#             "id": category_id,
#             "name": name,
#             "created_at": int(time.time())
#         }
#         categories.append(new_category)
#         self._save_categories(categories)
#         return new_category

#     def get_categories(self) -> List[Dict]:
#         """获取所有分类"""
#         return self._load_categories()

#     def create_knowledge_base(self, name: str, category_id: str = "") -> Dict:
#         """创建新的知识库"""
#         metadata = self._load_metadata()
#         if name in metadata:
#             raise ValueError(f"Knowledge base '{name}' already exists")

#         kb_path = self.base_path / name
#         kb_path.mkdir(exist_ok=True)

#         metadata[name] = {
#             "name": name,
#             "created_at": int(time.time()),
#             "document_count": 0,
#             "category_id": category_id
#         }
#         self._save_metadata(metadata)
#         return metadata[name]

#     def delete_knowledge_base(self, name: str):
#         """删除知识库"""
#         metadata = self._load_metadata()
#         if name not in metadata:
#             raise ValueError(f"Knowledge base '{name}' not found")

#         kb_path = self.base_path / name
#         if kb_path.exists():
#             import shutil
#             shutil.rmtree(kb_path)

#         del metadata[name]
#         self._save_metadata(metadata)

#     def get_knowledge_base_info(self, name: str) -> Dict:
#         """获取知识库信息"""
#         metadata = self._load_metadata()
#         if name not in metadata:
#             raise ValueError(f"Knowledge base '{name}' not found")
#         return metadata[name]

#     def list_knowledge_bases(self, category_id: str = "") -> List[Dict]:
#         """列出所有知识库"""
#         metadata = self._load_metadata()
#         if category_id:
#             return [kb for kb in metadata.values() if kb.get("category_id") == category_id]
#         return list(metadata.values())

#     async def upload_files(self, name: str, files: List) -> Dict:
#         """上传文件到知识库"""
#         metadata = self._load_metadata()
#         if name not in metadata:
#             raise ValueError(f"Knowledge base '{name}' not found")

#         kb_path = self.base_path / name
#         kb_path.mkdir(exist_ok=True)

#         processed_files = []
#         for file in files:
#             # 处理和保存文件
#             filename = file.filename
#             file_path = kb_path / filename
#             await file.save(file_path)

#             # 处理文件内容
#             try:
#                 texts = self.file_processor.process_file(file_path)
#                 # 将文本转换为向量并存储
#                 self.vector_store.add_texts(texts, metadata={"source": filename})
#                 processed_files.append(filename)
                
#                 # 更新文档计数
#                 metadata[name]["document_count"] += 1
#             except Exception as e:
#                 if file_path.exists():
#                     file_path.unlink()
#                 raise Exception(f"Error processing file {filename}: {str(e)}")

#         self._save_metadata(metadata)
#         return {
#             "success": True,
#             "processed_files": processed_files,
#             "knowledge_base": metadata[name]
#         }