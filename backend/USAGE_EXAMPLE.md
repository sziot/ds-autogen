# Optimizer 调用 User_Proxy 工具函数 - 使用示例

## 核心机制说明

在 AutoGen 中，Optimizer 智能体需要通过消息指示 User_Proxy 调用工具函数。由于不同版本的 AutoGen API 可能不同，我们提供了多种实现方式。

## 方式1: 通过消息明确指示（推荐，兼容性最好）

这是最通用的方式，不依赖特定的 AutoGen API。

### Optimizer 的消息格式

```python
optimizer_message = """
我已经完成了代码修复。以下是修复后的代码：

```python
import sqlite3
from typing import Optional

def get_user_by_id(user_id: int) -> Optional[dict]:
    \"\"\"安全地获取用户信息\"\"\"
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        # ... 完整代码
    except Exception as e:
        print(f"Error: {e}")
        return None
```

请 User_Proxy 调用 save_fixed_code 工具保存上述代码：
- file_path: "example.py"
- fixed_code: [上面的完整代码]
- original_file_name: "example.py"
"""
```

### User_Proxy 的处理逻辑

User_Proxy 接收到消息后，需要：
1. 解析消息中的工具调用指示
2. 提取参数（file_path, fixed_code, original_file_name）
3. 手动调用 save_fixed_code 函数

### 实现代码

```python
def process_optimizer_message(message: str, user_proxy):
    """处理 Optimizer 的消息，提取工具调用并执行"""
    import re
    
    # 检查是否有工具调用指示
    if "save_fixed_code" in message or "调用" in message:
        # 提取代码块
        code_match = re.search(r'```python\n(.*?)\n```', message, re.DOTALL)
        if code_match:
            fixed_code = code_match.group(1)
            
            # 提取参数（可以从消息中解析，或使用默认值）
            file_path = "example.py"  # 从消息或上下文中获取
            original_file_name = "example.py"
            
            # 调用工具函数
            result = save_fixed_code(
                file_path=file_path,
                fixed_code=fixed_code,
                original_file_name=original_file_name
            )
            
            return result
    
    return None
```

## 方式2: 使用 AutoGen 的函数调用机制（如果支持）

如果 AutoGen 版本支持函数调用，可以这样实现：

```python
# 在创建 User_Proxy 时注册工具
user_proxy = UserProxyAgent(
    name="User_Proxy",
    functions=[save_fixed_code],  # 如果支持
    function_map={"save_fixed_code": save_fixed_code},  # 或者这种方式
)

# Optimizer 可以直接在消息中调用
optimizer_message = """
修复代码已完成。请调用 save_fixed_code(
    file_path="example.py",
    fixed_code="[代码内容]",
    original_file_name="example.py"
)
"""
```

## 方式3: 通过 GroupChat 实现协作

```python
from autogen import GroupChat, GroupChatManager

# 创建群组对话
groupchat = GroupChat(
    agents=[optimizer, user_proxy],
    messages=[],
    max_round=10,
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=optimizer.llm_config,
)

# 启动对话
result = user_proxy.initiate_chat(
    manager,
    message="请修复代码并保存...",
    max_turns=10,
)

# 从对话历史中提取工具调用结果
for msg in result.chat_history:
    if "save_fixed_code" in str(msg.get("content", "")):
        # 处理工具调用结果
        pass
```

## 实际实现建议

由于 AutoGen 的 API 在不同版本间可能有差异，建议：

1. **优先使用方式1**：通过消息明确指示，兼容性最好
2. **在 User_Proxy 的 system_message 中说明工具用法**
3. **在代码中实现消息解析逻辑**，自动提取工具调用参数
4. **添加错误处理和日志**，便于调试

## 完整示例

参考 `backend/autogen_reviewer.py` 中的 `CodeReviewSystem` 类实现，它展示了：
- 如何创建智能体
- 如何设置消息传递
- 如何从对话结果中提取工具调用信息

## 调试技巧

1. 打印对话历史，查看消息格式
2. 检查 User_Proxy 是否收到工具调用指示
3. 验证工具函数参数是否正确
4. 检查文件保存路径和权限

