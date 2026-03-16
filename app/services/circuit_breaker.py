import asyncio
from functools import wraps
from app.core.config import settings
from app.core.exceptions import CircuitBreakerOpenException

class CircuitBreaker:
    def __init__(self):
        self.fail_count = 0
        self.last_failure_time = None
        self.is_open = False
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.is_open:
                raise CircuitBreakerOpenException()
            
            try:
                result = await func(*args, **kwargs)
                self.fail_count = 0
                self.is_open = False
                return result
            except Exception as e:
                self.fail_count += 1
                self.last_failure_time = asyncio.get_event_loop().time()
                
                if self.fail_count >= settings.circuit_breaker_threshold:
                    self.is_open = True
                    # 熔断超时后自动重置
                    asyncio.get_event_loop().call_later(
                        settings.circuit_breaker_timeout,
                        self._reset
                    )
                
                raise e
        
        return wrapper
    
    def _reset(self):
        self.fail_count = 0
        self.is_open = False

# 创建全局熔断器实例
circuit_breaker = CircuitBreaker()