import streamlit as st
from collections import Counter

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
    div.stButton > button:active { background-color: #ff0000 !important; }
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

# --- 初始化状态 ---
if 'res_text' not in st.session_state: st.session_state.res_text = ""
if 'count' not in st.session_state: st.session_state.count = 0
for key in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums', 'manual_d']:
    if key not in st.session_state: 
        st.session_state[key] = set() if 'killed' in key else ""

st.title("🐂 牛逼缩水工具")
col_left, col_right = st.columns([1, 1])

# --- 过滤面板 ---
with col_left:
    st.subheader("过滤面板")
    def render_filters(label, key, items):
        st.markdown(f"**{label}**")
        for i in range(0, len(items), 10):
            row = items[i:i+10]
            row_cols = st.columns(len(row))
            for idx, item in enumerate(row):
                is_active = item in st.session_state[key]
                if row_cols[idx].button(str(item), key=f"{key}_{item}", type="primary" if is_active else "secondary"):
                    if is_active: st.session_state[key].remove(item)
                    else: st.session_state[key].add(item)

    render_filters("跨度过滤", "killed_spans", list(range(10)))
    render_filters("形态过滤", "killed_types", ["AAAA", "AAAB", "AABB", "ABC", "ABCD"])
    render_filters("顺子过滤", "killed_consecutives", [2, 3, 4])
    render_filters("和值过滤", "killed_sums", list(range(37)))

# --- 计算面板 ---
with col_right:
    st.subheader("计算面板")
    st.session_state.manual_d = st.text_input("输入胆码 (如 234):", value=st.session_state.manual_d)
    
    # 点击即刻计算，无需 st.rerun()，响应极快
    if st.button("🚀 开始缩水计算", type="primary", use_container_width=True):
        res = get_final_numbers(st.session_state.manual_d,
                                st.session_state.killed_spans, st.session_state.killed_types, 
                                st.session_state.killed_consecutives, st.session_state.killed_sums)
        st.session_state.res_text = " ".join(res)
        st.session_state.count = len(res)
        
    st.metric("剩余注数", st.session_state.count)
    
    # 官方下载按钮，点击瞬间响应，绝不卡顿
    if st.session_state.res_text:
        st.download_button("💾 点击下载全部结果 (Txt)", st.session_state.res_text, "results.txt", use_container_width=True)
    
    st.text_area("缩水结果 (可全选复制):", value=st.session_state.res_text, height=250)
