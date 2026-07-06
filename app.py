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
    
    /* 0-9 数字的固定色彩系统 */
    .n0 { color: #FF5733; } .n1 { color: #FFD700; } .n2 { color: #87CEEB; }
    .n3 { color: #33FF57; } .n4 { color: #FF33A1; } .n5 { color: #00FFFF; }
    .n6 { color: #FF8C00; } .n7 { color: #ADFF2F; } .n8 { color: #FF00FF; } .n9 { color: #FFFFFF; }
    
    .preview-box { 
        background-color: #000 !important; padding: 15px !important; border-radius: 5px !important; 
        height: 450px !important; overflow-y: auto !important; border: 2px solid #000 !important;
        margin-top: 10px !important; font-family: monospace; font-weight: bold; font-size: 17px;
    }
    
    /* 饱满的大红色注数 */
    .highlight-count { 
        color: #FF0000 !important; 
        font-size: 40px !important; 
        font-weight: 900 !important; 
        text-shadow: 2px 2px 8px rgba(255, 0, 0, 0.4) !important;
        margin-left: 10px !important;
    }
    
    /* 核心按钮动画交互逻辑 */
    div.stButton > button, .unified-btn {
        height: 50px !important; font-weight: 900 !important; font-size: 16px !important;
        border-radius: 10px !important; border: none !important; transition: all 0.2s ease !important;
        display: flex !important; align-items: center !important; justify-content: center !important; cursor: pointer !important;
    }
    /* 悬停提亮 */
    div.stButton > button:hover, .unified-btn:hover { filter: brightness(1.2) !important; box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important; }
    /* 点击缩胀 */
    div.stButton > button:active, .unified-btn:active { transform: scale(0.95) !important; }

    /* 按钮颜色 */
    div.stButton > button { background-color: #FFD700 !important; color: #000 !important; width: 100% !important; }
    .unified-btn { background-color: #f0f0f0 !important; color: #333 !important; border: 1px solid #ccc !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d)
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        num_set = set(digits)
        if manual_d and not (manual_chars & set(num_str)): continue
        if sum(digits) in killed_sums: continue
        if (max(digits) - min(digits)) in killed_spans: continue
        is_killed_shunzi = False
        for n in killed_consecutives:
            for s in range(10):
                if {(s + j) % 10 for j in range(n)}.issubset(num_set):
                    is_killed_shunzi = True; break
            if is_killed_shunzi: break
        if is_killed_shunzi: continue
        counts = sorted(Counter(digits).values(), reverse=True)
        type_str = "ABCD"
        if counts == [4]: type_str = "AAAA"
        elif counts == [3, 1]: type_str = "AAAB"
        elif counts == [2, 2]: type_str = "AABB"
        elif counts == [2, 1, 1]: type_str = "AABC"
        if type_str in killed_types: continue
        results.append(num_str)
    return results

if 'res_list' not in st.session_state: st.session_state.res_list = []
for k in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if k not in st.session_state: st.session_state[k] = set()

@st.fragment
def render_right_panel():
    c_in, c_btns = st.columns([1, 2])
    with c_in:
        manual_d = st.text_input("输入胆码 (如 234):", key="manual_input")
    
    with c_btns:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        b1, b2, _ = st.columns([1, 1, 1])
        with b1:
            if st.button("🚀 立即计算"):
                st.session_state.res_list = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                                                        tuple(st.session_state.killed_types), 
                                                        tuple(st.session_state.killed_consecutives), 
                                                        tuple(st.session_state.killed_sums))
        with b2:
            if st.session_state.res_list:
                copy_text = " ".join(st.session_state.res_list).replace("'", "\\'")
                components.html(f"""
                <button id="copyBtn" class="unified-btn" onclick="
                    navigator.clipboard.writeText('{copy_text}');
                    this.innerText = '✅ 已复制';
                    setTimeout(() => this.innerText = '📋 复制结果', 2000);
                ">📋 复制结果</button>
                """, height=60)

    st.markdown(f"### 剩余注数: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    
    preview_html = "<div style='display:flex; flex-wrap:wrap;'>"
    for num in st.session_state.res_list[:300]:
        colored_num = "".join([f"<span class='n{d}'>{d}</span>" for d in num])
        preview_html += f"<div style='margin-right:15px; margin-bottom:5px;'>{colored_num}</div>"
    preview_html += "</div>"
    
    if len(st.session_state.res_list) > 300: preview_html += "<br>... (仅预览前300注)"
    st.markdown(f'<div class="preview-box">{preview_html}</div>', unsafe_allow_html=True)

st.title("⚡ 极速缩水工具")
col_l, col_r = st.columns([1, 1])

with col_l:
    st.subheader("过滤面板")
    for key, label, items in [('killed_spans', '跨度过滤', range(10)), 
                              ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]),
                              ('killed_consecutives', '顺子过滤', [2, 3, 4]),
                              ('killed_sums', '和值过滤', range(37))]:
        st.markdown(f"**{label}**")
        cols = st.columns(10)
        for idx, item in enumerate(items):
            if cols[idx % 10].checkbox(str(item), value=item in st.session_state[key], key=f"cb_{key}_{item}"):
                st.session_state[key].add(item)
            elif item in st.session_state[key]:
                st.session_state[key].remove(item)

with col_r:
    st.subheader("计算面板")
    render_right_panel()
