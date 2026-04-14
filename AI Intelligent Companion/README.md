# AI智能伴侣

用 Streamlit + DeepSeek 做的一个聊天应用，可以自定义 AI 的性格和昵称，对话记录会自动保存。

## 能做什么

- 和 AI 聊天，支持流式输出（不用等它说完才显示）
- 给 AI 起名字、设定性格
- 多个会话切换，历史记录自动保存
- 数据存在 SQLite 数据库里

## 用的技术

- Streamlit（做界面的）
- DeepSeek API（AI 模型）
- SQLite（存数据）
- OpenAI Python SDK（调 API 用的）

## 安装

```bash
pip install streamlit openai
```

## 配置 API Key

先去 [DeepSeek 官网](https://platform.deepseek.com/) 注册个账号，拿到 API Key。

然后设置环境变量：

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="你的key"

# Linux/Mac
export DEEPSEEK_API_KEY="你的key"
```

也可以装个 `python-dotenv`，在项目里放个 `.env` 文件。

## 运行

```bash
cd ai
streamlit run AI智能伴侣.py
```

跑起来后浏览器会自动打开，一般是 `http://localhost:8501`

## 怎么用

### 聊天

直接在底部输入框打字，回车或者点发送就行。AI 的回复会一个字一个字蹦出来。

### 改 AI 的人设

左边侧边栏有个"伴侣信息"，可以改：
- **昵称**：你想叫它什么（默认叫"小美"）
- **性格**：描述一下它的性格，比如"活泼开朗"、"温柔体贴"之类的

### 管理会话

**新建会话**：点侧边栏上面的"✏️ 新建会话"，当前的对话会自动保存，然后开个新的。

**加载历史**：侧边栏"历史会话"下面列出了所有聊过的会话，点名字就能加载。当前会话是蓝色的。

**删除会话**：点会话名旁边的 🗑️ 图标就删了。

### 数据存在哪

所有聊天记录都存在 `sessions.db` 这个文件里（SQLite 数据库）。

表结构长这样：
```sql
CREATE TABLE sessions (
    session_name TEXT PRIMARY KEY,  -- 会话名，用时间戳命名
    nick_name TEXT NOT NULL,        -- AI 昵称
    nature TEXT NOT NULL,           -- 性格描述
    messages TEXT NOT NULL,         -- 聊天记录（JSON 字符串）
    created_at TIMESTAMP            -- 创建时间
)
```

## 项目结构

```
ai/
├── AI智能伴侣.py              # 主程序
├── resources/                  # 图片啥的
│   ├── logo.png               # Logo
│   └── ...
├── sessions.db                # 数据库（运行后自动生成）
├── 01. deepseek调用测试.py    # 测试 API 的
├── 02. json模块入门.py        # 学习 JSON 用的
├── 02. streamlit入门.py       # 学习 Streamlit 用的
└── sessions/                  # 老版本的 JSON 存储（不用了）
```

## 关于系统提示词

代码里写了挺长一段 system prompt，主要规定了 AI 应该怎么聊天：

- 要主动关心人，记住之前聊过的内容
- 情绪低落时先共情，别急着给建议
- 说话像朋友一样自然，别太正式
- 可以适当用 emoji
- 别装医生律师，遇到严重问题建议找专业人士

想改的话直接改代码里的 `system_prompt` 变量就行。

## 代码说明

几个主要的函数：

- `init_db()` - 初始化数据库，建表
- `save_session()` - 把当前对话存到数据库
- `load_sessions()` - 读取所有会话列表
- `load_session(name)` - 加载某个会话
- `delete_session(name)` - 删掉某个会话
- `generate_session_name()` - 用时间戳生成会话名

状态都用 `st.session_state` 存着：
- `messages` - 聊天记录
- `nick_name` - AI 名字
- `nature` - AI 性格
- `current_session` - 当前会话名

## 注意点

1. API Key 别传到 GitHub 上
2. `sessions.db` 记得备份，不然聊天记录没了
3. 需要联网才能用（要调 API）
4. DeepSeek API 是要花钱的，注意用量

## 常见问题

**Q: 报错说找不到模块？**  
A: `pip install streamlit openai` 装一下

**Q: 发了消息没反应？**  
A: 检查 API Key 有没有设对

**Q: 聊天记录在哪看？**  
A: 都在 `sessions.db` 里，侧边栏能看到历史会话

**Q: 能导出聊天记录吗？**  
A: 可以用数据库工具打开 `sessions.db` 自己导

## 更新记录

**v2.0**（现在这个版本）
- 改成用 SQLite 存数据了（之前是 JSON 文件）
- 加载会话快了一些
- 自动记录创建时间

**v1.0**
- 最基本的聊天功能
- 用 JSON 文件存数据

## 许可证

随便玩玩，别商用就行。

---

有问题欢迎提 issue~
