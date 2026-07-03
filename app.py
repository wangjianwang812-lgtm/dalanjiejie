import streamlit as st
from collections import Counter
import streamlit.components.v1 as components

# --- 页面配置 ---
st.set_page_config(page_title="牛逼缩水工具", layout="wide")

# --- UI 样式 ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    #MainMenu, header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #87CEEB !important; }
    .stTextArea textarea { background-color: #000000 !important; color: #ff0000 !important; border: 2px solid #000000 !important; }
    div.stButton > button { background-color: #000000 !important; color: #ffffff !important; border: none !important; border-radius: 4px !important; padding: 5px 10px !important; margin: 2px !important; }
    div.stButton > button:active, div.stButton > button[kind="primary"] { background-color: #ff0000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 核心逻辑 ---
def get_num_type(num_str):
    counts = sorted(Counter(num_str).values(), reverse=True)
    if counts == [4]: return "AAAA"
    if counts == [3, 1]: return "AAAB"
    if counts == [2, 2]: return "AABB"
    if counts == [2, 1, 1]: return "AABC"
    return "ABCD"

def check_is_shunzi(num_str, n):
    num_digits = {int(d) for d in num_str}
    for i in range(10):
        c_set = {(i + j) % 10 for j in range(n)}
        if c_set.issubset(num_digits): return True
    return False

def get_final_numbers(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d)
    for i in range(10000):
        num_str = f"{i:04d}"
        num_set = set(num_str)
        digits_int = [int(d) for d in num_str]
        if manual_d and not (manual_chars & num_set): continue
        if (max(digits_int) - min(digits_int)) in killed_spans: continue
        if get_num_type(num_str) in killed_types: continue
        if any(check_is_shunzi(num_str, n) for n in killed_consecutives): continue
        if sum(digits_int) in killed_sums: continue
        results.append(num_str)
    return results

# --- 强力复制组件 ---
def copy_button_component(text):
    if not text: return
    # 这段代码生成一个直接挂载到浏览器剪贴板的按钮，点击即复制
    html_code = f"""
    <button onclick="navigator.clipboard.writeText(`{text}`);" 
    style="width:100%; padding:15px; font-size:18px; background:#ff0000; color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">
        📋 复制结果到剪贴板
    </button>
    """
    components.html(html_code, height=60)

# --- 界面 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        'manual_d': "", 'results': "", 'count': 0,
        'killed_spans': set(), 'killed_types': set(), 
        'killed_consecutives': set(), 'killed_sums': set()
    }

st.title("🐂 牛逼缩水工具")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("过滤面板")
    def render_filters(label, key, items):
        st.markdown(f"**{label}**")
        rows = [items[i:i+10] for i in range(0, len(items), 10)]
        for row in rows:
            row_cols = st.columns(len(row))
            for idx, item in enumerate(row):
                is_active = item in st.session_state.state[key]
                if row_cols[idx].button(str(item), key=f"{key}_{item}", type="primary" if is_active else "secondary"):
                    if is_active: st.session_state.state[key].remove(item)
                    else: st.session_state.state[key].add(item)
                    st.rerun()

    render_filters("跨度过滤", "killed_spans", list(range(10)))
    render_filters("形态过滤", "killed_types", ["AAAA", "AAAB", "AABB", "ABC", "ABCD"])
    render_filters("顺子过滤", "killed_consecutives", [2, 3, 4])
    render_filters("和值过滤", "killed_sums", list(range(37)))

with col_right:
    st.subheader("计算面板")
    st.session_state.state['manual_d'] = st.text_input("输入胆码 (如 234):", value=st.session_state.state['manual_d'])
    
    if st.button("🚀 开始缩水计算", type="primary", use_container_width=True):
        res = get_final_numbers(st.session_state.state['manual_d'],
                                st.session_state.state['killed_spans'], st.session_state.state['killed_types'], 
                                st.session_state.state['killed_consecutives'], st.session_state.state['killed_sums'])
        st.session_state.state['results'] = " ".join(res)
        st.session_state.state['count'] = len(res)
        st.rerun()
        
    st.metric("剩余注数", st.session_state.state['count'])
    
    # 点击复制按钮
    if st.session_state.state['results']:
        copy_button_component(st.session_state.state['results'])
    
    st.text_area("缩水结果:", value=st.session_state.state['results'], height=250)
