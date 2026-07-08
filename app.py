import streamlit as st
import random
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
    .n0 { color: #FF5733; } .n1 { color: #FFD700; } .n2 { color: #87CEEB; }
    .n3 { color: #33FF57; } .n4 { color: #FF33A1; } .n5 { color: #00FFFF; }
    .n6 { color: #FF8C00; } .n7 { color: #ADFF2F; } .n8 { color: #FF00FF; } .n9 { color: #FFFFFF; }
    .preview-box { 
        background-color: #000 !important; padding: 15px !important; border-radius: 5px !important; 
        height: 450px !important; overflow-y: auto !important; border: 2px solid #000 !important;
        margin-top: 10px !important; font-family: monospace; font-weight: bold; font-size: 17px;
    }
    .highlight-count { color: #FF0000 !important; font-size: 40px !important; font-weight: 900 !important; }
    div.stButton > button { background-color: #FFD700 !important; color: #000 !important; height: 50px !important; width: 100% !important; font-weight: 900 !important; border-radius: 10px !important; }
    .unified-btn { background-color: #f0f0f0 !important; color: #333 !important; padding: 12px; border-radius: 10px; cursor: pointer; text-align: center; font-weight: 900; border: 1px solid #ccc; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 初始化 ---
if 'res_list' not in st.session_state: st.session_state.res_list = []
if 'refresh_val' not in st.session_state: st.session_state.refresh_val = 0

# --- 计算逻辑 ---
def get_results(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
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

# --- 主布局 ---
st.title("⚡ 极速缩水工具")
col_l, col_r = st.columns([1, 1])

# 过滤面板
with col_l:
    st.subheader("过滤面板")
    filters = {
        'killed_spans': {'label': '跨度过滤', 'items': range(10)},
        'killed_types': {'label': '形态过滤', 'items': ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]},
        'killed_consecutives': {'label': '顺子过滤', 'items': [2, 3, 4]},
        'killed_sums': {'label': '和值过滤', 'items': range(37)}
    }
    for key, info in filters.items():
        if key not in st.session_state: st.session_state[key] = set()
        st.markdown(f"**{info['label']}**")
        cols = st.columns(10)
        for idx, item in enumerate(info['items']):
            chk = cols[idx % 10].checkbox(str(item), key=f"chk_{key}_{item}")
            if chk: st.session_state[key].add(item)
            elif item in st.session_state[key]: st.session_state[key].remove(item)

# 计算面板
with col_r:
    st.subheader("计算面板")
    c_in, c_btns = st.columns([1, 2])
    manual_d = c_in.text_input("输入胆码:", key="manual_input")
    
    if c_btns.button("🚀 立即计算"):
        st.session_state.res_list = get_results(manual_d, tuple(st.session_state.killed_spans), 
                                                tuple(st.session_state.killed_types), 
                                                tuple(st.session_state.killed_consecutives), 
                                                tuple(st.session_state.killed_sums))
        st.session_state.refresh_val = random.random()

    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    
    if st.session_state.res_list:
        copy_text = " ".join(st.session_state.res_list)
        st.markdown(f"""
        <div class="unified-btn" onclick="navigator.clipboard.writeText('{copy_text}'); alert('已复制全部结果');">📋 复制结果</div>
        """, unsafe_allow_html=True)
        
        # --- 修复核心：使用 container 代替在 markdown 中传 key ---
        preview = st.session_state.res_list[:300]
        html_content = "".join([f"<div style='margin-right:15px; margin-bottom:5px;'>{''.join([f'<span class=\"n{d}\">{d}</span>' for d in num])}</div>" for num in preview])
        
        # container 拥有 key 参数，这才是强制刷新的正确姿势
        with st.container(key=f"refresh_{st.session_state.refresh_val}"):
            st.markdown(f'<div class="preview-box" style="display:flex; flex-wrap:wrap;">{html_content}</div>', unsafe_allow_html=True)
