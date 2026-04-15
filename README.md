# AI智能伴侣

一个基于 Streamlit + DeepSeek 的 AI 聊天应用，支持自定义人设、多会话管理、对话记忆和记录导出。

## 功能特性

### 核心功能
- **实时对话**：流式输出，AI 回复逐字显示
- **角色定制**：自定义 AI 昵称和性格描述
- **多会话管理**：新建、切换、删除会话，历史自动保存
- **SQLite 存储**：数据持久化到本地数据库

### 新增功能

#### 🎭 角色预设模板
内置 8 种性格模板，一键切换：
- 🌸 温柔体贴、🧊 理性冷静、😄 幽默风趣、💼 成熟稳重
- 📚 知性优雅、🔥 热情奔放、🎯 毒舌傲娇、🌙 神秘高冷

#### 🧠 智能记忆
- AI 自动从对话中提取你的喜好、习惯、个人情况
- 记忆跨会话持久化，所有对话都能调用
- 最多保留 20 条记忆，自动去重
- 可手动清空

#### 📄 记录导出
- **TXT 格式**：便于阅读，带会话信息和时间戳
- **JSON 格式**：结构化数据，便于程序处理

## 技术栈

- **前端**：Streamlit（Web 界面）
- **AI 模型**：DeepSeek API（deepseek-chat）
- **数据存储**：SQLite（本地数据库）
- **SDK**：OpenAI Python SDK

## 快速开始

### 1. 安装依赖

```bash
pip install streamlit openai
```

### 2. 配置 API Key

注册 [DeepSeek](https://platform.deepseek.com/) 获取 API Key，然后设置环境变量：

```powershell
# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-xxxxxxxx"

# Linux / macOS
export DEEPSEEK_API_KEY="sk-xxxxxxxx"
```

或者用 `python-dotenv`，创建 `.env` 文件：
```
DEEPSEEK_API_KEY=sk-xxxxxxxx
```

### 3. 运行

```bash
cd ai
streamlit run AI智能伴侣.py
```

浏览器会自动打开 `http://localhost:8501`

## 使用说明

### 聊天
底部输入框打字发送，AI 回复会实时流式输出。

### 修改人设
侧边栏"伴侣信息"区域：
- **角色模板**：下拉选择 8 种预设性格
- **伴侣昵称**：自定义 AI 名字
- **伴侣性格**：手动编辑性格描述（模板可覆盖）

### 会话管理
- **新建会话**：点击"✏️ 新建会话"，当前会话自动保存
- **加载历史**：侧边栏"历史会话"列表，点击切换
- **删除会话**：点击会话旁边的 🗑️ 图标

### 记忆功能
AI 会在每次对话后自动提取关键信息（你的喜好、习惯等），显示在侧边栏"记忆功能"区域。这些记忆在所有会话中共享，AI 会根据记忆调整回复风格。

### 导出记录
侧边栏底部"导出聊天记录"，支持 TXT 和 JSON 两种格式。

## 项目结构

```
ai/
├── AI智能伴侣.py          # 主程序
├── sessions.db            # SQLite 数据库（运行后自动生成）
├── resources/
│   └── logo.png          # 应用图标
├── sessions_b/           # 旧版 JSON 备份
└── *.py                  # 学习/测试文件
```

## 数据库结构

```sql
CREATE TABLE sessions (
    session_name TEXT PRIMARY KEY,     -- 会话名（时间戳）
    nick_name TEXT NOT NULL,           -- AI 昵称
    nature TEXT NOT NULL,              -- 性格描述
    messages TEXT NOT NULL,            -- 聊天记录（JSON）
    memories TEXT DEFAULT '[]',        -- 用户记忆（JSON）
    created_at TIMESTAMP               -- 创建时间
)
```

## 核心函数

| 函数 | 功能 |
|------|------|
| `init_db()` | 初始化数据库，创建表 |
| `save_session()` | 保存当前会话到数据库 |
| `load_sessions()` | 获取所有会话列表 |
| `load_session(name)` | 加载指定会话 |
| `delete_session(name)` | 删除指定会话 |
| `extract_memories()` | 调用 AI 提取用户记忆 |
| `merge_memories()` | 合并去重记忆列表 |
| `export_as_txt()` | 导出 TXT 格式记录 |
| `export_as_json()` | 导出 JSON 格式记录 |

## Session State

| 状态变量 | 说明 |
|----------|------|
| `messages` | 当前会话的聊天记录 |
| `nick_name` | AI 昵称 |
| `nature` | AI 性格描述 |
| `memories` | 用户记忆列表（跨会话共享） |
| `current_session` | 当前会话名称 |

## 优化记录

- 程序启动时初始化数据库，避免重复调用
- 移除冗余的会话存在性检查，直接使用 `INSERT OR REPLACE`
- 列表推导式简化数据提取逻辑
- 记忆提取错误改用控制台输出，不打断用户

## 注意事项

1. **API Key 安全**：不要把 API Key 提交到代码仓库
2. **数据备份**：定期备份 `sessions.db`，防止聊天记录丢失
3. **网络依赖**：需要联网调用 DeepSeek API
4. **API 费用**：DeepSeek 按用量计费，注意控制调用频率

## 常见问题

**Q: 报错说找不到模块？**  
A: `pip install streamlit openai` 安装依赖

**Q: 发了消息没反应？**  
A: 检查 API Key 是否正确设置

**Q: 切换会话时闪退/报错？**  
A: 如果是旧版本升级，删除 `sessions.db` 重新生成（旧表结构缺少 `memories` 字段）

**Q: 记忆功能不生效？**  
A: 检查 AI 返回的 JSON 格式是否正确，错误信息会打印到控制台

## 许可证

个人学习使用，禁止商用。

---

有问题欢迎提 issue。
