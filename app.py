import streamlit as st
import streamlit.components.v1 as components
import functools
from collections import Counter

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 (完全保留你的原始 CSS) ---
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
    div.stButton > button:hover { background-color: #FFC107 !important; border: 2px solid #000 !important; }
    .unified-btn {
        width: 175px !important; height: 50px !important; 
        font-weight: 900 !important; font-size: 18px !important;
        border-radius: 5px !important; border: none !important;
        cursor: pointer; display: flex; align-items: center; justify-content: center;
        background-color: #FF0000 !important; color: #FFF !important;
        margin-top: 10px !important;
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
        digits = [int(d) for d in num_str]
        num_set = set(digits)
        
        # 1. 胆码过滤 (只要号码里含有胆码中的任意一个即保留)
        if manual_d and not (manual_chars & set(num_str)): continue
        
        # 2. 和值过滤
        if sum(digits) in killed_sums: continue
        
        # 3. 跨度过滤
        if (max(digits) - min(digits)) in killed_spans: continue
        
        # 4. 顺子过滤 (顺序无关，支持循环顺子，只要包含连号组合就杀)
        is_killed_shunzi = False
        for n in killed_consecutives:
            for start_digit in range(10):
                # 构建顺子模板，支持 9-0-1 等循环
                shunzi_set = {(start_digit + j) % 10 for j in range(n)}
                # 只要号码中凑齐了顺子模板的所有数字
                if shunzi_set.issubset(num_set):
                    is_killed_shunzi = True
                    break
            if is_killed_shunzi: break
        if is_killed_shunzi: continue
        
        # 5. 形态过滤
        counts = sorted(Counter(digits).values(), reverse=True)
        type_str = ""
        if counts == [4]: type_str = "AAAA"
        elif counts == [3, 1]: type_str = "AAAB"
        elif counts == [2, 2]: type_str = "AABB"
        elif counts == [2, 1, 1]: type_str = "AABC"
        else: type_str = "ABCD"
        
        if type_str in killed_types: continue
        
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
    c_in, c_btn = st.columns([1, 1])
    with c_in:
        manual_d = st.text_input("输入胆码 (如 234):", key="manual_input")
        st.markdown(f"### 剩余注数: {st.session_state.count}")
    
    with c_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 立即计算"):
            res = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                              tuple(st.session_state.killed_types), 
                              tuple(st.session_state.killed_consecutives), 
                              tuple(st.session_state.killed_sums))
            st.session_state.res_text = " ".join(res)
            st.session_state.count = len(res)
            st.rerun()
            
        copy_text = st.session_state.res_text.replace("'", "\\'")
        components.html(f"""
        <button id="copyBtn" class="unified-btn" onclick="
            navigator.clipboard.writeText('{copy_text}');
            var btn = document.getElementById('copyBtn');
            btn.innerText = '✅ 已复制';
            setTimeout(function() {{ btn.innerText = '📋 复制结果'; }}, 2000);
        ">📋 复制结果</button>
        """, height=70)

    st.markdown(f'<div class="preview-box">{st.session_state.res_text}</div>', unsafe_allow_html=True)
