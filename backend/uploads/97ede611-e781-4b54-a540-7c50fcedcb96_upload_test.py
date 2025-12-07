"""
代码审查系统测试文件
包含：安全漏洞、架构问题、性能问题、代码规范问题
"""

import os
import sqlite3
import subprocess
import pickle
from typing import List, Dict, Any

# ==================== 安全漏洞部分 ====================

class UserService:
    """用户服务类 - 包含多种安全漏洞"""
    
    def __init__(self):
        # ❌ 硬编码数据库连接信息
        self.db_path = "/var/data/users.db"
        self.admin_password = "Admin@123456"  # 硬编码密码
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息 - SQL注入漏洞"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ❌ 高危：SQL注入漏洞（直接拼接用户输入）
        query = f"SELECT * FROM users WHERE id = '{user_id}'"
        cursor.execute(query)
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else {}
    
    def backup_database(self, backup_name: str) -> bool:
        """备份数据库 - 命令注入漏洞"""
        # ❌ 高危：命令注入（直接执行用户输入）
        command = f"/usr/bin/backup_script.sh {backup_name}"
        result = subprocess.call(command, shell=True)  # shell=True 更危险！
        return result == 0
    
    def load_user_data(self, serialized_data: bytes) -> Any:
        """加载用户数据 - 不安全的反序列化"""
        # ❌ 高危：pickle反序列化可能执行任意代码
        return pickle.loads(serialized_data)
    
    def read_config_file(self, filename: str) -> str:
        """读取配置文件 - 路径遍历漏洞"""
        # ❌ 中危：可能读取系统敏感文件
        config_path = f"/config/{filename}"
        with open(config_path, 'r') as f:
            return f.read()


# ==================== 架构问题部分 ====================

class GodClass:
    """
    上帝类 - 违反单一职责原则
    这个类做了太多事情，应该拆分成多个类
    """
    
    def __init__(self):
        self.users = []
        self.products = []
        self.orders = []
        self.logs = []
        self.cache = {}
        self.config = {}
    
    # 用户管理相关方法
    def add_user(self, user): pass
    def delete_user(self, user_id): pass
    def update_user(self, user): pass
    def find_user(self, user_id): pass
    def validate_user(self, user): pass
    
    # 产品管理相关方法
    def add_product(self, product): pass
    def remove_product(self, product_id): pass
    def update_product(self, product): pass
    def get_product(self, product_id): pass
    def validate_product(self, product): pass
    
    # 订单管理相关方法
    def create_order(self, order): pass
    def cancel_order(self, order_id): pass
    def process_order(self, order): pass
    def refund_order(self, order_id): pass
    def track_order(self, order_id): pass
    
    # 日志相关方法
    def log_info(self, message): pass
    def log_error(self, message): pass
    def log_debug(self, message): pass
    def get_logs(self, date): pass
    def clear_old_logs(self): pass
    
    # 配置管理相关方法
    def load_config(self): pass
    def save_config(self): pass
    def get_config_value(self, key): pass
    def set_config_value(self, key, value): pass
    
    # 缓存管理相关方法
    def set_cache(self, key, value): pass
    def get_cache(self, key): pass
    def clear_cache(self): pass
    def cache_stats(self): pass
    
    # ... 这个类已经超过50行，还在继续增加方法


# ==================== 性能问题部分 ====================

def find_duplicates_slow(data: List[int]) -> List[int]:
    """查找重复元素 - O(n²)低效算法"""
    duplicates = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])
    return duplicates


def process_large_file_inefficient(filename: str) -> int:
    """处理大文件 - 内存效率低下"""
    # ❌ 一次性读取整个文件到内存
    with open(filename, 'r') as file:
        lines = file.readlines()  # 如果文件很大，会耗尽内存
    
    total = 0
    for line in lines:
        total += len(line.strip())
    
    return total


def fibonacci_inefficient(n: int) -> int:
    """计算斐波那契数 - 指数级时间复杂度"""
    if n <= 1:
        return n
    # ❌ 递归重复计算，O(2^n)时间复杂度
    return fibonacci_inefficient(n - 1) + fibonacci_inefficient(n - 2)


# ==================== 代码规范问题部分 ====================

def badly_formatted_function (  param1,param2,param3):
    """糟糕的格式：空格不一致、括号位置不对"""
    result=param1+param2*param3
    if result>100:
        print("结果太大")
    else:
        print("结果正常")
    return result


def confusing_naming():
    """令人困惑的命名"""
    a = 10  # a代表什么？
    b = 20  # b代表什么？
    c = a + b  # c代表什么？
    
    x1 = "data"  # x1是什么数据？
    x2 = "info"  # x2是什么信息？
    
    return c  # 返回的是什么？


# ==================== 错误处理问题部分 ====================

def divide_numbers(a: float, b: float) -> float:
    """除法函数 - 错误处理不完整"""
    # ❌ 只检查了除零错误，没有处理其他异常
    if b == 0:
        return 0  # 静默失败，应该抛出异常
    return a / b


def read_config():
    """读取配置 - 异常被吞没"""
    try:
        with open('config.json', 'r') as f:
            config = f.read()
            # 复杂处理...
            return config
    except Exception as e:
        # ❌ 吞没异常，没有日志，没有重新抛出
        return None


# ==================== 测试用例部分 ====================

def test_security_vulnerabilities():
    """测试安全漏洞检测"""
    service = UserService()
    
    # 测试SQL注入
    print("Testing SQL injection...")
    # 恶意输入：user_id = "1' OR '1'='1"
    result = service.get_user_info("1' OR '1'='1")
    print(f"Result: {result}")
    
    # 测试命令注入
    print("\nTesting command injection...")
    # 恶意输入：backup_name = "test; rm -rf /"
    success = service.backup_database("test; rm -rf /")
    print(f"Backup success: {success}")
    
    return True


def test_performance_issues():
    """测试性能问题"""
    print("\nTesting performance issues...")
    
    # 测试低效算法
    data = [1, 2, 3, 4, 5, 1, 2, 3]
    duplicates = find_duplicates_slow(data)
    print(f"Duplicates: {duplicates}")
    
    # 测试递归效率
    print("Calculating Fibonacci(10)...")
    fib_result = fibonacci_inefficient(10)
    print(f"Fibonacci(10) = {fib_result}")
    
    return True


def test_code_quality():
    """测试代码质量问题"""
    print("\nTesting code quality...")
    
    # 测试糟糕的格式
    result = badly_formatted_function(10, 20, 30)
    print(f"Badly formatted function result: {result}")
    
    # 测试令人困惑的命名
    confusing_result = confusing_naming()
    print(f"Confusing naming result: {confusing_result}")
    
    # 测试错误处理
    division_result = divide_numbers(10, 0)
    print(f"Division by zero result: {division_result}")
    
    return True


# ==================== 主程序 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("DeepSeek 代码审查系统 - 测试文件")
    print("=" * 60)
    print("本文件包含多种代码问题，用于测试AI代码审查能力")
    print()
    
    # 运行测试
    print("🔍 开始代码审查测试...")
    print()
    
    test_security_vulnerabilities()
    test_performance_issues()
    test_code_quality()
    
    print()
    print("=" * 60)
    print("测试完成！请查看AI生成的审查报告")
    print("预期AI应该发现：")
    print("1. ✅ SQL注入漏洞")
    print("2. ✅ 命令注入漏洞")
    print("3. ✅ 硬编码密码")
    print("4. ✅ 上帝类（违反单一职责）")
    print("5. ✅ 低效算法（O(n²)复杂度）")
    print("6. ✅ 代码格式问题")
    print("7. ✅ 命名不规范")
    print("8. ✅ 错误处理不完整")
    print("=" * 60)


if __name__ == "__main__":
    main()