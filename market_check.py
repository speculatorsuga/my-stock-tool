import yfinance as yf
import os
import smtplib
from email.mime.text import MIMEText

# データ取得
vix = yf.Ticker("^VIX")
spy = yf.Ticker("SPY")
qqq = yf.Ticker("QQQ")
usdjpy = yf.Ticker("JPY=X")

vix_price = vix.history(period="1d")["Close"].iloc[-1]

spy_hist = spy.history(period="2d")
spy_change = (spy_hist["Close"].iloc[-1] / spy_hist["Close"].iloc[-2] - 1) * 100

qqq_hist = qqq.history(period="2d")
qqq_change = (qqq_hist["Close"].iloc[-1] / qqq_hist["Close"].iloc[-2] - 1) * 100

usdjpy_price = usdjpy.history(period="1d")["Close"].iloc[-1]

# 判定
result = (
    "通常積立" if vix_price < 20 else
    "+5万円検討" if vix_price < 30 else
    "+15万円検討" if vix_price < 40 else
    "+30万円検討"
)

# メール設定
gmail_user = os.environ["GMAIL_USER"]
gmail_pass = os.environ["GMAIL_PASS"]

body = f"""
📈 市場レポート

VIX: {vix_price:.2f}
S&P500(SPY): {spy_change:.2f}%
NASDAQ(QQQ): {qqq_change:.2f}%
USDJPY: {usdjpy_price:.2f}

------------------
判定: {result}
"""

msg = MIMEText(body)
msg["Subject"] = "【投資ボット】市場レポート"
msg["From"] = gmail_user
msg["To"] = gmail_user

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(gmail_user, gmail_pass)
server.send_message(msg)
server.quit()
