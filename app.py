with col_r:
    st.subheader("计算面板")
    # 缩短输入框宽度
    manual_d = st.text_input("输入胆码:", key="manual_input")
    
    # 将按钮放在同一行，比例设置为 1:1，你可以通过调整 [1, 1] 改变宽度占比
    c1, c2 = st.columns([1, 1])
    
    with c1:
        if st.button("🚀 立即计算"):
            st.session_state.res_list = calc_logic(manual_d, st.session_state.killed_spans, st.session_state.killed_types, st.session_state.killed_consecutives, st.session_state.killed_sums)
    
    with c2:
        # 使用容器让组件在视觉上与按钮对齐
        if st.session_state.res_list:
            data_to_copy = " ".join(st.session_state.res_list)
            # 保持了你要求的 Hover/Active 动效
            components.html(f"""
            <button id="copy-btn" style="
                background:#FFD700; border:none; padding:0; border-radius:10px; width:100%; height: 50px;
                font-weight:900; cursor:pointer; transition: all 0.2s; font-size: 16px;
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
        else:
            # 保持占位，防止页面抖动
            st.markdown('<div style="height:50px"></div>', unsafe_allow_html=True)

    st.markdown(f"### 计算结果: <span class='highlight-count'>{len(st.session_state.res_list)}</span>", unsafe_allow_html=True)
    
    if st.session_state.res_list:
        st.markdown(f'<div class="preview-box">{" ".join(st.session_state.res_list[:500])} ...</div>', unsafe_allow_html=True)
