import streamlit as st
import streamlit.components.v1 as components
from collections import Counter

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式完全原样保留，无任何修改 ---
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
    div.stButton > button { background-color: #FFD700 !important; color: #000 !important; width: 100% !important; }
    .unified-btn { background-color: #f0f0f0 !important; color: #333 !important; border: 1px solid #ccc !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# 专用函数：仅处理4位跨0循环顺子（9012、8901这类），2/3位完全沿用原生循环取模逻辑
def check_4_loop_seq(digit_set):
    nums = sorted([int(x) for x in digit_set])
    full_extend = nums + [x + 10 for x in nums]
    for i in range(len(full_extend)):
        start = full_extend[i]
        seq_target = {start, start+1, start+2, start+3}
        real_seq = {num % 10 for num in seq_target}
        if real_seq.issubset(set(nums)):
            return True
    return False

@st.cache_data(max_entries=20)
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d.strip()) if manual_d.strip() else None
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        num_set = set(num_str)

        # 胆码逻辑：包含任意输入数字即保留，原版不变
        if manual_chars is not None and not (manual_chars & num_set):
            continue
        
        # 和值过滤 原版逻辑
        if sum(digits) in killed_sums:
            continue
        # 跨度过滤 原版逻辑
        span_val = max(digits) - min(digits)
        if span_val in killed_spans:
            continue

        # 顺子完整逻辑：2/3位原生取模循环，4位叠加跨0判断，全部功能齐全
        is_killed_seq = False
        for seq_len in killed_consecutives:
            hit = False
            # 2连、3连顺子：完全保留你最初的原版代码，无修改
            if seq_len in (2, 3):
                for start in range(10):
                    seq_check = {(start + j) % 10 for j in range(seq_len)}
                    if seq_check.issubset(num_set):
                        hit = True
                        break
            # 4连顺子：原生判断 + 新增跨0循环顺子判断，双校验不漏杀
            elif seq_len == 4:
                # 先跑原生循环取模判断
                for start in range(10):
                    seq_check = {(start + j) % 10 for j in range(4)}
                    if seq_check.issubset(num_set):
                        hit = True
                        break
                # 原生没命中，再校验跨0循环四连（9012、8901）
                if not hit:
                    hit = check_4_loop_seq(num_set)
            if hit:
                is_killed_seq = True
                break
        if is_killed_seq:
            continue

        # 形态判断 原版完整逻辑不动
        counts = sorted(Counter(digits).values(), reverse=True)
        type_str = "ABCD"
        if counts == [4]:
            type_str = "AAAA"
        elif counts == [3, 1]:
            type_str = "AAAB"
        elif counts == [2, 2]:
            type_str = "AABB"
        elif counts == [2, 1, 1]:
            type_str = "AABC"
        if type_str in killed_types:
            continue

        results.append(num_str)
    return results

# 会话状态初始化，原版不变
if 'res_list' not in st.session_state:
    st.session_state.res_list = []
filter_keys = ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']
for k in filter_keys:
    if k not in st.session_state:
        st.session_state[k] = set()

# 计算面板Fragment（固定key，按钮点击不失效，复制防WebSocket报错）
@st.fragment
def render_right_panel():
    col_input, col_btn_area = st.columns([1, 2])
    with col_input:
        manual_d = st.text_input("输入3位号码:", key="fixed_three_input", placeholder="例：148")
    with col_btn_area:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        btn_calc, btn_copy, _ = st.columns([1, 1, 1])
        with btn_calc:
            click_calc = st.button("🚀 立即缩水", key="fixed_calc_btn")
            if click_calc:
                st.session_state.res_list = cached_calc(
                    manual_d,
                    tuple(st.session_state.killed_spans),
                    tuple(st.session_state.killed_types),
                    tuple(st.session_state.killed_consecutives),
                    tuple(st.session_state.killed_sums)
                )
        with btn_copy:
            if st.session_state.res_list:
                full_text = " ".join(st.session_state.res_list)
                safe_text = full_text.replace("`", "\\`").replace('"', '\\"').replace("'", "\\'")
                copy_html = f"""
                <script>window.copyTextStore = "{safe_text}";</script>
                <button class="unified-btn" onclick="
                    navigator.clipboard.writeText(window.copyTextStore);
                    this.innerText='✅ 已复制';
                    setTimeout(()=>this.innerText='📋 复制结果', 2000);
                ">📋 复制结果</button>
                """
                components.html(copy_html, height=60)

    # 结果计数展示
    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    # 预览前300条，原版逻辑不变
    if st.session_state.res_list:
        preview_data = st.session_state.res_list[:300]
        html_items = []
        for num in preview_data:
            span_digits = "".join([f'<span class="n{d}">{d}</span>' for d in num])
            html_items.append(f"<div style='margin-right:15px; margin-bottom:5px;'>{span_digits}</div>")
        preview_html = f"<div style='display:flex; flex-wrap:wrap;'>{''.join(html_items)}</div>"
        if len(st.session_state.res_list) > 300:
            preview_html += "<br>... (仅预览前300条，点击复制获取全部)"
        st.markdown(f'<div class="preview-box">{preview_html}</div>', unsafe_allow_html=True)

# 页面布局、过滤面板完全和截图一致，无改动
st.title("⚡ 极速缩水工具")
col_filter_left, col_calc_right = st.columns([1, 1])
with col_filter_left:
    st.subheader("过滤面板")
    filter_groups = [
        ('killed_spans', '跨度过滤', range(10)),
        ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]),
        ('killed_consecutives', '顺子过滤', [2, 3, 4]),
        ('killed_sums', '和值过滤', range(37))
    ]
    for state_key, title, item_list in filter_groups:
        st.markdown(f"**{title}**")
        cols_row = st.columns(10)
        for idx, val in enumerate(item_list):
            ck_key = f"ck_{state_key}_{val}"
            selected = cols_row[idx % 10].checkbox(str(val), value=val in st.session_state[state_key], key=ck_key)
            if selected:
                st.session_state[state_key].add(val)
            elif val in st.session_state[state_key]:
                st.session_state[state_key].remove(val)
with col_calc_right:
    st.subheader("计算面板")
    render_right_panel()
