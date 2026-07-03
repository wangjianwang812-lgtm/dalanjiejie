import streamlit as st
from collections import Counter
import streamlit.components.v1 as components

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    #MainMenu, header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .stApp { background-color: #87CEEB !important; }
    
    /* 强视觉：黑底红字预览区 */
    .preview-box { 
        background-color: #000 !important; 
        color: #ff0000 !important; 
        padding: 15px !important; 
        border-radius: 5px !important; 
        font-family: monospace !important;
        font-weight: bold !important;
        font-size: 16px !important;
        min-height: 100px !important;
        border: 2px solid #000 !important;
    }
    
    /* 自定义黄色按钮样式 */
    div.stButton > button { 
        transition: all 0.1s !important; 
        border-radius: 4px !important; 
        background-color: #FFD700 !important; 
        color: #000 !important; 
        font-weight: bold !important;
        border: none !important;
    }
    div.stButton > button:active { transform: scale(0.95); }
    </style>
""", unsafe_allow_html=True)

# --- 核心计算 ---
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

def get_final_numbers(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d)
    for i in range(10000):
        num_str = f"{i:04d}"
        num_set = set(num_str)
        digits_int = [int(d) for d in num_str]
        if manual_d and not (manual_chars & num_set): continue
        if (max(digits_int) - min(digits_int)) in killed_spans: continue
        if get_num_type(num_str) in killed_types: continue
        if any(check_is_shunzi(num_str, n) for n in killed_consecutives): continue
        if sum(digits_int) in killed_sums: continue
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
                              ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "ABC", "ABCD"]),
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
    
    # 定义占位容器，确保位置固定
    preview_container = st.empty()
    
    # 按钮移到预览上方
    if st.button("🚀 立即计算 (查看最新结果)", use_container_width=True):
        preview_container.markdown('<div class="preview-box">正在计算，请稍候...</div>', unsafe_allow_html=True)
        res = get_final_numbers(manual_d, st.session_state.killed_spans, st.session_state.killed_types, 
                                st.session_state.killed_consecutives, st.session_state.killed_sums)
        st.session_state.res_text = " ".join(res)
        st.session_state.count = len(res)
        st.rerun()
            
    # 预览区域
    if st.session_state.res_text:
        preview = " ".join(st.session_state.res_text.split()[:100])
        preview_container.markdown(f'<div class="preview-box">{preview}</div>', unsafe_allow_html=True)
    else:
        preview_container.markdown('<div class="preview-box">暂无结果</div>', unsafe_allow_html=True)
    
    st.metric("剩余注数", st.session_state.count)
    
    # 复制与下载
    if st.session_state.res_text:
        copy_text = st.session_state.res_text.replace("'", "\\'")
        components.html(f"""
        <button id="copy_btn" onclick="
            navigator.clipboard.writeText('{copy_text}');
            this.innerText = '✅ 全部号码已复制！';
            setTimeout(() => this.innerText = '📋 一键复制全部结果', 2000);
        " style="width:100%; height:50px; background:#ff0000; color:#fff; border:none; border-radius:4px; font-weight:bold; font-size:16px; cursor:pointer;">
            📋 一键复制全部结果
        </button>
        """, height=60)
        st.download_button("💾 下载Txt结果", st.session_state.res_text, "results.txt", use_container_width=True)
