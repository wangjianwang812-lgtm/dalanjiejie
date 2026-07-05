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
    /* 统一按钮样式：宽度、高度、圆角 */
    .btn-style {
        width: 100% !important; 
        height: 48px !important; 
        font-weight: bold !important; 
        border: none !important;
        border-radius: 4px !important;
        font-size: 16px !important;
        cursor: pointer;
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
        if manual_d and not (manual_chars & set(num_str)): continue
        results.append(num_str)
    return results

# --- 界面 ---
st.title("⚡ 极速缩水工具")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("过滤面板")
    # ... (过滤面板逻辑保持不变)

with col_right:
    st.subheader("计算面板")
    
    # 布局：左侧输入框，右侧垂直堆叠两个按钮
    col_input, col_btns = st.columns([2, 1])
    
    with col_input:
        manual_d = st.text_input("输入胆码 (如 234):", key="input_d")
        st.markdown(f"### 剩余注数: {st.session_state.get('count', 0)}")
    
    with col_btns:
        # 立即计算按钮 (Streamlit 原生)
        if st.button("🚀 立即计算"):
            st.session_state.res_text = " ".join(cached_calc(manual_d, tuple(), tuple(), tuple(), tuple()))
            st.session_state.count = len(st.session_state.res_text.split())
            st.rerun()
            
        # 复制结果按钮 (HTML 模拟以保持样式一致)
        copy_text = st.session_state.get('res_text', '').replace("'", "\\'")
        components.html(f"""
        <button onclick="navigator.clipboard.writeText('{copy_text}'); this.innerText='✅ 已复制';" 
        class="btn-style" style="background:#ff0000; color:#fff;">
            📋 复制结果
        </button>
        """, height=60)

    st.markdown(f'<div class="preview-box">{st.session_state.get("res_text", "")}</div>', unsafe_allow_html=True)
