import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

def async_retry(max_attempts: int = 3, base_delay: float = 1.0):
    """
    异步重试装饰器
    """
    def decorator(func):
        @retry(stop=stop_after_attempt(max_attempts), wait=wait_exponential(multiplier=base_delay))
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator