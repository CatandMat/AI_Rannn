import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json
import uuid
# print("重新执行此文件")
#设置页面配置项
st.set_page_config(
    page_title="AI_Rannn",
    page_icon="🥰",
    layout="wide",#居中
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
#生成会话标识函数
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + str(uuid.uuid4())[:6]
#保存会话信息
def save_session():
    # 保存当前会话信息
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages,
            "nick_name": st.session_state.nick_name,
            "personality": st.session_state.personality
        }
        # 如果sessions目录不存在，则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)

#加载所有的会话列表信息
def load_sessions():
    session_list=[]
    #加载sessions目录下的文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)  # 排序，降序排序
    return session_list

#加载指定会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            #读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.current_session = session_data["current_session"]
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.personality = session_data["personality"]
    except Exception:
        st.error(f"Error loading session !")
#删除会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            # 删除会话数据
            os.remove(f"sessions/{session_name}.json")
            #如果删除的是当前会话，则需要更新消息列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_id()
    except Exception:
        st.error(f"Error deleting session !")

#大标题
st.title("AI_Rannn")
#logo
st.logo("resources/logo.jpg")

#系统提示词
system_promopt="你是一名AI女友，名字叫%s，性格为%s"

#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []
#昵称
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = "Rann"
#性格
if 'personality' not in st.session_state:
    st.session_state.personality = "非常可爱的我的AI女友"
#会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_id()


#展示聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])


#创建与AI交互的客户端对象（DEEPSEEK_API_KEY是环境变量的名字，值就是Deepseek的API_KEY的
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

#左侧侧边栏
with st.sidebar:
    #会话信息
    st.subheader("AI控制面板")
    #新建会话按钮
    if st.button("新建会话",width="stretch",icon="😘"):
        #保存会话信息
        save_session()

        # 创建新的会话
        if st.session_state.messages:#如果聊天消息非空，则保存当前会话
            st.session_state.messages=[]
            st.session_state.current_session=generate_session_id()
            save_session()
            st.rerun()  # 重新运行页面
    #会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
            #加载会话信息
            #三元运算符
           if st.button(session, width="stretch", icon="📄",key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
               #加载指定会话信息
               load_session(session)
               st.rerun()  # 重新运行页面
        with col2:
            #删除会话信息
            if st.button("", width="stretch", icon="❌️",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()  # 重新运行页面

    #分割线
    st.divider()
    #伴侣信息
    st.subheader("人物信息")
    #姓名输入框
    nick_name = st.text_input("昵称",placeholder="Please input name",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框
    personality = st.text_area("性格",placeholder="Please input personality",value=st.session_state.personality)
    if personality:
        st.session_state.personality = personality


#消息输入框
prompt= st.chat_input("宝贝想问什么呢？")
if prompt:
    st.chat_message("user").write(prompt)
    print("调用AI大模型，提示词",prompt)
    #保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    #调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system",
             "content": system_promopt % (st.session_state.nick_name, st.session_state.personality)},
            #会话记忆
            *st.session_state.messages
        ],
        #流式输出
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    # 输出大模型返回的结果(非流式输出的解析方式）
    # print("大模型返回的结果:",response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    #流式输出方式
    response_message=st.empty()#创建一个空的组件来显示大模型的返回结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response+=content
            response_message.chat_message("assistant").write(full_response)
    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content":full_response })

    #保存会话信息
    save_session()