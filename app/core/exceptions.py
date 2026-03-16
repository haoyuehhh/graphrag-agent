from fastapi import HTTPException
from starlette import status

class LLMTimeoutException(HTTPException):
    def __init__(self, detail: str = "LLM 请求超时"):
        super().__init__(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=detail)

class GraphNotReadyException(HTTPException):
    def __init__(self, detail: str = "知识图谱未就绪"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)

class CircuitBreakerOpenException(HTTPException):
    def __init__(self, detail: str = "服务暂时不可用，请稍后再试"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)