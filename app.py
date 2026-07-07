import streamlit as st
import streamlit.components.v1 as components
from collections import Counter

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式完全保留原样 ---
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

# 修复版顺子判断函数，正确识别跨0循环顺子（9,0,1,2）
def has_consecutive_seq(digit_set, seq_len):
    digit_list = sorted([int(x) for x in digit_set])
    full_digits = digit_list + [d + 10 for d in digit_list]
    for i in range(len(full_digits)):
        start = full_digits[i]
        target_seq = [start + offset for offset in range(seq_len)]
        all_exist = True
        for num in target_seq:
            real_num = num % 10
            if real_num not in digit_list:
                all_exist = False
                break
        if all_exist:
            return True
    return False

@st.cache_data(max_entries=20)
def cached_calc(three_code, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    input_code = three_code.strip()
    target_digits = set(input_code) if len(input_code) == 3 and input_code.isdigit() else None

    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        num_set = set(num_str)

        # 1. 三码筛选：完全不含输入3个数字直接剔除
        if target_digits is not None:
            if target_digits.isdisjoint(num_set):
                continue

        # 2. 跨度过滤
        span_val = max(digits) - min(digits)
        if span_val in killed_spans:
            continue

        # 3. 和值过滤
        sum_val = sum(digits)
        if sum_val in killed_sums:
            continue

        # 4. 顺子过滤（修复后无报错，支持9012循环四连顺）
        skip_seq = False
        for seq_n in killed_consecutives:
            if has_consecutive_seq(num_set, seq_n):
                skip_seq = True
                break
        if skip_seq:
            continue

        # 5. 形态过滤
        count_list = sorted(Counter(digits).values(), reverse=True)
        form_type = "ABCD"
        if count_list == [4]:
            form_type = "AAAA"
        elif count_list == [3, 1]:
            form_type = "AAAB"
        elif count_list == [2, 2]:
            form_type = "AABB"
        elif count_list == [2, 1, 1]:
            form_type = "AABC"
        if form_type in killed_types:
            continue

        results.append(num_str)
    return results

# 会话状态初始化
if 'res_list' not in st.session_state:
    st.session_state.res_list = []
filter_keys = ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']
for k in filter_keys:
    if k not in st.session_state:
        st.session_state[k] = set()

# 计算面板Fragment（固定Key，防止点击失效）
@st.fragment()
def render_right_panel():
    col_input, col_btn_area = st.columns([1, 2])
    with col_input:
        three_code = st.text_input("输入3位号码:", key="fixed_three_input", placeholder="例：148")
    with col_btn_area:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        btn_calc, btn_copy, _ = st.columns([1, 1, 1])
        with btn_calc:
            click_calc = st.button("🚀 立即缩水", key="fixed_calc_btn")
            if click_calc:
                st.session_state.res_list = cached_calc(
                    three_code,
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

    # 结果数量展示
    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    # 预览最多300条
    if st.session_state.res_list:
        preview_data = st.session_state.res_list[:300]
        html_items = []
        for num in preview_data:
            span_digits = "".join([f'<span class="n{d}">{d}</span>' for d in num])
            html_items.append(f"<div style='margin-right:15px; margin-bottom:5px;'>{span_digits}</div>")
        preview_html = f"<div style='display:flex; flex-wrap:wrap;'>{''.join(html_items)}</div>"
        if len(st.session_state.res_list) > 300:
            preview_html += "<br>... (预览仅展示前300条，点击复制获取全部)"
        st.markdown(f'<div class="preview-box">{preview_html}</div>', unsafe_allow_html=True)

# 主页面布局完全和截图一致，无改动
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
