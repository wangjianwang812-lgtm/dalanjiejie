import streamlit as st
import streamlit.components.v1 as components
from collections import Counter

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
    .stTextInput > div > div > input { width: 175px !important; min-width: 175px !important; }
    div.stButton > button { 
        background-color: #FFD700 !important; color: #000 !important; 
        width: 175px !important; height: 50px !important; 
        font-weight: 900 !important; font-size: 18px !important; 
        border-radius: 5px !important; border: none !important;
    }
    .unified-btn {
        width: 175px !important; height: 50px !important; 
        font-weight: 900 !important; font-size: 18px !important;
        border-radius: 5px !important; border: none !important;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        background-color: #FF0000 !important; color: #FFF !important;
        margin-top: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 核心计算逻辑 ---
@st.cache_data
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    # 胆码处理：将输入的数字转为集合
    manual_chars = set(manual_d) if manual_d else set()
    
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        num_set = set(digits)
        
        # 1. 胆码过滤
        if manual_d and not (manual_chars & set(num_str)): continue
        
        # 2. 和值过滤
        if sum(digits) in killed_sums: continue
        
        # 3. 跨度过滤
        if (max(digits) - min(digits)) in killed_spans: continue
        
        # 4. 顺子过滤 (顺序无关，支持循环顺子，包含即杀)
        is_killed_shunzi = False
        for n in killed_consecutives:
            for start_digit in range(10):
                shunzi_set = {(start_digit + j) % 10 for j in range(n)}
                if shunzi_set.issubset(num_set):
                    is_killed_shunzi = True
                    break
            if is_killed_shunzi: break
        if is_killed_shunzi: continue
        
        # 5. 形态过滤
        counts = sorted(Counter(digits).values(), reverse=True)
        type_str = "ABCD"
        if counts == [4]: type_str = "AAAA"
        elif counts == [3, 1]: type_str = "AAAB"
        elif counts == [2, 2]: type_str = "AABB"
        elif counts == [2, 1, 1]: type_str = "AABC"
        if type_str in killed_types: continue
        
        results.append(num_str)
    return results

# --- 初始化状态 ---
if 'killed_spans' not in st.session_state:
    st.session_state.update({k: set() for k in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']})

# --- 界面布局 ---
st.title("⚡ 极速缩水工具")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("过滤面板")
    # 跨度过滤
    st.markdown("**跨度过滤**")
    cols = st.columns(10)
    for i in range(10):
        if cols[i].checkbox(str(i), value=i in st.session_state.killed_spans, key=f"span_{i}"):
            st.session_state.killed_spans.add(i)
        elif i in st.session_state.killed_spans:
            st.session_state.killed_spans.remove(i)
    
    # 形态过滤
    st.markdown("**形态过滤**")
    types = ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]
    cols = st.columns(5)
    for i, t in enumerate(types):
        if cols[i].checkbox(t, value=t in st.session_state.killed_types, key=f"type_{t}"):
            st.session_state.killed_types.add(t)
        elif t in st.session_state.killed_types:
            st.session_state.killed_types.remove(t)
            
    # 顺子过滤
    st.markdown("**顺子过滤**")
    cols = st.columns(3)
    for i, n in enumerate([2, 3, 4]):
        if cols[i].checkbox(str(n), value=n in st.session_state.killed_consecutives, key=f"shun_{n}"):
            st.session_state.killed_consecutives.add(n)
        elif n in st.session_state.killed_consecutives:
            st.session_state.killed_consecutives.remove(n)
            
    # 和值过滤
    st.markdown("**和值过滤**")
    cols = st.columns(10)
    for i in range(37):
        if cols[i % 10].checkbox(str(i), value=i in st.session_state.killed_sums, key=f"sum_{i}"):
            st.session_state.killed_sums.add(i)
        elif i in st.session_state.killed_sums:
            st.session_state.killed_sums.remove(i)

with col_right:
    st.subheader("计算面板")
    manual_d = st.text_input("输入胆码 (如 234):", key="manual_input")
    
    if st.button("🚀 立即计算"):
        res = cached_calc(manual_d, tuple(st.session_state.killed_spans), tuple(st.session_state.killed_types), 
                          tuple(st.session_state.killed_consecutives), tuple(st.session_state.killed_sums))
        st.session_state.res_list = res
        st.rerun()

    res_list = st.session_state.get('res_list', [])
    st.markdown(f"### 剩余注数: {len(res_list)}")
    
    # 结果预览 (截断显示以优化性能)
    display_text = " ".join(res_list[:300])
    if len(res_list) > 300: display_text += f"\n\n... (共 {len(res_list)} 注，此处仅预览前300注)"
    st.markdown(f'<div class="preview-box">{display_text}</div>', unsafe_allow_html=True)
    
    # 复制按钮
    if res_list:
        copy_text = " ".join(res_list)
        components.html(f"""
        <button id="copyBtn" class="unified-btn" onclick="
            navigator.clipboard.writeText('{copy_text}');
            var btn = document.getElementById('copyBtn');
            btn.innerText = '✅ 已复制全量';
            setTimeout(() => btn.innerText = '📋 复制结果', 2000);
        ">📋 复制结果</button>
        """, height=70)
