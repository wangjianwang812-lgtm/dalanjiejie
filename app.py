import streamlit as st
import functools

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式：严格锁定，不再改动 ---
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
    </style>
""", unsafe_allow_html=True)

# --- 核心计算逻辑：严谨的过滤实现 ---
@functools.lru_cache(maxsize=16)
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d)
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        
        # 严格执行过滤规则
        if manual_d and not (manual_chars & set(num_str)): continue
        if sum(digits) in killed_sums: continue
        if (max(digits) - min(digits)) in killed_spans: continue
        
        # 这里补全你之前正常的顺子/形态过滤逻辑
        # ...
        
        results.append(num_str)
    return results

# --- 初始化 ---
if 'res_text' not in st.session_state: st.session_state.res_text = ""
if 'count' not in st.session_state: st.session_state.count = 0
for key in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if key not in st.session_state: st.session_state[key] = set()

# --- 界面布局 ---
st.title("⚡ 极速缩水工具")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("过滤面板")
    # ... (此处渲染过滤选项的代码保持不变)
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
    manual_d = st.text_input("输入胆码 (如 234):", key="manual_input")
    
    if st.button("🚀 立即计算"):
        res = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                          tuple(st.session_state.killed_types), 
                          tuple(st.session_state.killed_consecutives), 
                          tuple(st.session_state.killed_sums))
        st.session_state.res_text = " ".join(res)
        st.session_state.count = len(res)
        st.rerun()

    st.markdown(f"### 剩余注数: {st.session_state.count}")
    
    # 复制按钮
    if st.button("📋 复制结果"):
        st.write(f"正在复制: {st.session_state.res_text[:50]}...")

    st.markdown(f'<div class="preview-box">{st.session_state.res_text}</div>', unsafe_allow_html=True)
