import streamlit as st
from collections import Counter

st.set_page_config(page_title="牛逼缩水工具", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #87CEEB !important; }
    div.stButton > button { background-color: #000000 !important; color: #ffffff !important; border-radius: 4px !important; }
    div.stButton > button[kind="primary"] { background-color: #ff0000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 核心逻辑 ---
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

# --- 状态初始化 ---
if 'results' not in st.session_state: st.session_state.results = ""
if 'count' not in st.session_state: st.session_state.count = 0
for key in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if key not in st.session_state: st.session_state[key] = set()

st.title("🐂 牛逼缩水工具")
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("过滤面板")
    # 这里保持 st.rerun() 以确保交互反馈
    for key, label, items in [('killed_spans', '跨度过滤', list(range(10))), 
                              ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "ABC", "ABCD"]),
                              ('killed_consecutives', '顺子过滤', [2, 3, 4]),
                              ('killed_sums', '和值过滤', list(range(37)))]:
        st.markdown(f"**{label}**")
        for i in range(0, len(items), 10):
            row = items[i:i+10]
            cols = st.columns(len(row))
            for idx, item in enumerate(row):
                if cols[idx].button(str(item), key=f"{key}_{item}", type="primary" if item in st.session_state[key] else "secondary"):
                    if item in st.session_state[key]: st.session_state[key].remove(item)
                    else: st.session_state[key].add(item)
                    st.rerun()

with col_right:
    st.subheader("计算面板")
    manual_d = st.text_input("输入胆码 (如 234):")
    if st.button("🚀 开始缩水计算", type="primary", use_container_width=True):
        res = get_final_numbers(manual_d, st.session_state.killed_spans, st.session_state.killed_types, 
                                st.session_state.killed_consecutives, st.session_state.killed_sums)
        st.session_state.results = " ".join(res)
        st.session_state.count = len(res)
        st.rerun()
    st.metric("剩余注数", st.session_state.count)
    if st.session_state.results:
        st.download_button("💾 下载结果 (导出TXT)", st.session_state.results, "results.txt", use_container_width=True)
    st.text_area("缩水结果:", value=st.session_state.results, height=250)
