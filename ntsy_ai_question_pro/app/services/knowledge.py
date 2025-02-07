# app/services/knowledge.py

import os
from typing import List, Dict
from werkzeug.utils import secure_filename
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import markdown

class KnowledgeService:
    def __init__(self, config, vector_store):
        self.config = config
        self.vector_store = vector_store
    
    def _get_file_extension(self, filename: str) -> str:
        """
        获取文件扩展名（处理大小写和带点的情况）
        """
        # 分割文件名和扩展名
        _, ext = os.path.splitext(filename.lower())
        # 如果扩展名以点开头，去掉点
        return ext[1:] if ext.startswith('.') else ext

    def create_knowledge_base(self, name: str) -> bool:
        """创建新的知识库"""
        try:
            # 使用 vector_store 创建集合
            success = self.vector_store.create_collection(name)
            if success:
                print(f"Successfully created knowledge base: {name}")
            else:
                print(f"Failed to create knowledge base: {name}")
            return success
        except Exception as e:
            print(f"Error in create_knowledge_base: {e}")
            return False

    def _read_file(self, file_path: str, original_filename: str) -> List[str]:
        """
        读取不同格式的文件内容
        
        Args:
            file_path: 文件的实际路径
            original_filename: 原始文件名（用于确定文件类型）
        """
        try:
            # 使用原始文件名来确定文件类型
            ext = self._get_file_extension(original_filename)
            print(f"Processing file type: {ext}")

            if ext == 'txt':
                try:
                    encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read().strip()
                                return [content] if content else [""]
                        except UnicodeDecodeError:
                            continue
                    raise UnicodeDecodeError(f"Could not read file with any of the encodings: {encodings}")
                except UnicodeDecodeError as e:
                    print(f"Error reading file {file_path}: {str(e)}")
                    raise
            elif ext == 'pdf':
                try:
                    print(f"Reading PDF file: {file_path}")
                    reader = PdfReader(file_path)
                    texts = []
                    for i, page in enumerate(reader.pages):
                        try:
                            text = page.extract_text()
                            if text and text.strip():
                                texts.append(text.strip())
                            print(f"Extracted text from page {i+1}")
                        except Exception as page_error:
                            print(f"Error extracting text from page {i+1}: {str(page_error)}")
                    return texts if texts else [""]
                except Exception as pdf_error:
                    print(f"Error reading PDF file: {str(pdf_error)}")
                    raise

            elif ext == 'docx':
                try:
                    doc = Document(file_path)
                    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                    text = '\n'.join(paragraphs)
                    return [text] if text.strip() else [""]
                except Exception as e:
                    print(f"Error reading DOCX file: {str(e)}")
                    raise

            elif ext in ['xlsx', 'xls']:
                try:
                    df = pd.read_excel(file_path)
                    if df.empty:
                        return [""]
                    text = df.fillna('').to_string(index=False)
                    return [text] if text.strip() else [""]
                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise

            elif ext == 'md':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        html = markdown.markdown(content)
                        return [html] if html.strip() else [""]
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                        html = markdown.markdown(content)
                        return [html] if html.strip() else [""]

            else:
                print(f"Unsupported file type: {ext}")
                raise ValueError(f"Unsupported file type: {ext}")

        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            raise


    async def process_files(self, knowledge_base: str, files: List[Dict]) -> Dict:
        """
        处理上传的文件并添加到知识库
        """
        results = {"success": [], "failed": []}
        
        try:
            if knowledge_base not in self.vector_store.vector_stores:
                raise ValueError(f"Knowledge base '{knowledge_base}' does not exist")

            for file_info in files:
                filename = file_info.get('filename')
                file_path = file_info.get('path')
                
                if not filename or not file_path:
                    print(f"Invalid file info: {file_info}")
                    results["failed"].append(filename or "Unknown file")
                    continue
                    
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    results["failed"].append(filename)
                    continue

                print(f"Processing file: {filename}")
                print(f"File path: {file_path}")

                try:
                    # 读取文件内容，传入原始文件名用于确定文件类型
                    texts = self._read_file(file_path, filename)
                    
                    if not texts:
                        print(f"No content extracted from file: {filename}")
                        results["failed"].append(filename)
                        continue

                    # 准备元数据
                    metadata = {
                        "filename": filename,
                        "source": os.path.basename(file_path),
                        "type": self._get_file_extension(filename)
                    }

                    # 添加到向量存储
                    success = self.vector_store.add_texts(
                        collection_name=knowledge_base,
                        texts=texts,
                        metadatas=[metadata] * len(texts)
                    )

                    if success:
                        results["success"].append(filename)
                        print(f"Successfully processed file: {filename}")
                    else:
                        results["failed"].append(filename)
                        print(f"Failed to add texts for file: {filename}")

                except Exception as e:
                    print(f"Error processing file {filename}: {str(e)}")
                    results["failed"].append(filename)
                    continue

        except Exception as e:
            print(f"Error in process_files: {str(e)}")
            raise

        finally:
            print(f"Processing complete. Success: {len(results['success'])}, Failed: {len(results['failed'])}")
            return results