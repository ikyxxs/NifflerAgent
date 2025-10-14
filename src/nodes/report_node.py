from langchain_core.messages import SystemMessage, HumanMessage

from src.config import CACHE_DIR
from src.constatns.prompt import SYSTEM_PROMPT_REPORT_ANALYSIS, SYSTEM_PROMPT_EXTRACT_HOLDINGS
from src.tools import coze
from src.tools.coze import upload_file_to_coze
from src.tools.llm import get_llm
from src.tools.md_tool import markdown2pdf
from src.tools.strategy_tool import strategy_json_to_markdown


def receive_report(state):
    """PDF转Markdown"""
    file = state.get("file")
    file_id = upload_file_to_coze(file)
    file_content = coze.pdf2markdown(file_id)

    # 更新思考过程
    thoughts = [f"接收到研报《{file.name}》"]

    # 更新状态，传递给下一个节点
    return {"file_id": file_id, "file_content": file_content, "thoughts": thoughts}

    # 测试代码
    # file_content = "Goldman | Poroi sratey Sachs Research \n18 September 2025 | 3:37AM HKT \n## China Musings \n## What to do with China equities? Investor FAOs on China's (liquidity) bull market \nWhat’s the trigger for the recent rally? US$3tn of market cap has been added 1. in HK/China ytd, and CSI300/1000 has rallied 18%/23% since June. We think “reflation” expectations and AI (self-sufficiency) could be the key catalysts. \nKinger Lau, CFA +852-2978-1224 | kinger.lau@gs.com Goldman Sachs (Asia) L.L.C. \nSi Fu, Ph.D. +852-2978-0200 | si.fu@gs.com Goldman Sachs (Asia) L.L.C. \nHow do you contextual this bull run? Valuation/liquidity-powered equity 2. booms are not unique to China. Importantly, normalized profits are growing on a mid-to-high-single digit pace on our forecast. \nTimothy Moe, CFA +65-6889-1199 | timothy.moe@gs.com Goldman Sachs (Singapore) Pte \nHow sustainable? How likely is a “slow bull” market? Earnings are needed 3. for longevity, but “liquidity” is a necessary condition for all bull trends. The setup for a “slow bull’ market seems better constructed now than before in A shares. \nKevin Wang, CFA +852-2978-2446 | kevin.wang@gs.com Goldman Sachs (Asia) L.L.C. \nHow to gauge overheating risks? We recommend our revamped A-share Retail 4. Sentiment Proxy as a comprehensive measure for onshore risk appetite. It currently stands at 1.3, pointing to market consolidation risks but not a reversal. \nWho’s buying? Popular narrative says retail investors, but data show that 5. Chinese and foreign institutional investors have been key liquidity sponsors to this rally. \nHow much could Chinese households allocate to equities? Trillions of dollars 6. anchored by Rmb160tn in deposits and Rmb330tn in real estate, but the allocation shifts will be gradual and long-lasting. \nHow much could institutions allocate to equities? Rmb32tn/Rmb40tn of 7. potential buying for onshore equities if institutional ownership there were to rise to 50% (EM average)/59% (DM average) from 14% now. \nAre valuations stretched? Not by most metrics for large caps. Index PEs are at 8. mid-range, implying that upside liquidity optionality remains attractively priced in both A and H shares. \nWhat could reverse the bull trend? Policy shocks, namely abrupt liquidity 9. tightening, regulation changes, and policy disappointments. We introduce a new tool to monitor policy risk in the stock market. \nWhat to do with China equities? We stay Overweight A and H shares, forecast 10. 8% and 3% 12m upside respectively, suggest accumulating on dips, and like the Prominent 10, AI, anti-involution, and shareholder return themes/portfolios. \nInvestors should consider this report as only a single factor in making their investment decision. For Reg AC certification and other important disclosures, see the Disclosure Appendix, or go to www.gs.com/research/hedge.html.\nGoldman Sachs \nChina Musings \n## 1) What’s the trigger for the recent rally? \nThe “DeepSeek” moment in late January arguably kick-started the broad n China equity uptrend, with the POE Symposium in February, moderation in US-China tensions starting in late-April, and other industry specific and liquidity factors (e.g. compressing HIBOR in 2Q, a reviving IPO market in HK, and record-breaking Southbound flows) all subsequently contributing to the 35% ytd gains for MSCI China. \nWhile lagging their offshore counterparts for much of 1H25 and with cap-weighted n A-H premium for dual-listed stocks falling to 6-year lows (30%) at one point, A shares began to catch up in late 2Q, coinciding with the CCFEA meeting chaired by President Xi on July 1 where the anti-involution campaign was specifically emphasized. CSI300 has surged 26% since the lows in April, propelling index ytd gains to 15%. \nFrom a macro perspective, market expectations for intensifying policy n focus/execution centering on rationalizing supply, improving the pricing environment for general goods and services, and alleviating profitless competition among corporates has probably helped shore up inflation expectations, thereby triggering a reflation trade in the financial markets. Indeed, 10-year bond yields have risen 16bp and underperformed domestic equities by 16% since July 1, accompanied by noticeable fund flow rotation from bonds to equities during the same time. \nn Thematically, the acceleration of China’s technology self-reliance, as evidenced by the launch of DeepSeek’s V3.1 in late August, may have added fuel to the upswing, especially for onshore AI proxies which are concentrated in the upstream AI design and semiconductor manufacturing cohorts compared to the Offshore market where hyperscalers, data/cloud operators, and application-focused companies are dominating the AI Tech ecosystem by market cap. \nExhibit 1: The rally in A shares has been accompanied by meaningful fund rotation from bonds to equities \nExhibit 2: AI proxies, notably upstream semi cohorts, have led the A-share rally of late \n![fig_84544](https://p3-flow-imagex-sign.byteimg.com/ocean-cloud-tos/pdf/"
    # return {"file_id": '123', "file_content": file_content, "thoughts": thoughts}


def report_analysis(state):
    """分析研报生成投资策略JSON"""
    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("分析研报")

    # 处理文件内容
    file = state.get("file")
    file_content = state.get("file_content", '')
    addition = state.get("addition")

    # 构建提示词
    user_prompt = f"""
            研报内容
            {file_content}
            ---
            分析研报内容并建立投资策略。输出的策略使用中文。输出格式为JSON
            """
    if not addition:
        user_prompt = f"""
            研报内容
            {file_content}
            ---
            补充信息
            {addition}
            ---
            分析研报内容并建立投资策略。如果有补充信息，结合补充信息进行更正。输出的策略使用中文。输出格式为JSON
            """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT_REPORT_ANALYSIS),
        HumanMessage(content=user_prompt)
    ]

    # 调用OpenAI API
    try:
        llm = get_llm()
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        answer = f"分析研报失败: {str(e)}"
        thoughts.append(f"分析研报失败: {str(e)}")

    # 测试代码
    # answer = open("strategy_json.txt", "r", encoding="utf-8").read()

    # 持久化(临时先用本地文件代替)
    with open(CACHE_DIR + '/' + file.name + ".txt", "w", encoding="utf-8") as file:
        file.writelines(answer)

    # 返回最终结果
    return {"thoughts": thoughts, "strategy_json": answer}


def extract_holdings(state):
    """提取研报中的持仓信息"""
    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("[提取研报中的持仓信息](#研报中的持仓信息)")

    # 处理文件内容
    file_content = state.get("file_content", '')

    # 构建提示词
    messages = [
        SystemMessage(content=SYSTEM_PROMPT_EXTRACT_HOLDINGS),
        HumanMessage(content=file_content)
    ]

    # 调用OpenAI API
    try:
        llm = get_llm()
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        answer = f"分析研报失败: {str(e)}"
        thoughts.append(f"分析研报失败: {str(e)}")

    # 测试代码
    # answer = open("holdings.txt", "r", encoding="utf-8").read()

    if len(answer) > 10 and '-' in answer and '|' in answer:
        return {"thoughts": thoughts, "holdings": answer}

    # 返回最终结果
    return {"thoughts": thoughts, "holdings": "无"}


def generate_strategy_markdown(state):
    """生成投资策略Markdown"""
    strategy_json = state.get('strategy_json')
    strategy_markdown = strategy_json_to_markdown(strategy_json)

    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("[生成投资策略 Markdown](#投资策略)")

    return {"thoughts": thoughts, "strategy_markdown": strategy_markdown}


def generate_strategy_pdf(state):
    """生成投资策略PDF"""
    file = state.get("file")
    file_name = f"《{file.name}》投资策略"
    strategy_markdown = state.get("strategy_markdown")
    strategy_pdf = markdown2pdf(file_name, strategy_markdown)

    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("生成投资策略 PDF")

    # 更新状态，传递给下一个节点
    return {"file": state.get('file'), "strategy_pdf": strategy_pdf, "thoughts": thoughts}
