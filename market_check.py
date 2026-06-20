import yfinance as yf
import os
import smtplib
import csv
from datetime import datetime
from email.mime.text import MIMEText

# ===== データ取得 =====

# 米国市場
vix = yf.Ticker("^VIX")
spy = yf.Ticker("SPY")
qqq = yf.Ticker("QQQ")
usdjpy = yf.Ticker("JPY=X")

# 日本市場（全体）
nikkei = yf.Ticker("^N225")      # 日経平均
topix = yf.Ticker("1306.T")      # TOPIX ETF
mothers = yf.Ticker("^JSDAQ")    # マザーズ系

# 日本セクター
semi = yf.Ticker("8035.T")       # 東京エレクトロン（半導体代表）
bank = yf.Ticker("8306.T")       # 三菱UFJ（銀行代表）
auto = yf.Ticker("7203.T")       # トヨタ（自動車代表）
softbank = yf.Ticker("9984.T")   # ソフトバンクG（テック代表）
lasertec = yf.Ticker("6920.T")   # レーザーテック

# ===== 価格取得関数 =====
def get_change(ticker):
    try:
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            return None
        return (hist["Close"].iloc[-1] / hist["Close"].iloc[-2] - 1) * 100
    except:
        return None

def get_price(ticker):
    try:
        hist = ticker.history(period="1d")
        if len(hist) == 0:
            return None
        return hist["Close"].iloc[-1]
    except:
        return None

# ===== 各データ取得 =====
vix_price     = get_price(vix)
spy_change    = get_change(spy)
qqq_change    = get_change(qqq)
usdjpy_price  = get_price(usdjpy)

nikkei_change   = get_change(nikkei)
topix_change    = get_change(topix)
semi_change     = get_change(semi)
bank_change     = get_change(bank)
auto_change     = get_change(auto)
softbank_change = get_change(softbank)
lasertec_change = get_change(lasertec)

# ===== 判定 =====
if vix_price is None:
    result = "データ取得失敗"
elif vix_price < 20:
    result = "通常積立"
elif vix_price < 30:
    result = "+5万円検討"
elif vix_price < 40:
    result = "+15万円検討"
else:
    result = "+30万円検討"

# セクター強弱判定
def sector_signal(change):
    if change is None:
        return "－"
    elif change > 1.5:
        return f"🔥 強い (+{change:.1f}%)"
    elif change > 0:
        return f"↑ (+{change:.1f}%)"
    elif change > -1.5:
        return f"↓ ({change:.1f}%)"
    else:
        return f"❄️ 弱い ({change:.1f}%)"

# ===== CSV蓄積 =====
today = datetime.now().strftime("%Y-%m-%d")
csv_file = "market_history.csv"

row = [
    today,
    round(vix_price, 2) if vix_price else "",
    round(spy_change, 2) if spy_change else "",
    round(qqq_change, 2) if qqq_change else "",
    round(usdjpy_price, 2) if usdjpy_price else "",
    round(nikkei_change, 2) if nikkei_change else "",
    round(topix_change, 2) if topix_change else "",
    round(semi_change, 2) if semi_change else "",
    round(bank_change, 2) if bank_change else "",
    round(auto_change, 2) if auto_change else "",
    round(softbank_change, 2) if softbank_change else "",
    round(lasertec_change, 2) if lasertec_change else "",
    result
]

file_exists = os.path.exists(csv_file)
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow([
            "日付","VIX","SP500","NASDAQ","USDJPY",
            "日経平均","TOPIX","東京エレクトロン","三菱UFJ","トヨタ",
            "ソフトバンクG","レーザーテック","判定"
        ])
    writer.writerow(row)

# ===== メール =====
gmail_user = os.environ["GMAIL_USER"]
gmail_pass = os.environ["GMAIL_PASS"]

body = f"""
📈 市場レポート {today}

【米国市場】
VIX:        {vix_price:.2f} → {result}
S&P500:     {spy_change:.2f}%
NASDAQ:     {qqq_change:.2f}%
ドル円:      {usdjpy_price:.2f}

【日本市場】
日経平均:          {sector_signal(nikkei_change)}
TOPIX:             {sector_signal(topix_change)}

【セクター強弱】
半導体(東エレク):  {sector_signal(semi_change)}
銀行(三菱UFJ):     {sector_signal(bank_change)}
自動車(トヨタ):    {sector_signal(auto_change)}
テック(SBG):       {sector_signal(softbank_change)}
レーザーテック:    {sector_signal(lasertec_change)}

------------------
💡 本日の判定: {result}
"""

msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = f"【投資ボット】{today} 市場レポート"
msg["From"] = gmail_user
msg["To"] = gmail_user

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(gmail_user, gmail_pass)
server.send_message(msg)
server.quit()

print(body)
