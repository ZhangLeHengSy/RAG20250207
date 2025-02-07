# # modules/file_processor.py
# import os
# from typing import List
# from pathlib import Path
# from config.config import Config
# import pypdf
# import docx
# import pandas as pd

# class FileProcessor:
#     def __init__(self):
#         self.supported_extensions = Config.SUPPORTED_EXTENSIONS

#     def process_file(self, file_path: Path) -> List[str]:
#         """处理不同类型的文件并返回文本内容"""
#         extension = file_path.suffix.lower()[1:]  # 移除点号
        
#         if extension not in self.supported_extensions:
#             raise ValueError(f"Unsupported file type: {extension}")

#         if extension == 'txt':
#             return self._process_txt(file_path)
#         elif extension == 'pdf':
#             return self._process_pdf(file_path)
#         elif extension == 'docx':
#             return self._process_docx(file_path)
#         elif extension == 'xlsx':
#             return self._process_xlsx(file_path)
#         elif extension == 'md':
#             return self._process_markdown(file_path)
#         else:
#             raise ValueError(f"Unsupported file type: {extension}")

#     def _process_txt(self, file_path: Path) -> List[str]:
#         """处理文本文件"""
#         with open(file_path, 'r', encoding='utf-8') as f:
#             text = f.read()
#         return self._split_text(text)

#     def _process_pdf(self, file_path: Path) -> List[str]:
#         """处理PDF文件"""
#         texts = []
#         with open(file_path, 'rb') as f:
#             pdf = pypdf.PdfReader(f)
#             for page in pdf.pages:
#                 text = page.extract_text()
#                 if text.strip():
#                     texts.extend(self._split_text(text))
#         return texts

#     def _process_docx(self, file_path: Path) -> List[str]:
#         """处理Word文件"""
#         doc = docx.Document(file_path)
#         texts = []
#         for paragraph in doc.paragraphs:
#             text = paragraph.text.strip()
#             if text:
#                 texts.extend(self._split_text(text))
#         return texts

#     def _process_xlsx(self, file_path: Path) -> List[str]:
#         """处理Excel文件"""
#         texts = []
#         df = pd.read_excel(file_path)
#         for column in df.columns:
#             texts.append(f"{column}:")
#             for value in df[column].dropna():
#                 if str(value).strip():
#                     texts.extend(self._split_text(str(value)))
#         return texts

#     def _process_markdown(self, file_path: Path) -> List[str]:
#         """处理Markdown文件"""
#         with open(file_path, 'r', encoding='utf-8') as f:
#             text = f.read()
#         return self._split_text(text)

#     def _split_text(self, text: str, max_length: int = 500) -> List[str]:
#         """将长文本分割成小段落"""
#         paragraphs = text.split('\n')
#         results = []
#         current_chunk = ""
        
#         for paragraph in paragraphs:
#             paragraph = paragraph.strip()
#             if not paragraph:
#                 continue
                
#             if len(current_chunk) + len(paragraph) + 1 <= max_length:
#                 current_chunk += ("\n" + paragraph if current_chunk else paragraph)
#             else:
#                 if current_chunk:
#                     results.append(current_chunk)
#                 current_chunk = paragraph

#         if current_chunk:
#             results.append(current_chunk)
            
#         return results