from typing import List, Dict, Any, Callable
import inspect

class FunctionManager:
    def __init__(self):
        self.functions: Dict[str, Callable] = {}
        self.function_descriptions: Dict[str, str] = {}

    def register_function(self, 
                        func: Callable, 
                        description: str = None):
        """注册新的function"""
        func_name = func.__name__
        self.functions[func_name] = func
        self.function_descriptions[func_name] = description or inspect.getdoc(func)

    def get_function_descriptions(self) -> List[Dict[str, Any]]:
        """获取所有注册的function描述"""
        return [
            {
                "name": name,
                "description": desc,
                "parameters": inspect.signature(func).parameters
            }
            for name, (func, desc) in self.functions.items()
        ]

    def call_function(self, 
                     func_name: str, 
                     **kwargs) -> Any:
        """调用指定的function"""
        if func_name not in self.functions:
            raise ValueError(f"Function {func_name} not found")
        return self.functions[func_name](**kwargs)