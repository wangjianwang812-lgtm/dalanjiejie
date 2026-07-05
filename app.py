import streamlit as st
from collections import Counter
import streamlit.components.v1 as components
import functools

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    #MainMenu, header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #87CEEB !important; }
    .preview-box { 
        background-color: #000 !important; color: #ff0000 !important; 
        padding: 15px !important; border-radius: 5px !important; 
        font-family: monospace !important; font-weight: bold !important;
        font-size: 16px !important; height: 350px !important; /* 增加高度 */
        overflow-y: auto !important; border: 2px solid #000 !important;
        margin-top: 10px !important; line-height: 1.8 !important;
    }
    /* 调整按钮高度以匹配输入框 */
    div.stButton > button { 
        background-color: #FFD700 !important; color: #000 !important; 
        font-weight: bold !important; border: none !important;
        width: 100% !important; height: 40px !important; margin-top: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 核心计算逻辑 ---
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

@functools.lru_cache(maxsize=16)
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d)
    for i in range(10000):
        num_str = f"{i:04d}"
        digits_int = [int(d) for d in num_str]
        if manual_d and not (manual_chars & set(num_str)): continue
        if sum(digits_int) in killed_sums: continue
        if (max(digits_int) - min(digits_int)) in killed_spans: continue
        if get_num_type(num_str) in killed_types: continue
        if any(check_is_shunzi(num_str, n) for n in killed_consecutives): continue
        results.append(num_str)
    return results

# --- 初始化 ---
if 'res_text' not in st.session_state: st.session_state.res_text = ""
if 'count' not in st.session_state: st.session_state.count = 0
for key in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if key not in st.session_state: st.session_state[key] = set()

# --- 界面 ---
st.title("⚡ 极速缩水工具")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("过滤面板")
    for key, label, items in [('killed_spans', '跨度过滤', list(range(10))), 
                              ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]),
                              ('killed_consecutives', '顺子过滤', [2, 3, 4]),
                              ('killed_sums', '和值过滤', list(range(37)))]:
        st.markdown(f"**{label}**")
        cols = st.columns(10)
        for idx, item in enumerate(items):
            if cols[idx % 10].checkbox(str(item), value=item in st.session_state[key], key=f"cb_{key}_{item}"):
                st.session_state[key].add(item)
            elif item in st.session_state[key]:
                st.session_state[key].remove(item)

with col_right:
    st.subheader("计算面板")
    
    # 调整布局：输入框占3/4，按钮占1/4
    row1, row2 = st.columns([3, 1])
    with row1:
        manual_d = st.text_input("输入胆码 (如 234):")
    with row2:
        calc_btn = st.button("🚀 立即计算")
        
    if calc_btn:
        res = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                          tuple(st.session_state.killed_types), 
                          tuple(st.session_state.killed_consecutives), 
                          tuple(st.session_state.killed_sums))
        st.session_state.res_text = " ".join(res)
        st.session_state.count = len(res)

    # 剩余注数放在原按钮位置
    st.markdown(f"### 剩余注数: {st.session_state.count}")
    
    # 按钮组往上移
    if st.session_state.res_text:
        copy_text = st.session_state.res_text.replace("'", "\\'")
        c1, c2 = st.columns([1, 1])
        with c1:
            components.html(f"""
            <button id="copy_btn" onclick="navigator.clipboard.writeText('{copy_text}'); this.innerText='✅ 已复制';" style="width:100%; height:40px; background:#ff0000; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">
                📋 复制结果
            </button>
            """, height=50)
        with c2:
            st.download_button("💾 下载Txt", st.session_state.res_text, "results.txt", use_container_width=True)

    # 黑色显示框加高
    st.markdown(f'<div class="preview-box">{st.session_state.res_text}</div>', unsafe_allow_html=True)
