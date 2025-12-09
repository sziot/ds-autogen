"""
Optimizer 调用 User_Proxy 工具函数的示例代码

这个文件展示了 Optimizer 智能体如何指示 User_Proxy 调用 save_fixed_code 工具
"""

# ============================================================================
# 方式1: 通过消息明确指示（推荐）
# ============================================================================

# Optimizer 在生成修复代码后，发送以下格式的消息给 User_Proxy:

optimizer_message_to_user_proxy = """
我已经完成了代码修复。以下是修复说明和修复后的代码：

## 修复说明
1. 修复了SQL注入漏洞，使用参数化查询
2. 添加了错误处理机制
3. 优化了代码结构，提高了可读性

## 综合质量评分
85/100

## 修复后的代码
```python
import sqlite3
from typing import Optional

def get_user_by_id(user_id: int) -> Optional[dict]:
    \"\"\"安全地获取用户信息\"\"\"
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # 使用参数化查询防止SQL注入
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'email': result[2]
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
```

## 工具调用
请 User_Proxy 执行以下工具调用以保存修复后的代码：

**调用 save_fixed_code 工具**
- file_path: "example.py"
- fixed_code: [上面的完整代码内容]
- original_file_name: "example.py"
"""

# ============================================================================
# 方式2: 使用 AutoGen 的函数调用机制
# ============================================================================

# 如果 AutoGen 支持函数调用，Optimizer 可以直接调用：

from autogen import ConversableAgent

# Optimizer 的 system_message 中应该包含工具描述
optimizer_system_message_with_tools = """
你是一名代码优化专家。

可用工具：
- save_fixed_code(file_path: str, fixed_code: str, original_file_name: str): 保存修复后的代码

当你完成代码修复后，直接调用 save_fixed_code 工具。
"""

# Optimizer 在回复中可以直接使用函数调用格式：
optimizer_function_call = {
    "function": "save_fixed_code",
    "arguments": {
        "file_path": "example.py",
        "fixed_code": "import sqlite3\n\ndef get_user_by_id(user_id: int):\n    ...",
        "original_file_name": "example.py"
    }
}

# ============================================================================
# 方式3: 通过 GroupChat 实现（实际实现方式）
# ============================================================================

from autogen import GroupChat, GroupChatManager
from tools import save_fixed_code

def setup_optimizer_with_tools():
    """设置 Optimizer 和 User_Proxy 的协作"""
    
    # 创建 User_Proxy 并注册工具
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config=False,
    )
    
    # 注册工具函数
    user_proxy.register_function(
        function_map={
            "save_fixed_code": save_fixed_code,
        }
    )
    
    # 创建 Optimizer
    optimizer = ConversableAgent(
        name="Optimizer",
        system_message="""你负责生成修复后的代码，然后指示 User_Proxy 调用 save_fixed_code 工具。
        
        格式示例：
        1. 生成修复代码
        2. 在消息中明确说明：请 User_Proxy 调用 save_fixed_code(file_path="...", fixed_code="...", original_file_name="...")
        """,
        llm_config={...},
    )
    
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
    # Optimizer 会生成修复代码，然后指示 User_Proxy 调用工具
    result = user_proxy.initiate_chat(
        manager,
        message="请修复以下代码并保存...",
        max_turns=10,
    )
    
    return result


# ============================================================================
# 方式4: 消息格式示例（实际使用）
# ============================================================================

# Optimizer 发送给 User_Proxy 的完整消息格式：

complete_optimizer_message = """
## 代码修复完成

我已经根据 Architect 和 Reviewer 的报告完成了代码修复。

### 修复内容：
1. 修复了3个安全漏洞
2. 改进了代码结构
3. 添加了类型注解
4. 优化了错误处理

### 综合质量评分：88/100

### 修复后的完整代码：

```python
# 修复后的代码内容
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
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'email': result[2]
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
```

### 请执行工具调用

User_Proxy，请调用 save_fixed_code 工具保存上述修复后的代码：

**工具名称**: save_fixed_code
**参数**:
- file_path: "example.py"
- fixed_code: [上面的完整Python代码]
- original_file_name: "example.py"

请确认保存结果。
"""

# ============================================================================
# 关键点总结
# ============================================================================

"""
1. Optimizer 必须在消息中明确指示 User_Proxy 调用工具
2. 工具参数必须完整且准确
3. fixed_code 必须是完整的、可运行的代码
4. User_Proxy 接收到指示后会自动调用注册的工具函数
5. 工具执行结果会返回给 Optimizer 或记录在对话历史中
"""

