# modules/llm_wrapper.py
from zhipuai import ZhipuAI
from typing import List, Dict, Optional
import json
import asyncio

class LLMWrapper:
    def __init__(self, config):
        self.config = config
        self.client = ZhipuAI(api_key=config.ZHIPU_API_KEY)
        
    def chat_completion(
        self, 
        messages: List[Dict],
        functions: Optional[List[Dict]] = None,
        temperature: float = None
    ) -> Dict:
        """同步调用智谱AI GLM-4-Flash进行对话"""
        try:
            temperature = temperature or self.config.TEMPERATURE
            
            if functions:
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    functions=functions,
                    temperature=temperature,
                    max_tokens=self.config.MAX_TOKENS,
                )
            else:
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=self.config.MAX_TOKENS,
                )
            
            return {
                'choices': [{
                    'message': {
                        'content': response.choices[0].message.content,
                        'role': response.choices[0].message.role,
                    }
                }],
                'usage': {
                    'completion_tokens': response.usage.completion_tokens,
                    'prompt_tokens': response.usage.prompt_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return {"error": str(e)}

    async def stream_chat_completion(
        self,
        messages: List[Dict],
        functions: Optional[List[Dict]] = None,
        temperature: float = None
    ):
        """异步流式调用智谱AI GLM-4-Flash进行对话"""
        try:
            temperature = temperature or self.config.TEMPERATURE
            
            if functions:
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    functions=functions,
                    temperature=temperature,
                    max_tokens=self.config.MAX_TOKENS,
                    stream=True  # 启用流式输出
                )
            else:
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=self.config.MAX_TOKENS,
                    stream=True  # 启用流式输出
                )
            
            # 处理流式响应
            for chunk in response:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield {
                        'choices': [{
                            'delta': {
                                'content': delta.content,
                                'role': 'assistant'
                            },
                            'finish_reason': chunk.choices[0].finish_reason
                        }]
                    }
                
        except Exception as e:
            print(f"Error in stream chat completion: {e}")
            yield {"error": str(e)}