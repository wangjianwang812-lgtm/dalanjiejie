import streamlit as st
import streamlit.components.v1 as components
import functools
from collections import Counter

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 (完全保留你的原始 CSS，不动任何布局) ---
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

# --- 核心计算逻辑：精准修复 ---
def get_num_type(digits):
    counts = sorted(Counter(digits).values(), reverse=True)
    if counts == [4]: return "AAAA"
    if counts == [3, 1]: return "AAAB"
    if counts == [2, 2]: return "AABB"
    if counts == [2, 1, 1]: return "AABC"
    return "ABCD"

def is_shunzi(digits, n):
    # n 为 2, 3, 4 代表连号长度
    for i in range(10):
        # 构造顺子模板 (如 012, 123)
        target = [(i + j) % 10 for j in range(n)]
        # 在号码中寻找是否存在该连号序列
        for start in range(len(digits) - n + 1):
            if digits[start:start+n] == target: return True
    return False

@functools.lru_cache(maxsize=16)
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = {int(d) for d in manual_d} if manual_d else set()
    
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        
        # 1. 胆码：只要含有胆码中的数字即可 (符合 7599 逻辑)
        if manual_d and not (manual_chars & set(digits)): continue
        
        # 2. 和值过滤
        if sum(digits) in killed_sums: continue
        
        # 3. 跨度过滤
        if (max(digits) - min(digits)) in killed_spans: continue
        
        # 4. 形态过滤
        if get_num_type(digits) in killed_types: continue
        
        # 5. 顺子过滤 (修复：只有勾选对应顺子长度才过滤)
        if any(is_shunzi(digits, n) for n in killed_consecutives): continue
        
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
