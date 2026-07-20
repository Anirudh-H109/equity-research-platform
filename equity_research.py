import yfinance as yf
import pandas as pd
from groq import Groq
import streamlit as st

client = Groq(api_key=st.secrets["GROQ_API_KEY"])


def get_financials(ticker_symbol):
    ticker=yf.Ticker(ticker_symbol)
    info=ticker.info
    financials=ticker.financials

    return {
        "info":info,
        "financials":financials
    }

def data_pull(data):
    info=data["info"]
    fin=data["financials"]

    gp=fin.loc["Gross Profit"].iloc[0]
    tr=fin.loc["Total Revenue"].iloc[0]
    ni=fin.loc["Net Income"].iloc[0]
    data_required ={
        "Total Revenue": fin.loc["Total Revenue"].iloc[0],
        "Net Income": fin.loc["Net Income"].iloc[0],
        "EBITDA": fin.loc["EBITDA"].iloc[0],
        "Gross Profit": fin.loc["Gross Profit"].iloc[0],
        "Market Cap": info.get("marketCap"),
        "P/E Ratio": info.get("trailingPE"),
        "EPS": info.get("trailingEps"),
        "EV": info.get("enterpriseValue"),
        "gross_margin":gp/tr*100,
        "net_margin":ni/tr*100,
        "rev_growth":(tr-fin.loc["Total Revenue"].iloc[1])/fin.loc["Total Revenue"].iloc[1]*100,
        "Debt/Equity":info.get("debtToEquity")/100,
        "ROE":info.get("returnOnEquity")*100
    }
    return data_required


def score_company(data):
    my_data = data_pull(data)
    
    # P/E ratio
    if 15 <= my_data["P/E Ratio"] <= 20:
        pe_score = 1
    elif 20 < my_data["P/E Ratio"] < 35:
        pe_score = 2
    else:
        pe_score = 0

    # Gross Margin
    gm = my_data["gross_margin"]
    if gm > 40:
        gm_score = 2
    elif 20 <= gm <= 40:
        gm_score = 1
    else:
        gm_score = 0

    # Net Margin
    nm = my_data["net_margin"]
    if nm > 20:
        nm_score = 2
    elif 10 <= nm <= 20:
        nm_score = 1
    else:
        nm_score = 0

    # Revenue Growth (Fixed: changed 'nm' to 'rg')
    rg = my_data["rev_growth"]
    if rg > 10:
        rg_score = 2
    elif 5 <= rg <= 10:
        rg_score = 1
    else:
        rg_score = 0

    # DE Ratio
    de = my_data["Debt/Equity"]
    # Handle case if Debt/Equity is missing (None)
    if de is None:
        de_score = 0
    elif de < 1:
        de_score = 2
    elif 1 <= de <= 2:
        de_score = 1
    else:
        de_score = 0

    # Return on Equity (Fixed: changed 'nm' to 'roe')
    roe = my_data["ROE"]
    if roe is None:
        roe_score = 0
    elif roe > 20:
        roe_score = 2
    elif 12 <= roe <= 20:
        roe_score = 1
    else:
        roe_score = 0

    # EV/EBITDA (Fixed: changed 1510 to an 'else' block to catch everything else)
    ev_ebidta = my_data["EV"] / my_data["EBITDA"]
    if ev_ebidta < 10:
        ee_score = 2
    elif 10 <= ev_ebidta <= 15:
        ee_score = 1
    else:
        ee_score = 0
    
    total_score = (1.5 * (gm_score + nm_score + pe_score + ee_score)) + de_score + roe_score + rg_score
    if total_score > 12:
        verdict = "Buy"
    elif 6 <= total_score <= 12:
        verdict = "Hold"
    else:
        verdict = "Sell"
    
    return {
        "Verdict": verdict,
        "Scores": {
            "P/E": pe_score,
            "EV/Ebitda": ee_score,
            "GM": gm_score,
            "NM": nm_score,
            "DE": de_score,
            "RG": rg_score,
            "ROE": roe_score
        },
        "Final Weight": total_score
    }


def prepare_prompt(ticker):
    data=get_financials(ticker)
    data_given=data_pull(data)
    recommendation=score_company(data)
    system_prompt= f"""
    You are a senior equity research analyst at a top-tier investment bank. 
    You will be given a company's financial metrics along with scores (0, 1, or 2) 
    representing Bad, Average, and Good respectively, and a final verdict of Buy, Hold, or Sell.

    Generate a professional but user-friendly equity research report with exactly these sections:

    1. Company Overview — briefly describe what the company does and its market position
    2. Financial Analysis — for each metric provided, explain what the score means in plain English and why it matters
    3. Valuation — assess whether the stock is cheap or expensive based on the valuation metrics provided
    4. Risk Factors — identify 2-3 key risks based on the weak scores or market conditions
    5. Investment Recommendation — state the Buy/Hold/Sell verdict clearly and explain the reasoning behind it in 2-3 sentences

    Tone: professional but accessible to a non-expert investor
    Length: 400-600 tokens
    Important: base your analysis strictly on the scores and metrics provided — do not invent numbers or make assumptions beyond what is given
    """
    
    prompt = f"""
    Company Analysis Request:
    
    Market Cap: {data_given["Market Cap"]}
    P/E Ratio: {data_given["P/E Ratio"]}
    EPS: {data_given["EPS"]}
    EV:{data_given["EV"]}
    
    Financial Statements (Most Recent Year):
    Total Revenue: {data_given["Total Revenue"]}
    Net Income: {data_given["Net Income"]}
    EBITDA: {data_given["EBITDA"]}
    Gross Profit: {data_given["Gross Profit"]}
    Gross Margin:{data_given["gross_margin"]}
    Net Margin: {data_given["net_margin"]}
    Revenue Growth: {data_given["rev_growth"]}
    Debt To Equity: {data_given["Debt/Equity"]}
    Return on Equity: {data_given["ROE"]}

    Verdict According to my Engine:
    Verdict:{recommendation["Verdict"]}
    Score for each Parameter:{recommendation["Scores"]}
    Total Score out of 18: {recommendation["Final Weight"]}
    
    
    """
    
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ],
    max_tokens=1024
    )
    return response.choices[0].message.content
    
    





# print(data["info"]["marketCap"])
# print(data["financials"].loc["Total Revenue"].iloc[0])