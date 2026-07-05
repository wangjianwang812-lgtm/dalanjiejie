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
        font-size: 16px !important; height: 450px !important; 
        overflow-y: auto !important; border: 2px solid #000 !important;
        margin-top: 10px !important; line-height: 1.8 !important;
    }
    /* 统一按钮样式，确保饱满度和高度一致 */
    .custom-btn {
        width: 100% !important; 
        height: 42px !important; 
        font-weight: bold !important; 
        border: none !important; 
        border-radius: 4px !important;
        font-size: 16px !important;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 核心计算逻辑 ---
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
    
    # 核心布局调整：使用 [2, 1] 比例将输入框与右侧功能区精准分开
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        manual_d = st.text_input("输入胆码 (如 234):", key="manual_input")
        # 将剩余注数放在输入框下方，宽度自然对其
        st.markdown(f"### 剩余注数: {st.session_state.count}")
    
    with c_right:
        # 立即计算按钮
        st.markdown("<br>", unsafe_allow_html=True) # 垂直对齐间距
        if st.button("🚀 立即计算"):
            res = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                              tuple(st.session_state.killed_types), 
                              tuple(st.session_state.killed_consecutives), 
                              tuple(st.session_state.killed_sums))
            st.session_state.res_text = " ".join(res)
            st.session_state.count = len(res)
            st.rerun()
            
        # 复制结果按钮 (使用 HTML 确保样式统一)
        copy_text = st.session_state.res_text.replace("'", "\\'")
        components.html(f"""
        <button onclick="navigator.clipboard.writeText('{copy_text}'); this.innerText='✅ 已复制';" 
        class="custom-btn" style="background:#ff0000; color:#fff; border:none;">
            📋 复制结果
        </button>
        """, height=55)

    st.markdown(f'<div class="preview-box">{st.session_state.res_text}</div>', unsafe_allow_html=True)
