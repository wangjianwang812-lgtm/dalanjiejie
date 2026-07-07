import streamlit as st
import streamlit.components.v1 as components
from collections import Counter

# --- 页面配置 ---
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- UI 样式完全原样保留，无修改 ---
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

# 全局一次性预生成全部10000条四位数预计算数据（启动仅运行一次）
if "all_full_data" not in st.session_state:
    full_list = []
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(c) for c in num_str]
        num_set = set(digits)
        sum_val = sum(digits)
        span_val = max(digits) - min(digits)
        count_sort = sorted(Counter(digits).values(), reverse=True)
        if count_sort == [4]:
            form = "AAAA"
        elif count_sort == [3, 1]:
            form = "AAAB"
        elif count_sort == [2, 2]:
            form = "AABB"
        elif count_sort == [2, 1, 1]:
            form = "AABC"
        else:
            form = "ABCD"
        full_list.append((num_str, num_set, sum_val, span_val, form))
    st.session_state.all_full_data = full_list

# 顺子判断函数（兼容2/3/4连、跨0循环顺，无功能缺失）
def seq_kill_check(num_set, seq_len):
    num_list = list(num_set)
    extend_nums = num_list + [x + 10 for x in num_list]
    for start in extend_nums:
        hit = True
        for offset in range(1, seq_len):
            if (start + offset) % 10 not in num_set:
                hit = False
                break
        if hit:
            return True
    return False

@st.cache_data(max_entries=15, ttl=1800)
def calc_filter(three_input, kill_span, kill_form, kill_seq, kill_sum):
    full_data = st.session_state.all_full_data
    input_digits = set(three_input.strip()) if three_input.strip() and len(three_input.strip()) == 3 and three_input.strip().isdigit() else None
    step1_pool = []
    # 第一步：筛选基础池 仅保留包含输入3码任意一个数字的号码（7599条，直接剔除剩余2401条）
    for item in full_data:
        num_str, num_set, sum_v, span_v, form_v = item
        if input_digits is not None:
            # 完全不含输入3个数字 → 直接排除，不进入后续过滤
            if input_digits.isdisjoint(num_set):
                continue
        step1_pool.append(item)
    # 第二步：在7599条基础池内执行所有勾选过滤（跨度/形态/顺子/和值，支持全部多选）
    final_result = []
    for item in step1_pool:
        num_str, num_set, sum_v, span_v, form_v = item
        # 跨度剔除
        if span_v in kill_span:
            continue
        # 和值剔除
        if sum_v in kill_sum:
            continue
        # 形态剔除
        if form_v in kill_form:
            continue
        # 顺子剔除（2/3/4连全部生效）
        seq_hit = False
        for sl in kill_seq:
            if seq_kill_check(num_set, sl):
                seq_hit = True
                break
        if seq_hit:
            continue
        final_result.append(num_str)
    return final_result

# ====================== 修复点1：修正会话状态初始化逻辑，彻底解决KeyError ======================
if 'res_list' not in st.session_state:
    st.session_state.res_list = []
filter_keys = ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']
# 正确逻辑：判断key是否不存在于session_state，而非filter_keys列表
for k in filter_keys:
    if k not in st.session_state:
        st.session_state[k] = set()

# 计算面板固定逻辑，按钮点击稳定不失效
@st.fragment
def calc_panel():
    col_input, col_btn_area = st.columns([1, 2])
    with col_input:
        three_code = st.text_input("输入3位号码:", key="input_3num", placeholder="例：148")
    with col_btn_area:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        btn_calc, btn_copy, _ = st.columns([1, 1, 1])
        with btn_calc:
            click_run = st.button("🚀 立即缩水", key="btn_calc_run")
            if click_run:
                st.session_state.res_list = calc_filter(
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
                <script>window.copyStorage = `{safe_text}`;</script>
                <button class="unified-btn" onclick="
                    navigator.clipboard.writeText(window.copyStorage);
                    this.innerText='✅ 已复制';
                    setTimeout(()=>this.innerText='📋 复制结果', 2000);
                ">📋 复制结果</button>
                """
                components.html(copy_html, height=60)
    # 结果数量展示
    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    # 预览前300条，不影响完整复制功能
    if st.session_state.res_list:
        preview_show = st.session_state.res_list[:300]
        html_items = []
        for num in preview_show:
            span_html = "".join([f'<span class="n{d}">{d}</span>' for d in num])
            html_items.append(f"<div style='margin-right:15px; margin-bottom:5px;'>{span_html}</div>")
        preview_box_html = f"<div style='display:flex; flex-wrap:wrap;'>{''.join(html_items)}</div>"
        if len(st.session_state.res_list) > 300:
            preview_box_html += "<br>... (仅预览前300条，复制按钮导出全部)"
        st.markdown(f'<div class="preview-box">{preview_box_html}</div>', unsafe_allow_html=True)

# 主页面布局完全和截图一致
st.title("⚡ 极速缩水工具")
col_left_filter, col_right_calc = st.columns([1, 1])
with col_left_filter:
    st.subheader("过滤面板")
    filter_group_list = [
        ('killed_spans', '跨度过滤', range(10)),
        ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]),
        ('killed_consecutives', '顺子过滤', [2, 3, 4]),
        ('killed_sums', '和值过滤', range(37))
    ]
    for state_key, title, item_list in filter_group_list:
        st.markdown(f"**{title}**")
        row_cols = st.columns(10)
        for idx, val in enumerate(item_list):
            ck_key = f"ck_{state_key}_{val}"
            selected = row_cols[idx % 10].checkbox(str(val), value=val in st.session_state[state_key], key=ck_key)
            if selected:
                st.session_state[state_key].add(val)
            elif val in st.session_state[state_key]:
                st.session_state[state_key].remove(val)
with col_right_calc:
    st.subheader("计算面板")
    calc_panel()
