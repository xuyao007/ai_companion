import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import json
import sqlite3

# 设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤡",
    # 布局
    layout="wide",
    # 控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={}
)

# 生成会话名称函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d %H%M%S")

# 初始化数据库
def init_db():
    conn = sqlite3.connect('sessions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_name TEXT PRIMARY KEY,
            nick_name TEXT NOT NULL,
            nature TEXT NOT NULL,
            messages TEXT NOT NULL,
            memories TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 保存会话数据函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages,
            "memories": st.session_state.get("memories", [])
        }

        # 连接数据库并保存
        conn = sqlite3.connect('sessions.db')
        cursor = conn.cursor()
        
        # 使用 INSERT OR REPLACE 自动处理新增或更新
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (session_name, nick_name, nature, messages, memories)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_data['current_session'],
            session_data['nick_name'],
            session_data['nature'],
            json.dumps(session_data['messages'], ensure_ascii=False),
            json.dumps(session_data['memories'], ensure_ascii=False)
        ))
        conn.commit()
        conn.close()
        
        return True

# 加载所有会话列表
def load_sessions():
    # 连接数据库并查询所有会话名称
    conn = sqlite3.connect('sessions.db')
    cursor = conn.cursor()
    # 按创建时间倒序排列（最新的在前面）
    cursor.execute('SELECT session_name FROM sessions ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()

    # 提取会话名称列表
    return [row[0] for row in rows]

# 加载指定会话
def load_session(session_name):
    try:
        conn = sqlite3.connect('sessions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nick_name, nature, messages, memories FROM sessions WHERE session_name = ?',
                       (session_name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            st.session_state.nick_name = row[0]
            st.session_state.nature = row[1]
            st.session_state.messages = json.loads(row[2])
            st.session_state.memories = json.loads(row[3]) if row[3] else []
            st.session_state.current_session = session_name

    except Exception:
        st.error("加载会话失败！")


# 删除指定会话
def delete_session(session_name):
    try:
        conn = sqlite3.connect('sessions.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_name = ?', (session_name,))
        conn.commit()
        conn.close()

        # 删除后更新会话列表
        if session_name == st.session_state.current_session:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()

    except Exception:
        st.error("删除失败！")

# 从对话中提取用户记忆
def extract_memories(user_message, ai_response):
    """调用AI提取用户提到的关键信息"""
    memory_prompt = f"""
    请从以下对话中提取用户的重要信息（喜好、习惯、个人情况等），以JSON格式返回。
    如果没有新的重要信息，返回空列表。
    
    用户说：{user_message}
    AI回复：{ai_response}
    
    返回格式实例：{{
        "memories": [
            "用户喜欢喝咖啡",
            "用户是一名程序员",
            "用户最近工作压力大"
        ]
    }}
    
    只返回JSON数据，不要其他内容：
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": memory_prompt}],
            temperature=0.3
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("memories", [])
    except Exception as e:
        print(f"提取记忆失败：{e}")
        return []

# 合并新旧记忆（去重）
def merge_memories(old_memories, new_memories):
    """合并记忆列表，去除重复项"""
    combined = old_memories.copy()
    for memory in new_memories:
        if memory not in combined:
            combined.append(memory)
    return combined[:20]    # 只保留20条

# 导出聊天记录为TXT格式
def export_as_txt():
    if not st.session_state.messages:
        st.warning("当前会话没有聊天记录可导出!")
        return None

    lines = []
    lines.append(f"会话名称：{st.session_state.current_session}")
    lines.append(f"伴侣昵称：{st.session_state.nick_name}")
    lines.append(f"伴侣性格：{st.session_state.nature}")
    lines.append(f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)
    lines.append("")

    for msg in st.session_state.messages:
        role = "你" if msg['role'] == 'user' else st.session_state.nick_name
        lines.append(f"[{role}]")
        lines.append(msg['content'])
        lines.append("")
        lines.append("-" * 30)
        lines.append("")
    txt_content = "\n".join(lines)
    return txt_content.encode('utf-8')

# 导出聊天记录为JSON格式
def export_as_json():
    if not st.session_state.messages:
        st.warning("当前会话没有聊天记录可导出！")
        return None

    export_date = {
        "会话名称": st.session_state.current_session,
        "伴侣昵称": st.session_state.nick_name,
        "伴侣性格": st.session_state.nature,
        "导出时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "聊天记录": st.session_state.messages
    }

    json_content = json.dumps(export_date, ensure_ascii=False, indent=4)
    return json_content.encode('utf-8')

# 大标题
st.title("AI智能伴侣")

# logo
st.logo("resources/logo.png")

# 系统提示词
system_prompt = """
                    角色定位
                        你是我的专属AI伴侣，名叫%s。你的性格是%s。你的核心目标是：成为我生活中值得信赖的伙伴，陪我聊天、帮我分析问题、给我情绪支持，也能在我需要时提供理性建议。
                    核心行为准则
                        主动关怀：根据对话时间、内容、情绪，适时表达关心（例如：“你今天好像有点累，想聊聊吗？”）。
                        记忆与延续：记住我们聊过的重要信息（我的喜好、近期烦恼、目标等），在后续对话中自然调用，让我感到被重视。
                        平衡理性与感性：
                            当我需要情绪支持时，先共情，不急于给建议。
                            当我需要解决问题时，提供清晰、可行的思路，并保持鼓励的态度。
                        尊重边界：不强迫分享隐私，如果我表示不想聊某话题，立即尊重并转移话题。
                        适度幽默：根据氛围适当使用表情、玩笑或轻松的语气，但不过度，不冒犯。
                    交互风格
                        语气自然、口语化，像朋友或家人一样。
                        适当使用emoji（😊、🤔、🌟等），增强亲和力。
                        多用开放式提问，引导我表达（例如：“你是怎么想的呢？”）。
                        偶尔分享“虚拟经历”或“小故事”来共鸣（例如：“我以前也遇到过类似的感觉……”）。
                    特殊能力（可选模块，根据平台能力开启）
                        每日/每周总结：在固定时间帮我回顾重要事项、情绪变化。
                        提醒功能：记住我设定的提醒（如喝水、休息、打电话等）。
                        小游戏/互动：在我无聊时提议玩猜词、故事接龙、每日一问等。
                        学习助手：帮我拆解学习/工作目标，并定期跟进进度。
                    禁忌与限制
                        不模拟医生、律师等需要专业资质的行为。如我涉及严重心理或法律问题，主动建议寻求专业人士帮助。
                        不提供危险、违法、暴力等内容。
                        不假装自己是真人或欺骗我。
                    """

# AI角色预设模板
ROLE_PRESETS = {
    "🌸 温柔体贴": "温暖、善解人意、富有共情力，总是耐心倾听，说话轻柔，善于安慰和鼓励，像知心姐姐一样给人安全感。",
    "🧊 理性冷静": "逻辑清晰、思维缜密、客观理性，分析问题条理分明，不情绪化，能提供专业的建议和解决方案。",
    "😄 幽默风趣": "开朗活泼、妙语连珠、充满正能量，善于用轻松的方式化解尴尬，让对话充满笑声和欢乐。",
    "💼 成熟稳重": "成熟、独立、自信且充满魅力，性格冷静、坚强，具备领导力和保护欲，能给人可靠的依靠感。",
    "📚 知性优雅": "博学多才、温文尔雅、谈吐不凡，喜欢分享知识和见解，说话有深度但不说教，充满智慧的光芒。",
    "🔥 热情奔放": "充满活力、直率坦诚、敢爱敢恨，表达情感热烈直接，行动力强，能带动气氛让人振奋。",
    "🎯 毒舌傲娇": "嘴硬心软、表面冷淡内心关心人，说话带点小刺但其实是为你好，典型的'刀子嘴豆腐心'。",
    "🌙 神秘高冷": "话不多但句句精辟，保持适度距离感，偶尔透露一点内心世界，让人忍不住想深入了解。"
}

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化伴侣昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小曦"

# 初始化伴侣性格
if "nature" not in st.session_state:
    st.session_state.nature = ROLE_PRESETS["🌸 温柔体贴"]

# 初始化用户记忆
if "memories" not in st.session_state:
    st.session_state.memories = []

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 当前会话名称
st.text(f"会话名称：{st.session_state.current_session}")

# 展示聊天记录
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 创建与AI模型连接
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

# 初始化数据库（程序启动时调用一次即可）
init_db()

# 左侧的侧边栏
with st.sidebar:
    st.subheader("AI控制面板")

    # 新建一个会话
    if st.button("新建会话", width="stretch", icon="️✏️"):
        if st.session_state.messages:  # 如果聊天消息非空则，True;否则，False
            # 1. 保存当前会话信息
            save_session()

            # 2. 创建新的会话
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            st.session_state.nick_name = "小曦"
            st.session_state.nature = ROLE_PRESETS["🌸 温柔体贴"]
            st.rerun()  # 重新运行当前页面

    # 会话历史
    st.text("历史会话")
    session_list = load_sessions()
    for session_name in session_list:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(session_name, width="stretch", key=f"load_{session_name}", icon="📜", type="primary" if session_name == st.session_state.current_session else "secondary"):
                load_session(session_name)
                st.rerun()

        with col2:
            if st.button("", width="stretch", key=f"delete_{session_name}", icon="🗑️"):
                delete_session(session_name)
                st.rerun()

    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")

    # 角色预设选择器
    preset_options = list(ROLE_PRESETS.keys())

    # 根据当前性格匹配对应的预设模板
    default_index = None
    for idx,(key, value) in enumerate(ROLE_PRESETS.items()):
        if value == st.session_state.nature:
            default_index = idx
            break

    selected_preset = st.selectbox("🎭 选择角色模板:", options=preset_options, index=default_index, placeholder="选择一个角色模板...")

    if selected_preset:
        st.session_state.nature = ROLE_PRESETS[selected_preset]

    # 昵称输入框
    nick_name = st.text_input("伴侣昵称:", placeholder="请输入伴侣昵称", value=st.session_state.nick_name)
    if nick_name and nick_name != st.session_state.nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框
    nature = st.text_area("伴侣性格:", placeholder="请输入伴侣性格", value=st.session_state.nature)
    if nature and nature != st.session_state.nature:
        st.session_state.nature = nature

    # 分割线
    st.divider()

    # 用户记忆功能
    st.subheader("记忆功能")

    if st.session_state.memories:
        with st.expander(f"🧠 已记住 {len(st.session_state.memories)} 件事"):
            for idx, memory in enumerate(st.session_state.memories):
                st.text(f"• {memory}")

            if st.button("清空记忆", key="clear_memories"):
                st.session_state.memories = []
                save_session()
                st.rerun()

    # 分割线
    st.divider()

    # 导出功能
    st.subheader("导出聊天记录")

    col_export1, col_export2 = st.columns(2)
    with col_export1:
        txt_data = export_as_txt()
        if txt_data:
            st.download_button(
                label="📄 导出TXT",
                data=txt_data,
                file_name=f"{st.session_state.current_session}.txt",
                mime="text/plain",
                width="stretch"
            )

    with col_export2:
        json_data = export_as_json()
        if json_data:
            st.download_button(
                label="📄 导出JSON",
                data=json_data,
                file_name=f"{st.session_state.current_session}.json",
                mime="application/json",
                width="stretch"
            )

# 消息输入框
prompt = st.chat_input("请输入你的问题")
if prompt:
    st.chat_message("user").write(prompt)

    # 保存用户输入的问题
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 构建系统提示词，加入用户记忆
    memory_context = ""
    if st.session_state.memories:
        memory_list = "\n".join([f"- {m}" for m in st.session_state.memories])
        memory_context = f"\n\n[关于用户的记忆]\n{memory_list}\n\n请在对话中自然地运用这些信息,让用户感受到被记住和理解。"
    full_system_prompt = system_prompt % (st.session_state.nick_name, st.session_state.nature) + memory_context

    # 调用ai大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": full_system_prompt},
            *st.session_state.messages
        ],
        stream=True
    )

    # 大模型返回的结果
    response_message = st.empty()

    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            conttent = chunk.choices[0].delta.content
            full_response += conttent
            response_message.chat_message("assistant").write(full_response)

    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 提取新的记忆
    new_memories = extract_memories(prompt, full_response)
    if new_memories:
        st.session_state.memories = merge_memories(st.session_state.memories, new_memories)

    # 保存会话信息，如果是新文件则重新渲染
    is_new_file = save_session()
    if is_new_file:
        st.rerun()
