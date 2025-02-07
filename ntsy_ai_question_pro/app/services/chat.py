# app/services/chat.py

from typing import List, Dict, Optional
import json

class ChatService:
    def __init__(self, config, llm_wrapper, vector_store):
        self.config = config
        self.llm = llm_wrapper
        self.vector_store = vector_store
        
    def _format_knowledge_context(self, knowledge_docs: List[Dict]) -> str:
        """格式化知识库上下文"""
        context = "根据以下参考资料：\n\n"
        for i, doc in enumerate(knowledge_docs, 1):
            context += f"{i}. {doc['content']}\n\n"
        return context.strip()
        
    def chat(
        self,
        query: str,
        history: List[Dict],
        knowledge_base: Optional[str] = None,
        functions: Optional[List[Dict]] = None
    ) -> Dict:
        """处理聊天请求"""
        try:
            messages = []
            
            # 如果启用了知识库
            if knowledge_base:
                # 搜索相关文档
                docs = self.vector_store.similarity_search(knowledge_base, query)
                if docs:
                    context = self._format_knowledge_context(docs)
                    system_prompt = f"""你是一个专业的AI助手。请基于以下参考资料回答用户的问题。
                    如果问题无法从参考资料中得到答案，请说明这一点。
                    
                    {context}"""
                    
                    messages.append({"role": "system", "content": system_prompt})
                
            # 添加历史对话
            messages.extend(history[-self.config.CHAT_HISTORY_MAX_TURNS:])
            
            # 添加当前问题
            messages.append({"role": "user", "content": query})
            
            # 调用LLM
            response = self.llm.chat_completion(
                messages=messages,
                functions=functions
            )
            
            # 检查是否有错误
            if "error" in response:
                return response
                
            # 构造返回结果
            return {
                "response": response['choices'][0]['message']['content'],
                "history": messages + [response['choices'][0]['message']],
                "usage": response['usage']
            }
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return {"error": str(e)}
    
    async def stream_chat(self, query: str, history: List[Dict], knowledge_base: Optional[str] = None):
        try:
            messages = []
            
            # 如果启用了知识库
            if knowledge_base:
                docs = self.vector_store.similarity_search(knowledge_base, query)
                if docs:
                    context = self._format_knowledge_context(docs)
                    system_prompt = f"""你是一个专业的AI助手。请基于以下参考资料回答用户的问题。
                    如果问题无法从参考资料中得到答案，请说明这一点。
                    
                    {context}"""
                    messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史对话
            messages.extend(history[-self.config.CHAT_HISTORY_MAX_TURNS:])
            messages.append({"role": "user", "content": query})
            
            # 使用流式输出
            async for chunk in self.llm.stream_chat_completion(messages=messages):
                if "error" in chunk:
                    yield {"error": chunk["error"]}
                    return
                
                if "choices" in chunk and chunk["choices"]:
                    content = chunk["choices"][0]["delta"].get("content", "")
                    if content:
                        yield {
                            "type": "content",
                            "content": content,
                            "done": False
                        }
            
            # 发送完成标记
            yield {
                "type": "content",
                "content": "",
                "done": True
            }
            
        except Exception as e:
            print(f"Error in stream_chat: {e}")
            yield {"error": str(e)}