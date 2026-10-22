# 📊 AI 智能核价与风控看板 (AI Costing & Risk Control Dashboard)

这是一个基于 Python + Streamlit + LangChain 开发的 AI 采购核价提效工具。专为解决制造业、电子代工厂等行业中，采购与核价人员面临的“BOM表物料多、人工核算慢、比价易出错、审批邮件撰写繁琐”等真实业务痛点而设计。

🔗 **在线体验 Demo:** [点击这里访问公网应用](https://costing-tool-3qnj3p9p58fsypxnjxag9k-misaka.streamlit.app/)

## ✨ 核心功能

1. **秒级智能算账**：一键上传 Excel 报价表，基于 pandas 秒级计算所有物料的总成本。
2. **智能异常预警**：自动比对历史单价与客户预算价，揪出涨幅 > 8% 或超预算的异常物料，并用红色高亮展示。
3. **数据清洗与兼容**：内置智能列名映射与脏数据清洗机制。无论表头叫“单价”、“报价”还是“Unit Price”，甚至价格带有“元”字，代码都能自动兼容识别。
4. **AI 商务邮件生成**：无缝接入 DeepSeek 大模型（基于 LangChain），一键根据异常物料清单，生成格式专业、逻辑清晰的调价审批邮件，支持一键复制。
5. **现代 B 端 UI**：基于 Streamlit 深度定制的现代化数据看板，包含数据指标卡片、Plotly 交互式环形图，完全隐藏原生 UI，视觉效果媲美商业 SaaS 产品。

## 🛠️ 技术栈

- **前端 & 部署**: Streamlit (自定义 HTML/CSS 深度美化), Streamlit Community Cloud
- **数据处理**: pandas, openpyxl
- **数据可视化**: Plotly Express
- **AI 大模型编排**: LangChain, DeepSeek API (兼容 OpenAI 格式)
- **安全性**: 使用 Streamlit Secrets 隐藏大模型 API Key

## 🚀 本地运行指南

如果你想在本地运行或进行二次开发：

1. 克隆仓库：
   ```bash
   git clone https://github.com/misaka9988/costing-tool.git
   cd costing-tool
   
2.安装依赖：
pip install -r requirements.txt

3.配置环境变量：
在项目根目录新建 .env 文件，填入你的 DeepSeek API Key：DEEPSEEK_API_KEY="sk-你的真实API_KEY"

4.启动应用：
streamlit run web_page.py

📝 业务背景

在传统采购环节中，面对几百颗料，核价员往往需要花费 1-2 天时间手动计算和比价，且极易出错。

等审批流程走完，往往错过最佳锁价期，导致缺货或供应商涨价。本项目通过自动化脚本与大模型，将这一过程缩短至秒级，极大降低了人工对账成本与断供风险。


## ⚠️ 免责声明 (Disclaimer)

1. 本项目仅供技术学习、交流与内部效率测试使用。
2. 本代码包含调用第三方大模型 API（如 DeepSeek 等）的逻辑。**请绝对不要将包含公司机密、真实商业底价、客户隐私的未经脱敏的 Excel 数据上传至公有云环境。**
3. 使用者在实际商业场景中使用本代码时，须自行承担遵守所在公司数据安全合规政策的全部责任。
4. 作者不对因使用本项目、或因为使用者操作不当导致的任何数据泄露、经济损失承担任何连带法律责任。
