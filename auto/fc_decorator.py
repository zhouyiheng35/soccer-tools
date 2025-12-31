# fc_decorator.py
FC_REGISTRY = {}

def fc(func=None, *, name=None):
    """
    装饰器：注册工具到 FC_REGISTRY
    """
    def wrapper(f):
        tool_name = name or f.__name__
        FC_REGISTRY[tool_name] = f
        return f
    return wrapper(func) if func else wrapper
