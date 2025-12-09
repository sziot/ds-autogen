"""
计算模块示例 - 修复版本

此模块提供了一个安全的数值计算框架，包含输入验证、错误处理和日志记录功能。
采用模块化设计，便于扩展和维护。

架构说明：
- 配置层：Config 类负责配置管理
- 服务层：CalculatorService 类提供核心计算服务
- 工具层：ValidationUtils 提供验证工具
- 应用层：main() 函数作为应用入口
"""

import logging
from typing import Union, Optional
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class Config:
    """配置管理类"""
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    max_value: float = 1e6
    min_value: float = -1e6
    
    def validate(self) -> bool:
        """验证配置有效性"""
        if self.max_value <= self.min_value:
            raise ValueError("max_value 必须大于 min_value")
        return True


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_number(value: Union[int, float], config: Config) -> bool:
        """
        验证数值是否在有效范围内
        
        Args:
            value: 要验证的数值
            config: 配置对象
            
        Returns:
            bool: 验证是否通过
            
        Raises:
            ValueError: 当数值超出允许范围时
            TypeError: 当输入不是数值类型时
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"输入必须是数值类型，得到 {type(value).__name__}")
        
        if not (config.min_value <= value <= config.max_value):
            raise ValueError(
                f"数值 {value} 超出允许范围 [{config.min_value}, {config.max_value}]"
            )
        
        return True


class CalculatorService:
    """计算服务类"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化计算服务
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or Config()
        self.config.validate()
        self._setup_logging()
        self.validator = ValidationUtils()
        
    def _setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=self.config.log_level.value,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=self.config.log_file,
            filemode='a' if self.config.log_file else None
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("CalculatorService 初始化完成")
    
    def calculate_sum(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        计算两个数的和
        
        Args:
            a: 第一个加数
            b: 第二个加数
            
        Returns:
            float: 两个数的和
            
        Raises:
            ValueError: 当输入超出允许范围时
            TypeError: 当输入不是数值类型时
            
        Example:
            >>> calculator = CalculatorService()
            >>> calculator.calculate_sum(10, 20)
            30.0
        """
        try:
            # 验证输入
            self.validator.validate_number(a, self.config)
            self.validator.validate_number(b, self.config)
            
            # 执行计算
            result = float(a + b)
            
            # 验证结果
            self.validator.validate_number(result, self.config)
            
            self.logger.debug(f"计算 {a} + {b} = {result}")
            return result
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"计算失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            raise RuntimeError(f"计算过程中发生未知错误: {e}")


def main():
    """主函数 - 应用入口点"""
    try:
        # 配置应用
        config = Config(
            log_level=LogLevel.INFO,
            log_file="calculator.log",
            max_value=1000000,
            min_value=-1000000
        )
        
        # 创建计算服务
        calculator = CalculatorService(config)
        
        # 测试数据
        test_cases = [
            (10, 20),
            (3.14, 2.86),
            (-5, 10),
            (0, 0)
        ]
        
        # 执行计算
        for i, (num1, num2) in enumerate(test_cases, 1):
            try:
                total = calculator.calculate_sum(num1, num2)
                print(f"测试用例 {i}: {num1} + {num2} = {total}")
            except Exception as e:
                print(f"测试用例 {i} 失败: {e}")
        
        print("所有计算完成！")
        
    except Exception as e:
        print(f"应用启动失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())