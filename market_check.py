import yfinance as yf

vix = yf.Ticker("^VIX")
spy = yf.Ticker("SPY")
qqq = yf.Ticker("QQQ")
usdjpy = yf.Ticker("JPY=X")

vix_price = vix.history(period="1d")["Close"].iloc[-1]

spy_hist = spy.history(period="2d")
spy_change = ((spy_hist["Close"].iloc[-1] / spy_hist["Close"].iloc[-2]) - 1) * 100

qqq_hist = qqq.history(period="2d")
qqq_change = ((qqq_hist["Close"].iloc[-1] / qqq_hist["Close"].iloc[-2]) - 1) * 100

usdjpy_price = usdjpy.history(period="1d")["Close"].iloc[-1]

print("📈 市場状況")
print("------------------")
print(f"VIX: {vix_price:.2f}")
print(f"S&P500(SPY): {spy_change:.2f}%")
print(f"NASDAQ(QQQ): {qqq_change:.2f}%")
print(f"USDJPY: {usdjpy_price:.2f}")
print("------------------")

if vix_price < 20:
    print("判定: 通常積立")
elif vix_price < 30:
    print("判定: +5万円検討")
elif vix_price < 40:
    print("判定: +15万円検討")
else:
    print("判定: +30万円検討")
