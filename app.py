with col_right:
    st.subheader("计算面板")
    
    # 将计算面板细分为两列：左侧输入框，右侧放置按钮
    # [3, 1] 的比例可以根据你的视觉喜好调整，数字越小右侧按钮区越宽
    c1, c2 = st.columns([3, 1])
    
    with c1:
        manual_d = st.text_input("输入胆码 (如 234):", key="manual_input")
        st.markdown(f"### 剩余注数: {st.session_state.count}")
    
    with c2:
        # 这里使用垂直占位让按钮对齐输入框顶部
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        
        # 立即计算按钮
        if st.button("🚀 立即计算"):
            res = cached_calc(manual_d, tuple(st.session_state.killed_spans), 
                              tuple(st.session_state.killed_types), 
                              tuple(st.session_state.killed_consecutives), 
                              tuple(st.session_state.killed_sums))
            st.session_state.res_text = " ".join(res)
            st.session_state.count = len(res)
            st.rerun()
            
        # 复制结果按钮
        copy_text = st.session_state.res_text.replace("'", "\\'")
        components.html(f"""
        <button onclick="navigator.clipboard.writeText('{copy_text}'); this.innerText='✅ 已复制';" 
        class="unified-btn" style="background-color: #FF0000; color: #FFF; margin-top: 10px;">
            📋 复制结果
        </button>
        """, height=50)

    st.markdown(f'<div class="preview-box">{st.session_state.res_text}</div>', unsafe_allow_html=True)
