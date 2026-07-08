import streamlit as st
from collections import Counter

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式 (保持原样) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    #MainMenu, header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #87CEEB !important; }
    .preview-box { 
        background-color: #000 !important; padding: 15px !important; border-radius: 5px !important; 
        height: 450px !important; overflow-y: auto !important; border: 2px solid #000 !important;
        margin-top: 10px !important; font-family: monospace; font-weight: bold; font-size: 17px;
        color: #fff !important; white-space: pre-wrap !important;
    }
    .highlight-count { color: #FF0000 !important; font-size: 40px !important; font-weight: 900 !important; }
    div.stButton > button { background-color: #FFD700 !important; color: #000 !important; height: 50px !important; width: 100% !important; font-weight: 900 !important; border-radius: 10px !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- 状态初始化 ---
if 'res_list' not in st.session_state: st.session_state.res_list = []
for k in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if k not in st.session_state: st.session_state[k] = set()

# --- 计算逻辑 ---
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

# --- 布局 ---
st.title("⚡ 极速缩水工具")
col_l, col_r = st.columns([1, 1])

with col_l:
    st.subheader("过滤面板")
    for key, label, items in [('killed_spans', '跨度过滤', range(10)), ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]), ('killed_consecutives', '顺子过滤', [2, 3, 4]), ('killed_sums', '和值过滤', range(37))]:
        st.markdown(f"**{label}**")
        cols = st.columns(10)
        for idx, item in enumerate(items):
            # 修复 KeyError：使用唯一的固定 key
            if cols[idx % 10].checkbox(str(item), value=item in st.session_state[key], key=f"chk_{key}_{item}"):
                st.session_state[key].add(item)
            elif item in st.session_state[key]:
                st.session_state[key].remove(item)

with col_r:
    st.subheader("计算面板")
    manual_d = st.text_input("输入胆码:", key="manual_input")
    b1, b2 = st.columns([1, 1])
    
    with b1:
        if st.button("🚀 立即计算"):
            st.session_state.res_list = calc_logic(manual_d, st.session_state.killed_spans, st.session_state.killed_types, st.session_state.killed_consecutives, st.session_state.killed_sums)
    with b2:
        # 使用原生的复制按钮，无需复杂的组件调用
        if st.button("📋 复制结果"):
            if st.session_state.res_list:
                st.write(f"请手动复制下方内容: {' '.join(st.session_state.res_list)}")
            else:
                st.warning("暂无结果")

    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    
    # 渲染结果：为了性能，直接输出一段高性能文本，不再生成数千个 HTML 标签
    if st.session_state.res_list:
        display_str = " ".join(st.session_state.res_list)
        st.markdown(f'<div class="preview-box">{display_str}</div>', unsafe_allow_html=True)
