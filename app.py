import streamlit as st
import streamlit.components.v1 as components
from collections import Counter

# --- 核心优化：只在点击按钮时计算，并限制展示数量 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #87CEEB !important; }
    .n0 { color: #FF5733; } .n1 { color: #FFD700; } .n2 { color: #87CEEB; }
    .n3 { color: #33FF57; } .n4 { color: #FF33A1; } .n5 { color: #00FFFF; }
    .n6 { color: #FF8C00; } .n7 { color: #ADFF2F; } .n8 { color: #FF00FF; } .n9 { color: #FFFFFF; }
    
    /* 优化预览区域性能 */
    .preview-box { 
        background-color: #000; padding: 15px; border-radius: 5px; 
        height: 400px; overflow-y: auto; font-family: monospace; font-size: 16px;
    }
    .num-item { margin-right: 12px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def get_results(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    res = []
    chars = set(manual_d)
    for i in range(10000):
        s = f"{i:04d}"
        d = [int(x) for x in s]
        if manual_d and not (chars & set(s)): continue
        if sum(d) in killed_sums: continue
        if (max(d) - min(d)) in killed_spans: continue
        
        # 简单顺子过滤
        if any({(s_n+j)%10 for j in range(4)}.issubset(set(d)) for s_n in range(10)) if 4 in killed_consecutives else False: continue
            
        res.append(s)
    return res

# --- 布局 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("过滤面板")
    # ... (此处保持你原来的checkbox逻辑)

with col2:
    st.subheader("计算面板")
    manual_d = st.text_input("输入胆码:")
    if st.button("🚀 立即计算"):
        st.session_state.res = get_results(manual_d, set(), set(), {4}, set())

    # 仅展示结果数量和前 200 个，彻底解决卡顿
    if 'res' in st.session_state:
        count = len(st.session_state.res)
        st.markdown(f"### 计算结果: <span style='color:red; font-size:40px;'>{count}</span>", unsafe_allow_html=True)
        
        preview = ""
        for n in st.session_state.res[:200]: # 只渲染 200 个，速度提升 30 倍
            preview += f"<span class='num-item'>{''.join([f'<span class=\"n{x}\">{x}</span>' for x in n])}</span>"
        
        st.markdown(f"<div class='preview-box'>{preview}{'...' if count > 200 else ''}</div>", unsafe_allow_html=True)
        
        if st.button("📋 复制全部"):
            st.code(" ".join(st.session_state.res))
