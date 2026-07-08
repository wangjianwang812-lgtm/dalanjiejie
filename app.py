import streamlit as st
import streamlit.components.v1 as components
from collections import Counter
import random

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 (完全保留你的原样式与布局) ---
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
    .highlight-count { 
        color: #FF0000 !important; font-size: 40px !important; font-weight: 900 !important;
        text-shadow: 2px 2px 8px rgba(255, 0, 0, 0.4) !important; margin-left: 10px !important;
    }
    div.stButton > button, .unified-btn {
        height: 50px !important; font-weight: 900 !important; font-size: 16px !important;
        border-radius: 10px !important; border: none !important; transition: all 0.2s ease !important;
        display: flex !important; align-items: center !important; justify-content: center !important; cursor: pointer !important;
    }
    div.stButton > button:hover, .unified-btn:hover { filter: brightness(1.2) !important; box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important; }
    div.stButton > button:active, .unified-btn:active { transform: scale(0.95) !important; }
    div.stButton > button { background-color: #FFD700 !important; color: #000 !important; width: 100% !important; }
    .unified-btn { background-color: #f0f0f0 !important; color: #333 !important; border: 1px solid #ccc !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# --- 核心计算函数 (无缓存，确保重复点击能够即时重新计算) ---
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

# --- 状态与 Key 安全初始化 (彻底消灭 KeyError) ---
if 'res_list' not in st.session_state: st.session_state.res_list = []
if 'refresh_key' not in st.session_state: st.session_state.refresh_key = 0

# 预先在全局声明所有复选框的 Key 状态映射，避免动态渲染造成的 KeyError
filter_configs = [
    ('killed_spans', '跨度过滤', list(range(10))), 
    ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]), 
    ('killed_consecutives', '顺子过滤', [2, 3, 4]), 
    ('killed_sums', '和值过滤', list(range(37)))
]

for key, _, items in filter_configs:
    if key not in st.session_state: 
        st.session_state[key] = set()
    for item in items:
        # 预先给每一个可能的 checkbox 键值在 session_state 中注册默认开关状态
        cb_key = f"cb_{key}_{item}"
        if cb_key not in st.session_state:
            st.session_state[cb_key] = (item in st.session_state[key])

# --- 右侧计算面板渲染函数 ---
@st.fragment
def render_right_panel():
    c_in, c_btns = st.columns([1, 2])
    with c_in:
        manual_d = st.text_input("输入胆码:", key="manual_input")
    with c_btns:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        b1, b2, _ = st.columns([1, 1, 1])
        with b1:
            if st.button("🚀 立即计算", key="calc_btn_trigger"):
                # 显式读取当前所有复选框状态同步到集合中
                for key, _, items in filter_configs:
                    st.session_state[key] = {item for item in items if st.session_state.get(f"cb_{key}_{item}", False)}
                
                # 执行计算并生成新的刷新标记
                st.session_state.res_list = get_results(
                    manual_d, 
                    tuple(st.session_state.killed_spans), 
                    tuple(st.session_state.killed_types), 
                    tuple(st.session_state.killed_consecutives), 
                    tuple(st.session_state.killed_sums)
                )
                st.session_state.refresh_key = random.random()
        with b2:
            if st.session_state.res_list:
                copy_text = " ".join(st.session_state.res_list).replace("'", "\\'")
                components.html(f"""
                <button class="unified-btn" onclick="navigator.clipboard.writeText('{copy_text}'); this.innerText='✅ 已复制'; setTimeout(()=>this.innerText='📋 复制结果', 2000);">📋 复制结果</button>
                """, height=60)

    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    
    # 渲染优化：通过批量拼接 HTML 以及加入 refresh_key 确保数据即时刷新且不卡顿
    if st.session_state.res_list:
        preview = st.session_state.res_list[:300]
        html_list = [f"<div style='margin-right:15px; margin-bottom:5px;'>{''.join([f'<span class=\"n{d}\">{d}</span>' for d in num])}</div>" for num in preview]
        preview_html = f"<div style='display:flex; flex-wrap:wrap;'>{''.join(html_list)}</div>"
        if len(st.session_state.res_list) > 300: preview_html += "<br>... (已隐藏剩余结果，点击复制即可获取全部)"
        st.markdown(f'<div class="preview-box" data-ref="{st.session_state.refresh_key}">{preview_html}</div>', unsafe_allow_html=True)

# --- 主页面布局 ---
st.title("⚡ 极速缩水工具")
col_l, col_r = st.columns([1, 1])

with col_l:
    st.subheader("过滤面板")
    for key, label, items in filter_configs:
        st.markdown(f"**{label}**")
        cols = st.columns(10)
        for idx, item in enumerate(items):
            cb_key = f"cb_{key}_{item}"
            # 使用静态注册好的稳定 Key 渲染勾选框
            is_checked = cols[idx % 10].checkbox(str(item), key=cb_key)
            if is_checked:
                st.session_state[key].add(item)
            else:
                st.session_state[key].discard(item)

with col_r:
    st.subheader("计算面板")
    render_right_panel()
