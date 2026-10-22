import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 尝试加载本地的 .env 文件（如果你在本地跑，它会读取这里的 Key）
load_dotenv()

def generate_approval_email(bad_items_text: str) -> str:
    # 💡 核心修改：优先从 Streamlit 的云端 Secrets 拿 Key，拿不到再去本地环境变量找
    api_key = st.secrets.get("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY"))
    
    llm = ChatOpenAI(
        model="deepseek-flash", 
        api_key=api_key, 
        base_url="https://api.deepseek.com",
        temperature=0.3
    )
    
    prompt = f"""
    你现在是一家大型电子代工厂（MRO/MES背景）的资深采购专员。
    现在有一批物料的供应商突然大幅涨价，或者超出了客户给定的预算价。
    如果不尽快向客户申请差额审批，我们将面临缺货风险，导致交期延误。
    
    请根据以下异常物料清单，写一封发给客户的【调价审批邮件】。
    
    异常物料清单如下：
    {bad_items_text}
    
    要求：
    1. 语气要专业、委婉，但必须强调“缺货风险”和“交期紧迫性”，促使客户尽快批复。
    2. 邮件包含：主题、称呼、说明情况（列出物料和涨幅）、说明风险、期望客户动作、结尾。
    3. 不要废话，直接输出邮件正文。
    """
    
    response = llm.invoke(prompt)
    return response.content