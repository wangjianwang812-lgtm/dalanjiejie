import streamlit as st
from collections import Counter
import streamlit.components.v1 as components

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    #MainMenu, header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .stApp { background-color: #87CEEB !important; }
    div.stButton > button { transition: all 0.1s !important; border-radius: 4px !important; background-color: #000 !important; color: #fff !important; }
    div.stButton > button:active { transform: scale(0.95); }
    .stTextArea textarea { background-color: #000000 !important; color: #ff0000 !important; border: 2px solid #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 核心计算逻辑 ---
def get_final_numbers(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    # 这里保持你的核心计算逻辑不变
    results = []
    manual_chars = set(manual_d)
    # 提取逻辑进行简单的优化
    def get_num_type(n_s):
        c = sorted(Counter(n_s).values(), reverse=True)
        if c == [4]: return "AAAA"
        if c == [3, 1]: return "AAAB"
        if c == [2, 2]: return "AABB"
        if c == [2, 1, 1]: return "AABC"
        return "ABCD"
    
    for i in range(10000):
        num_str = f"{i:04d}"
        if manual_d and not (set(manual_d) & set(num_str)): continue
        d_int = [int(d) for d in num_str]
        if (max(d_int) - min(d_int)) in killed_spans: continue
        if get_num_type(num_str) in killed_types: continue
        # 顺子和和值逻辑...
        results.append(num_str)
    return results

# --- 初始化 ---
if 'res_text' not in st.session_state: st.session_state.res_text = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'trigger_calc' not in st.session_state: st.session_state.trigger_calc = False
for key in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if key not in st.session_state: st.session_state[key] = set()

# --- 界面布局 ---
st.title("⚡ 极速缩水工具")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("过滤面板")
    # (过滤项代码同前，保持不变...)
    # ...[此处放置你的checkbox循环代码]...

with col_right:
    st.subheader("计算面板")
    manual_d = st.text_input("输入胆码 (如 234):")
    
    # 关键：这里不再直接写计算逻辑，而是仅仅改变一个状态位
    if st.button("🚀 立即计算", type="primary", use_container_width=True):
        st.session_state.trigger_calc = True
    
    # 页面刷新时检测到标志位才执行计算，这样按钮会先完成回弹动作
    if st.session_state.trigger_calc:
        res = get_final_numbers(manual_d, st.session_state.killed_spans, st.session_state.killed_types, 
                                st.session_state.killed_consecutives, st.session_state.killed_sums)
        st.session_state.res_text = " ".join(res)
        st.session_state.count = len(res)
        st.session_state.trigger_calc = False # 重置标志位
        st.rerun() # 执行一次性渲染

    st.metric("剩余注数", st.session_state.count)
    st.text_area("缩水结果:", value=st.session_state.res_text, height=250)
    
    # 复制逻辑 (保持不变)
    if st.session_state.res_text:
        # ...[此处放置复制组件代码]...
