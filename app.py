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
        font-size: 16px !important; height: 200px !important; 
        overflow-y: auto !important; border: 2px solid #000 !important;
        margin-top: 10px !important;
    }
    div.stButton > button { 
        background-color: #FFD700 !important; color: #000 !important; 
        font-weight: bold !important; font-size: 18px !important;
        border: none !important; width: 100% !important; height: 60px !important;
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

# 缓存计算结果，防止重复运算
@functools.lru_cache(maxsize=16)
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d)
    # 预生成范围
    for i in range(10000):
        num_str = f"{i:04d}"
        digits_int = [int(d) for d in num_str]
        
        # 优化判断顺序：从最简单的条件开始
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
    manual_d = st.text_input("输入胆码 (如 234):")
    
    if st.button("🚀 立即计算"):
        # 转换集合为元组，以便被 lru_cache 识别
        res = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                          tuple(st.session_state.killed_types), 
                          tuple(st.session_state.killed_consecutives), 
                          tuple(st.session_state.killed_sums))
        st.session_state.res_text = " ".join(res)
        st.session_state.count = len(res)

    st.markdown(f"### 剩余注数: {st.session_state.count}")
    st.markdown(f'<div class="preview-box">{st.session_state.res_text}</div>', unsafe_allow_html=True)
    
    if st.session_state.res_text:
        copy_text = st.session_state.res_text.replace("'", "\\'")
        components.html(f"""
        <button id="copy_btn" onclick="
            navigator.clipboard.writeText('{copy_text}');
            this.innerText = '✅ 已成功完整复制！';
            setTimeout(() => this.innerText = '📋 一键复制全部结果', 2000);
        " style="width:100%; height:45px; background:#ff0000; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">
            📋 一键复制全部结果
        </button>
        """, height=60)
        st.download_button("💾 下载Txt结果", st.session_state.res_text, "results.txt", use_container_width=True)
