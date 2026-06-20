import os
import smtplib
from email.mime.text import MIMEText

gmail_user = os.environ["GMAIL_USER"]
gmail_pass = os.environ["GMAIL_PASS"]

result = (
    "通常積立" if vix_price < 20 else
    "+5万円検討" if vix_price < 30 else
    "+15万円検討" if vix_price < 40 else
    "+30万円検討"
)

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
