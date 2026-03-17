from enum import Enum
from datetime import datetime, timedelta
import logging
from typing import Callable, Any, Optional

# 设置日志
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"      # 正常状态，正常调用主函数
    OPEN = "open"         # 熔断状态，调用备用函数
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复

class CircuitBreaker:
    """三状态熔断器实现"""
    
    def __init__(self, 
                 failure_threshold: int = 3,
                 recovery_timeout: int = 60,
                 half_open_success_threshold: int = 1):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 触发熔断的失败次数
            recovery_timeout: OPEN状态持续时间（秒）
            half_open_success_threshold: 半开状态下成功次数达到此值则恢复
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_success_threshold = half_open_success_threshold
        
        # 状态相关属性
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_success_count = 0
        
        # 备用函数
        self.fallback_func = None
        
    def call(self, primary_func: Callable, fallback_func: Callable, *args, **kwargs) -> Any:
        """
        执行函数并根据状态决定调用主函数还是备用函数
        
        Args:
            primary_func: 主函数
            fallback_func: 备用函数
            *args, **kwargs: 传递给函数的参数
            
        Returns:
            函数执行结果
        """
        try:
            # 根据当前状态决定调用哪个函数
            if self.state == CircuitState.CLOSED:
                # 正常状态，调用主函数
                result = primary_func(*args, **kwargs)
                self._on_success()
                return result
                
            elif self.state == CircuitState.OPEN:
                # 熔断状态，调用备用函数
                logger.info("[熔断器] 当前状态: OPEN，调用备用函数")
                result = fallback_func(*args, **kwargs)
                self._check_recovery()
                return result
                
            elif self.state == CircuitState.HALF_OPEN:
                # 半开状态，尝试调用主函数
                try:
                    result = primary_func(*args, **kwargs)
                    self._on_half_open_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    logger.info("[熔断器] 半开状态调用失败，切换到OPEN")
                    result = fallback_func(*args, **kwargs)
                    return result
                    
        except Exception as e:
            self._on_failure()
            if self.state == CircuitState.CLOSED:
                # 正常状态下失败，调用备用函数
                logger.info("[熔断器] 正常状态调用失败，切换到OPEN")
                return fallback_func(*args, **kwargs)
            elif self.state == CircuitState.HALF_OPEN:
                # 半开状态下失败，切换到OPEN
                logger.info("[熔断器] 半开状态调用失败，切换到OPEN")
                return fallback_func(*args, **kwargs)
            else:
                # OPEN状态下已经调用备用函数，直接返回
                return fallback_func(*args, **kwargs)
    
    def _on_success(self):
        """成功时的处理"""
        if self.state == CircuitState.CLOSED:
            # 正常状态，重置失败计数
            self.failure_count = 0
        elif self.state == CircuitState.HALF_OPEN:
            # 半开状态，增加成功计数
            self.half_open_success_count += 1
            if self.half_open_success_count >= self.half_open_success_threshold:
                self.state = CircuitState.CLOSED
                self.half_open_success_count = 0
                logger.info("[熔断器] 状态转换: HALF_OPEN → CLOSED")
    
    def _on_failure(self):
        """失败时的处理"""
        if self.state == CircuitState.CLOSED:
            # 正常状态，增加失败计数
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = datetime.now()
                logger.info(f"[熔断器] 状态转换: CLOSED → OPEN (失败次数: {self.failure_count})")
        elif self.state == CircuitState.HALF_OPEN:
            # 半开状态，失败则切换到OPEN
            self.state = CircuitState.OPEN
            self.last_failure_time = datetime.now()
            logger.info("[熔断器] 状态转换: HALF_OPEN → OPEN")
    
    def _check_recovery(self):
        """检查是否应该从OPEN状态恢复"""
        if self.state == CircuitState.OPEN and self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            if elapsed >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_success_count = 0
                logger.info(f"[熔断器] 状态转换: OPEN → HALF_OPEN (已等待 {elapsed:.1f} 秒)")
    
    def _on_half_open_success(self):
        """半开状态成功时的处理"""
        self.half_open_success_count += 1
        if self.half_open_success_count >= self.half_open_success_threshold:
            self.state = CircuitState.CLOSED
            self.half_open_success_count = 0
            logger.info("[熔断器] 状态转换: HALF_OPEN → CLOSED")
    
    def reset(self):
        """重置熔断器状态"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_success_count = 0
        logger.info("[熔断器] 状态重置为CLOSED")
    
    def get_state_info(self) -> dict:
        """获取当前状态信息"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "half_open_success_count": self.half_open_success_count
        }