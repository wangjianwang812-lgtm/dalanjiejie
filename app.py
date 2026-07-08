import streamlit as st
from collections import Counter
import streamlit.components.v1 as components

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 ---
st.markdown("""
    <style>
    /* 缩短输入框 */
    [data-testid="stTextInput"] { max-width: 300px !important; }
    
    .block-container { padding-top: 1rem !important; }
    #MainMenu, header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #87CEEB !important; }
    
    .preview-box { 
        background-color: #000 !important; padding: 15px !important; border-radius: 5px !important; 
        height: 450px !important; overflow-y: auto !important; border: 2px solid #000 !important;
        margin-top: 10px !important; font-family: monospace; font-size: 17px;
        color: #fff !important; white-space: pre-wrap !important;
    }
    .highlight-count { color: #FF0000 !important; font-size: 40px !important; font-weight: 900 !important; }
    
    /* 按钮基础动效 */
    div.stButton > button { 
        background-color: #FFD700 !important; color: #000 !important; height: 50px !important; 
        width: 100% !important; font-weight: 900 !important; border-radius: 10px !important; 
        border: none !important; transition: all 0.2s ease !important; cursor: pointer !important;
    }
    div.stButton > button:hover { filter: brightness(1.15) !important; transform: scale(1.02) !important; }
    div.stButton > button:active { transform: scale(0.95) !important; }
    </style>
""", unsafe_allow_html=True)

# --- 状态与逻辑 ---
if 'res_list' not in st.session_state: st.session_state.res_list = []
for k in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if k not in st.session_state: st.session_state[k] = set()

def calc_logic(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d)
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        num_set = set(digits)
        if manual_d and not (manual_chars & set(num_str)): continue
        if sum(digits) in killed_sums: continue
        if (max(digits) - min(digits)) in killed_spans: continue
        is_killed = False
        for n in killed_consecutives:
            for s in range(10):
                if {(s + j) % 10 for j in range(n)}.issubset(num_set):
                    is_killed = True; break
            if is_killed: break
        if is_killed: continue
        counts = sorted(Counter(digits).values(), reverse=True)
        type_str = "ABCD"
        if counts == [4]: type_str = "AAAA"
        elif counts == [3, 1]: type_str = "AAAB"
        elif counts == [2, 2]: type_str = "AABB"
        elif counts == [2, 1, 1]: type_str = "AABC"
        if type_str in killed_types: continue
        results.append(num_str)
    return results

# --- 界面布局 ---
st.title("⚡ 极速缩水工具")
col_l, col_r = st.columns([1, 1])

with col_l:
    st.subheader("过滤面板")
    for key, label, items in [('killed_spans', '跨度过滤', range(10)), ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]), ('killed_consecutives', '顺子过滤', [2, 3, 4]), ('killed_sums', '和值过滤', range(37))]:
        st.markdown(f"**{label}**")
        cols = st.columns(10)
        for idx, item in enumerate(items):
            if cols[idx % 10].checkbox(str(item), value=item in st.session_state[key], key=f"chk_{key}_{item}"):
                st.session_state[key].add(item)
            elif item in st.session_state[key]:
                st.session_state[key].remove(item)

with col_r:
    st.subheader("计算面板")
    manual_d = st.text_input("输入胆码:", key="manual_input")
    b1, _ = st.columns([1, 2])
    if b1.button("🚀 立即计算"):
        st.session_state.res_list = calc_logic(manual_d, st.session_state.killed_spans, st.session_state.killed_types, st.session_state.killed_consecutives, st.session_state.killed_sums)

    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    
    if st.session_state.res_list:
        data_to_copy = " ".join(st.session_state.res_list)
        # 集成复制组件，并为其添加与 St 按钮一致的 Hover/Active 动效
        components.html(f"""
        <button id="copy-btn" style="
            background:#f0f0f0; border:1px solid #ccc; padding:12px; border-radius:10px; width:100%; 
            font-weight:900; cursor:pointer; transition: all 0.2s;
        " onmouseover="this.style.filter='brightness(1.15)'; this.style.transform='scale(1.02)';" 
           onmouseout="this.style.filter='brightness(1.0)'; this.style.transform='scale(1.0)';"
           onmousedown="this.style.transform='scale(0.95)';"
           onmouseup="this.style.transform='scale(1.02)';"
           onclick="
            const text = `{data_to_copy}`;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copy-btn');
                btn.innerText = '✅ 已复制全部';
                setTimeout(() => {{ btn.innerText = '📋 复制结果'; }}, 2000);
            }});
        ">📋 复制结果</button>
        """, height=60)
        
        st.markdown(f'<div class="preview-box">{" ".join(st.session_state.res_list[:500])} ... (已省略部分预览)</div>', unsafe_allow_html=True)
