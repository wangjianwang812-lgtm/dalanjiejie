import streamlit as st
import streamlit.components.v1 as components
from collections import Counter

# --- 页面基础配置（原样不动）
st.set_page_config(page_title="极速缩水工具", layout="wide")

# --- 界面样式完全原版，一字未改
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

# 4连顺子专用跨0判断函数，2/3顺子沿用原版逻辑不变
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

# 核心计算函数（完全还原你最初业务逻辑，仅补全4连循环顺）
@st.cache_data(max_entries=20)
def cached_calc(manual_d, killed_spans, killed_types, killed_consecutives, killed_sums):
    results = []
    manual_chars = set(manual_d.strip()) if manual_d.strip() else None
    # 遍历全部10000个四位数
    for i in range(10000):
        num_str = f"{i:04d}"
        digits = [int(d) for d in num_str]
        num_set = set(num_str)

        # 第一层筛选：输入3位数字，只要包含任意一个就保留，完全不含直接剔除（基础池7599）
        if manual_chars is not None and manual_chars.isdisjoint(num_set):
            continue
        
        # 和值过滤 原版逻辑
        if sum(digits) in killed_sums:
            continue
        # 跨度过滤 原版逻辑
        span_val = max(digits) - min(digits)
        if span_val in killed_spans:
            continue

        # 顺子逻辑：2、3位完全原版，4位叠加跨0判断，全部功能齐全
        is_killed = False
        for n in killed_consecutives:
            hit = False
            # 2连、3连顺子 原版代码不动
            if n in (2,3):
                for s in range(10):
                    seq_check = {(s + j) % 10 for j in range(n)}
                    if seq_check.issubset(num_set):
                        hit = True
                        break
            # 4连顺子：原版判断 + 跨0循环判断
            elif n == 4:
                for s in range(10):
                    seq_check = {(s + j) % 10 for j in range(4)}
                    if seq_check.issubset(num_set):
                        hit = True
                        break
                if not hit:
                    hit = check_4_loop_seq(num_set)
            if hit:
                is_killed = True
                break
        if is_killed:
            continue
        
        # 形态判断 原版完整逻辑无修改
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

# ========== 修复1：正确初始化会话状态，彻底解决KeyError报错 ==========
if 'res_list' not in st.session_state:
    st.session_state.res_list = []
filter_keys = ['killed_spans', 'killed_types', 'killed_consecutives', 'killed_sums']
# 正确判断：不存在才创建空集合，不会页面崩溃
for k in filter_keys:
    if k not in st.session_state:
        st.session_state[k] = set()

# 计算面板，固定key不失效，复制防长文本ws报错
@st.fragment
def render_right_panel():
    c_in, c_btns = st.columns([1, 2])
    with c_in:
        manual_d = st.text_input("输入3位号码:", key="manual_input_fixed")
    with c_btns:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        b1, b2, _ = st.columns([1, 1, 1])
        with b1:
            if st.button("🚀 立即缩水", key="calc_btn_fixed"):
                st.session_state.res_list = cached_calc(manual_d, 
                                                        tuple(st.session_state.killed_spans), 
                                                        tuple(st.session_state.killed_types), 
                                                        tuple(st.session_state.killed_consecutives), 
                                                        tuple(st.session_state.killed_sums))
        with b2:
            if st.session_state.res_list:
                full_copy_str = " ".join(st.session_state.res_list)
                safe_text = full_copy_str.replace("`", "\\`").replace('"', '\\"').replace("'", "\\'")
                copy_html = f"""
                <script>window.tempCopyData = `{safe_text}`;</script>
                <button class="unified-btn" onclick="
                    navigator.clipboard.writeText(window.tempCopyData);
                    this.innerText='✅ 已复制';
                    setTimeout(()=>this.innerText='📋 复制结果', 2000);
                ">📋 复制结果</button>
                """
                components.html(copy_html, height=60)

    # 结果数量展示
    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    
    # 预览逻辑原版不动，展示前300条
    if st.session_state.res_list:
        preview = st.session_state.res_list[:300]
        html_list = [f"<div style='margin-right:15px; margin-bottom:5px;'>{''.join([f'<span class=\"n{d}\">{d}</span>' for d in num])}</div>" for num in preview]
        preview_html = f"<div style='display:flex; flex-wrap:wrap;'>{''.join(html_list)}</div>"
        if len(st.session_state.res_list) > 300:
            preview_html += "<br>... (已隐藏剩余结果，点击复制即可获取全部)"
        st.markdown(f'<div class="preview-box">{preview_html}</div>', unsafe_allow_html=True)

# 页面布局、左侧过滤面板完全和你截图一致，无删减
st.title("⚡ 极速缩水工具")
col_l, col_r = st.columns([1, 1])
with col_l:
    st.subheader("过滤面板")
    for key, label, items in [
        ('killed_spans', '跨度过滤', range(10)),
        ('killed_types', '形态过滤', ["AAAA", "AAAB", "AABB", "AABC", "ABCD"]),
        ('killed_consecutives', '顺子过滤', [2, 3, 4]),
        ('killed_sums', '和值过滤', range(37))
    ]:
        st.markdown(f"**{label}**")
        cols = st.columns(10)
        for idx, item in enumerate(items):
            cb_key = f"cb_{key}_{item}"
            selected = cols[idx % 10].checkbox(str(item), value=item in st.session_state[key], key=cb_key)
            if selected:
                st.session_state[key].add(item)
            elif item in st.session_state[key]:
                st.session_state[key].remove(item)
with col_r:
    st.subheader("计算面板")
    render_right_panel()
