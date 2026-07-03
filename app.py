import streamlit as st
import streamlit.components.v1 as components
from collections import Counter

# --- CSS 样式 ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
        border: 1px solid #e0e0e0;
        padding: 15px !important;
        border-radius: 10px;
        margin-bottom: 15px !important;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 5px #eee;
    }
    h3 { color: #d63384 !important; font-size: 18px !important; margin-bottom: 10px !important; }
    div.stButton > button { padding: 4px 8px !important; font-size: 14px !important; font-weight: 600 !important; height: 35px !important; width: 100%; margin: 2px !important; }
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

def has_consecutive_simple(num_str, n):
    digits = [int(d) for d in num_str]
    for i in range(len(digits) - (n - 1)):
        if all(abs(digits[i+j] - digits[i+j+1]) == 1 for j in range(n - 1)): return True
    return False

def has_custom_four_consecutive(num_str, manual_d):
    d_set = {int(d) for d in manual_d if d.isdigit()}
    num_digits = [int(d) for d in num_str]
    current_num_set = set(num_digits)
    for i in range(10):
        c_set = {(i + j) % 10 for j in range(4)}
        if c_set.issubset(current_num_set):
            if c_set & d_set: return True
    return False

def get_final_numbers(manual_d, btn_status, killed_spans, killed_types, killed_consecutives, killed_sums):
    btn_kill = {k for k, v in btn_status.items() if v == "kill"}
    all_bold = {char for char in manual_d if char.isdigit()} | {k for k, v in btn_status.items() if v == "bold"}
    full_pool = []
    for i in range(10000):
        num_str = f"{i:04d}"
        digits_int = [int(d) for d in num_str]
        if {d for d in num_str} & btn_kill: continue
        if all_bold and not ({d for d in num_str} & all_bold): continue
        if (max(digits_int) - min(digits_int)) in killed_spans: continue
        if get_num_type(num_str) in killed_types: continue
        if 4 in killed_consecutives:
            if has_custom_four_consecutive(num_str, manual_d): continue
        if any(has_consecutive_simple(num_str, n) for n in killed_consecutives if n < 4): continue
        if sum(digits_int) in killed_sums: continue
        full_pool.append(num_str)
    return full_pool

# --- 界面展示 ---
st.set_page_config(layout="wide")
st.title("🎯 终极缩水遥控工作台")

if 'btn_status' not in st.session_state: st.session_state.btn_status = {str(i): "none" for i in range(10)}
for k in ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']:
    if k not in st.session_state: st.session_state[k] = set()

# 侧边栏：使用 text_area 代替 text_input，text_area 的粘贴兼容性远好于 text_input
st.sidebar.header("数字控制")
st.sidebar.markdown("请在下方框内使用 **Ctrl+V** 粘贴胆码：")
manual_d = st.sidebar.text_area("胆码 (支持粘贴):", value="", height=80, max_chars=10)

cols = st.sidebar.columns(5)
for i in range(10):
    curr = st.session_state.btn_status[str(i)]
    type_map = {"bold": "primary", "kill": "secondary", "none": "secondary"}
    if cols[i % 5].button(str(i), key=f"b_{i}", type=type_map[curr]):
        st.session_state.btn_status[str(i)] = {"none":"bold", "bold":"kill", "kill":"none"}[curr]
        st.rerun()

# 模块化渲染 (逻辑不变)
for label, state_key, items, col_count in [
    ("跨度杀码", "killed_spans", range(10), 10),
    ("类型杀码", "killed_types", ["AAAA", "AAAB", "AABB", "AABC", "ABCD"], 5),
    ("连号杀码", "killed_consecutives", [2, 3, 4], 3),
    ("和值杀码", "killed_sums", range(37), 19)
]:
    with st.container():
        st.subheader(label)
        cols = st.columns(col_count)
        for idx, item in enumerate(items):
            key = f"{state_key}_{item}"
            is_active = item in st.session_state[state_key]
            btn_label = str(item) + ("连号" if label == "连号杀码" else "")
            if cols[idx % col_count].button(btn_label, key=key, type="primary" if is_active else "secondary"):
                if is_active: st.session_state[state_key].remove(item)
                else: st.session_state[state_key].add(item)
                st.rerun()

# 执行区域
st.subheader("执行区域")
if st.button("🚀 执行缩水计算", type="primary"):
    # 自动处理粘贴进去的杂质，只提取数字
    clean_manual_d = "".join([c for c in manual_d if c.isdigit()])
    st.session_state.last_results = get_final_numbers(clean_manual_d, st.session_state.btn_status, st.session_state.killed_spans, st.session_state.killed_types, st.session_state.killed_consecutives, st.session_state.killed_sums)

if 'last_results' in st.session_state:
    results = st.session_state.last_results
    st.metric("剩余组号结果", len(results))
    page = st.number_input("翻页查看", min_value=1, max_value=max(1, (len(results)//100)+1), value=1)
    st.text_area("结果预览（仅当前页）：", value=" ".join(results[(page-1)*100 : page*100]), height=150)
    
    full_text = " ".join(results)
    copy_js = f"""
    <script>
        function copyAll() {{
            navigator.clipboard.writeText(`{full_text}`).then(() => {{
                alert("已成功复制全部 {len(results)} 条结果！");
            }});
        }}
    </script>
    <button onclick="copyAll()" style="padding:10px; width:100%; font-weight:bold; background:#ff4b4b; color:white; border:none; border-radius:5px; cursor:pointer;">
        📋 一键复制全部 {len(results)} 条结果
    </button>
    """
    components.html(copy_js, height=50)