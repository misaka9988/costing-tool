import streamlit as st
import pandas as pd
import plotly.express as px
import re
from ai_service import generate_approval_email

st.set_page_config(page_title="AI 核价风控看板", page_icon="📊", layout="wide")

# ================= 核心：智能数据清洗与兼容函数 =================
def smart_column_mapping(df):
    """自动识别同义词列名，将乱表头统一为标准表头"""
    column_aliases = {
        '物料编码': ['物料编码', '料号', '物料编号', '编码', 'Part No', 'Part Number', 'Item'],
        '物料名称': ['物料名称', '名称', '品名', '描述', 'Description', 'Item Name'],
        '历史单价': ['历史单价', '历史价', '原价', '旧价', '基准价', '采购价', '历史采购价'],
        '最新报价': ['最新报价', '单价', '报价', '新价格', '现价', 'Unit Price', 'Price'],
        '采购数量': ['采购数量', '数量', '需求量', '需求数', 'Qty', 'Quantity'],
        '客户预算价': ['客户预算价', '预算价', '目标价', '限价', 'Target Price']
    }
    df.columns = df.columns.astype(str).str.strip()
    rename_dict = {}
    for std_col, aliases in column_aliases.items():
        for alias in aliases:
            matched_cols = [col for col in df.columns if alias.lower() == col.lower()]
            if matched_cols:
                rename_dict[matched_cols[0]] = std_col
                break
    return df.rename(columns=rename_dict)

def clean_numeric_data(df, columns):
    """数据清洗：把 '12.5元', '—', 空格 等强制转换成纯数字"""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True) 
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) 
    return df

# ================= 终极精装修 CSS =================
st.markdown("""
<style>
    /* 1. 隐藏默认UI */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. 全局背景与居中限制 */
    .stApp { background-color: #F8FAFC !important; }
    .block-container {padding-top: 3rem; padding-bottom: 4rem; max-width: 1200px;}
    
    /* 3. 字体与标题 */
    h1 { color: #0F172A !important; font-weight: 800 !important; text-align: center; letter-spacing: -1px;}
    .sub-title { text-align: center; color: #64748B !important; font-size: 18px; margin-bottom: 40px;}
    h2, h3 { color: #0F172A !important; font-weight: 600 !important; margin-bottom: 20px !important;}
    
    /* 4. 卡片容器基础样式 + 悬浮特效 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #F1F5F9 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 30px -4px rgba(79, 70, 229, 0.15) !important;
        border-color: #C7D2FE !important;
    }
    
    /* 5. 主按钮 (流光渐变) */
    .stButton > button {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important; 
        color: #FFFFFF !important;
        border: none !important; border-radius: 10px !important;
        padding: 12px 28px !important; font-weight: 600 !important;
        transition: all 0.3s ease !important; width: 100%;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
    }
    .stButton > button:hover { 
        transform: translateY(-2px) scale(1.02) !important; 
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4) !important;
    }

    /* ================= 6. 终极上传框美化 ================= */
    [data-testid="stFileUploader"] button[title="Add files"],
    [data-testid="stFileUploader"] button[aria-label="Add files"] { display: none !important; }
    [data-testid="stFileUploader"] { max-width: 700px !important; margin: 0 auto !important; }
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important; border: 2px dashed #CBD5E1 !important; 
        border-radius: 16px !important; padding: 24px !important; transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploadDropzone"]:hover { border-color: #4F46E5 !important; background-color: #F8FAFC !important; }
    [data-testid="stFileUploadDropzone"] button {
        background-color: #4F46E5 !important; background-image: none !important;
        border: none !important; border-radius: 8px !important;
        padding: 10px 32px !important; font-weight: 600 !important;
    }
    [data-testid="stFileUploadDropzone"] button * {
        color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; fill: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] section { background-color: transparent !important; border: none !important; padding: 0 !important; }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important; padding: 10px 20px !important;
        width: fit-content !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] div,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] small,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] svg {
        color: #475569 !important; fill: #475569 !important;
    }

    /* ================= 7. 纯 HTML 指标卡片 (绝对等高) ================= */
    [data-testid="column"] { display: flex; flex-direction: column; }
    [data-testid="column"] > div { height: 100%; }
    
    .metric-card {
        background-color: #FFFFFF; border-radius: 16px; padding: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05); border: 1px solid #F1F5F9;
        height: 100% !important; display: flex; flex-direction: column; justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        transform: translateY(-4px); box-shadow: 0 12px 30px -4px rgba(79, 70, 229, 0.15); border-color: #C7D2FE;
    }
    .metric-title { color: #64748B !important; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
    .metric-number { color: #4F46E5 !important; font-size: 36px; font-weight: 800; line-height: 1.2; }
    .metric-footer { margin-top: 12px; min-height: 28px; }
    
    /* 标签徽章 */
    .badge-inverse { display: inline-block; padding: 4px 12px; border-radius: 20px; background-color: #FEE2E2; color: #DC2626; font-size: 13px; font-weight: 600; }
    .badge-normal { display: inline-block; padding: 4px 12px; border-radius: 20px; background-color: #DCFCE7; color: #16A34A; font-size: 13px; font-weight: 600; }

    /* ================= 8. 高级表格 CSS ================= */
    .modern-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .modern-table th { background-color: #F8FAFC; color: #64748B; font-weight: 600; text-align: left; padding: 12px 16px; border-bottom: 1px solid #E2E8F0; }
    .modern-table td { padding: 12px 16px; color: #0F172A; border-bottom: 1px solid #F1F5F9; }
    .modern-table tr:last-child td { border-bottom: none; }
    .modern-table tr:hover { background-color: #F8FAFC; }
    
    /* ================= 9. 邮件正文代码块美化 ================= */
    [data-testid="stCode"] { background-color: #F8FAFC !important; border: none !important; padding: 0 !important; }
    [data-testid="stCode"] pre {
        background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important; padding: 24px !important;
        white-space: pre-wrap !important; word-wrap: break-word !important;
    }
    [data-testid="stCode"] code {
        color: #1E293B !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        font-size: 14px !important; line-height: 1.8 !important; 
    }
    [data-testid="stCode"] .stCodeBlock-toolbar {
        opacity: 1 !important; background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important; border-radius: 6px !important;
        top: 15px !important; right: 15px !important;
    }

    /* 卖点卡片 (首页) */
    .feature-card {
        background-color: #FFFFFF !important; border-radius: 16px; padding: 30px 20px;
        text-align: center; box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #F1F5F9; height: 100%; transition: all 0.3s ease;
    }
    .feature-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px -4px rgba(79, 70, 229, 0.15); border-color: #C7D2FE; }
    .feature-icon { font-size: 40px; margin-bottom: 15px; }
    .feature-title { color: #0F172A !important; font-size: 18px; font-weight: 700; margin-bottom: 10px; }
    .feature-desc { color: #64748B !important; font-size: 14px; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)
# =================================================

st.title("📊 AI 智能核价与风控看板")
st.markdown("<p class='sub-title'>智能解析供应商报价，实时比对历史价格与客户预算，防范断供风险</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("点击或将 Excel 报价表拖拽到这里", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
        # 让用户自定义预警阈值
    threshold = st.slider("⚠️ 设置涨幅预警阈值 (%)", min_value=1, max_value=50, value=8, step=1)
    
    # ================= 智能兼容与清洗 =================
    df = smart_column_mapping(df)
    
    # 核心校验：必须要有报价和数量
    if '最新报价' not in df.columns or '采购数量' not in df.columns:
        st.error("❌ 表格解析失败：未找到【最新报价/单价】或【采购数量】列，请检查表头名称。")
        st.stop()
        
    # 容错处理：缺少某些列时自动补齐
    if '物料名称' not in df.columns:
        df['物料名称'] = df['物料编码'] if '物料编码' in df.columns else '未知物料'
    if '历史单价' not in df.columns:
        df['历史单价'] = df['最新报价']
    if '客户预算价' not in df.columns:
        df['客户预算价'] = 9999999
        
    # 数据强制清洗
    df = clean_numeric_data(df, ['最新报价', '采购数量', '历史单价', '客户预算价'])
    
    # ================= 业务计算 =================
    df['核算总成本'] = df['最新报价'] * df['采购数量']
    total_cost = df['核算总成本'].sum()
    
    # 防除零报错
    df['涨幅比例'] = (df['最新报价'] - df['历史单价']) / df['历史单价']
    df['涨幅比例'] = df['涨幅比例'].replace([float('inf'), -float('inf')], 0).fillna(0)
    
    alerts_df = df[(df['涨幅比例'] > (threshold / 100)) | (df['最新报价'] > df['客户预算价'])]
    
    st.write("") 
    
    # ================= 纯 HTML 指标卡片 =================
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">✅ 本单核算总成本</div>
            <div class="metric-number">¥ {total_cost:,.2f}</div>
            <div class="metric-footer"></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        risk_amount = alerts_df['核算总成本'].sum() if not alerts_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⚠️ 风险物料涉及金额</div>
            <div class="metric-number" style="color: #DC2626 !important;">¥ {risk_amount:,.2f}</div>
            <div class="metric-footer"><span class="badge-inverse">↑ 需重点审批</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🚨 异常物料数量</div>
            <div class="metric-number" style="color: #DC2626 !important;">{len(alerts_df)} <span style="font-size: 20px;">颗</span></div>
            <div class="metric-footer"><span class="badge-normal">↑ 涨幅超标/超预算</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    if not alerts_df.empty:
        col_chart, col_table = st.columns([1, 1.2])
        
        # ================= 图表区域 =================
        with col_chart:
            with st.container(border=True):
                st.markdown("### 📊 成本构成分析")
                fig = px.pie(df, values='核算总成本', names='物料名称', hole=0.6, color_discrete_sequence=px.colors.sequential.Teal)
                fig.update_traces(
                    textposition='inside', textinfo='percent',
                    hovertemplate="<b>%{label}</b><br>金额: ¥%{value:,.2f}<extra></extra>" 
                )
                fig.update_layout(
                    template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                    margin=dict(t=0, b=0, l=0, r=0), height=280, showlegend=False
                )
                st.plotly_chart(fig, width='stretch')
                
        # ================= 表格区域 =================
        with col_table:
            with st.container(border=True):
                st.markdown("### ⚠️ 异常物料清单")
                display_df = alerts_df.copy()
                display_df['涨幅比例'] = display_df['涨幅比例'].apply(lambda x: f"{x:.1%}")
                
                table_html = "<table class='modern-table'><thead><tr>"
                for col in ['物料编码', '物料名称', '历史单价', '最新报价', '涨幅比例']:
                    table_html += f"<th>{col}</th>"
                table_html += "</tr></thead><tbody>"
                for _, row in display_df.iterrows():
                    table_html += f"<tr><td>{row.get('物料编码', '-')}</td><td>{row['物料名称']}</td><td>{row['历史单价']}</td><td>{row['最新报价']}</td><td style='color: #EF4444; font-weight: 600;'>{row['涨幅比例']}</td></tr>"
                table_html += "</tbody></table>"
                
                st.markdown(table_html, unsafe_allow_html=True)
        
        st.write("")
        
        # ================= AI 邮件区域 =================
        with st.container(): 
            st.markdown("### ✉️ AI 智能商务邮件")
            col_btn, col_info = st.columns([1, 3])
            with col_btn:
                generate_btn = st.button("⚡ 一键生成调价邮件")
            with col_info:
                st.markdown("<p style='color:#64748B; margin-top: 10px;'>大模型将基于上述异常清单，自动撰写致客户的催批邮件。</p>", unsafe_allow_html=True)
                
            if generate_btn:
                with st.spinner("AI 正在撰写中..."):
                    bad_items_text = display_df[['物料编码', '物料名称', '历史单价', '最新报价', '涨幅比例']].to_string(index=False)
                    email_draft = generate_approval_email(bad_items_text)
                    st.markdown("### 📋 邮件正文（可直接复制）")
                    st.code(email_draft, language="text")
    else:
        with st.container(border=True):
            st.success("🎉 数据核对完毕，本单所有物料价格正常，无超预算或大幅涨价风险！")

else:
    # ================= 卖点卡片 =================
    st.write("") 
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        st.markdown("<div class='feature-card'><div class='feature-icon'>⚡</div><div class='feature-title'>秒级算账</div><div class='feature-desc'>上传即核算，告别几百颗料手动相乘对账。</div></div>", unsafe_allow_html=True)
    with f_col2:
        st.markdown("<div class='feature-card'><div class='feature-icon'>🛡️</div><div class='feature-title'>智能预警</div><div class='feature-desc'>实时比对历史价与客户预算，自动揪出异常。</div></div>", unsafe_allow_html=True)
    with f_col3:
        st.markdown("<div class='feature-card'><div class='feature-icon'>📧</div><div class='feature-title'>AI 撰写邮件</div><div class='feature-desc'>自动生成致客户的催批调价邮件，一键复制。</div></div>", unsafe_allow_html=True)