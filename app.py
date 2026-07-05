import streamlit as st
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
    
    /* 输入框宽度设置 */
    .stTextInput > div > div > input { 
        width: 175px !important; 
        min-width: 175px !important; 
    }
    
    /* 立即计算按钮样式 */
    div.stButton > button { 
        background-color: #FFD700 !important; color: #000 !important; 
        width: 140px !important; height: 44px !important; 
        font-weight: 900 !important; font-size: 16px !important; 
        border-radius: 5px !important; border: none !important;
    }
    div.stButton > button:hover { background-color: #FFC107 !important; border: 2px solid #000 !important; }

    /* 复制按钮样式 */
    .unified-btn {
        width: 140px !important; height: 44px !important; 
        font-weight: 900 !important; font-size: 16px !important;
        border-radius: 5px !important; border: none !important;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        background-color: #FF0000; color: #FFF;
    }
    .unified-btn:hover { background-color: #CC0000 !important; border: 2px solid #000 !important; }
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
    
    # 布局采用左右并排，输入框与按钮区紧凑排列
    c_in, c_btn = st.columns([1, 1])
    
    with c_in:
        manual_d = st.text_input("输入胆码 (如 234):", key="manual_input")
        st.markdown(f"### 剩余注数: {st.session_state.count}")
    
    with c_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        
        # 立即计算按钮
        if st.button("🚀 立即计算"):
            res = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                              tuple(st.session_state.killed_types), 
                              tuple(st.session_state.killed_consecutives), 
                              tuple(st.session_state.killed_sums))
            st.session_state.res_text = " ".join(res)
            st.session_state.count = len(res)
            st.rerun()
            
        # 复制结果按钮 (点击后变为“已复制”，2秒后自动恢复)
        copy_text = st.session_state.res_text.replace("'", "\\'")
        components.html(f"""
        <button id="copyBtn" onclick="
            navigator.clipboard.writeText('{copy_text}');
            var btn = document.getElementById('copyBtn');
            btn.innerText = '✅ 已复制';
            setTimeout(function() {{
                btn.innerText = '📋 复制结果';
            }}, 2000);
        " class="unified-btn">
            📋 复制结果
        </button>
        """, height=60)

    st.markdown(f'<div class="preview-box">{st.session_state.res_text}</div>', unsafe_allow_html=True)
