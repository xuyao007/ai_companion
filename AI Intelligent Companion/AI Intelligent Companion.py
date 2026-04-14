import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import json
import sqlite3
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
            "messages": st.session_state.messages
        }

        # 初始化数据库
        init_db()

        # 检查会话是否已存在
        conn = sqlite3.connect('sessions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE session_name = ?', 
                      (session_data['current_session'],))
        exists = cursor.fetchone()[0] > 0
        
        # 保存或更新会话数据
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (session_name, nick_name, nature, messages)
            VALUES (?, ?, ?, ?)
        ''', (
            session_data['current_session'],
            session_data['nick_name'],
            session_data['nature'],
            json.dumps(session_data['messages'], ensure_ascii=False)
        ))
        conn.commit()
        conn.close()
        
        return not exists

# 加载所有会话列表
def load_sessions():
    session_list = []
    # 初始化数据库
    init_db()
    
    conn = sqlite3.connect('sessions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT session_name FROM sessions ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        session_list.append(row[0])
    
    return session_list

# 加载指定会话
def load_session(session_name):
    try:
        init_db()
        conn = sqlite3.connect('sessions.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nick_name, nature, messages FROM sessions WHERE session_name = ?', 
                      (session_name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            st.session_state.nick_name = row[0]
            st.session_state.nature = row[1]
            st.session_state.messages = json.loads(row[2])
            st.session_state.current_session = session_name

    except Exception:
        st.error("加载会话失败！")

# 删除指定会话
def delete_session(session_name):
    try:
        init_db()
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

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化伴侣昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小美"

# 初始化伴侣性格
if "nature" not in st.session_state:
    st.session_state.nature = "成熟、独立、自信且充满魅力的女性角色，性格冷静、坚强，具备领导力和保护欲。"

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 当前会话名称
st.text(f"会话名称：{st.session_state.current_session}")

# 展示聊天记录
for message in st.session_state.messages:
    # message 样式是 {"role": "user", "content": prompt}
    st.chat_message(message["role"]).write(message["content"])

# 创建与AI模型连接
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

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
            print("<-------- 重新渲染_1 --------> ")
            st.rerun()  # 重新运行当前页面

    # 会话历史
    st.text("历史会话")
    session_list = load_sessions()
    for session_name in session_list:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(session_name, width="stretch", key=f"load_{session_name}", icon="📜", type="primary" if session_name == st.session_state.current_session else "secondary"):
                load_session(session_name)
                print("<-------- 重新渲染_2 --------> ")
                st.rerun()

        with col2:
            if st.button("", width="stretch", key=f"delete_{session_name}", icon="🗑️"):
                delete_session(session_name)
                print("<-------- 重新渲染_3 --------> ")
                st.rerun()

    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")

    # 昵称输入框
    nick_name = st.text_input("伴侣昵称:", placeholder="请输入伴侣昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框
    nature = st.text_area("伴侣性格:", placeholder="请输入伴侣性格", value=st.session_state.nature)

# 消息输入框
prompt = st.chat_input("请输入你的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print("----------------->调用ai大模型，提示词", prompt)

    # 保存用户输入的问题
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用ai大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
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

    # 保存会话信息，如果是新文件则重新渲染
    is_new_file = save_session()
    if is_new_file:
        print("<-------- 重新渲染_4 --------> ")
        st.rerun()
