import yfinance as yf
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

today = datetime.now().strftime("%Y-%m-%d")

# ===== データ取得関数 =====
def get_price(symbol):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="1d")
        return hist["Close"].iloc[-1] if len(hist) > 0 else None
    except:
        return None

def get_change(symbol):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d")
        if len(hist) < 2:
            return None
        return (hist["Close"].iloc[-1] / hist["Close"].iloc[-2] - 1) * 100
    except:
        return None

# ===== 米国市場 =====
vix_price     = get_price("^VIX")
spy_change    = get_change("SPY")
qqq_change    = get_change("QQQ")
usdjpy_price  = get_price("JPY=X")

# ===== 日本株セクター（時価総額トップ5） =====
sectors = {
    "半導体・AI": {
        "東京エレクトロン": "8035.T",
        "ソニーグループ":   "6758.T",
        "キーエンス":       "6861.T",
        "アドバンテスト":   "6857.T",
        "レーザーテック":   "6920.T",
    },
    "テック・DX": {
        "ソフトバンクG":         "9984.T",
        "富士通":               "6702.T",
        "NTTデータG":           "9613.T",
        "NEC":                  "6701.T",
        "さくらインターネット": "3778.T",
    },
    "銀行・金融": {
        "三菱UFJ":       "8306.T",
        "三井住友":       "8316.T",
        "みずほ":         "8411.T",
        "三井住友トラスト":"8309.T",
        "りそなHD":       "8308.T",
    },
    "保険": {
        "東京海上HD":     "8766.T",
        "MS&ADインシュアランス": "8725.T",
        "SOMPOホールディングス": "8630.T",
        "第一生命HD":     "8750.T",
        "T&Dホールディングス":   "8795.T",
    },
    "自動車": {
        "トヨタ":         "7203.T",
        "ホンダ":         "7267.T",
        "日産":           "7201.T",
        "デンソー":       "6902.T",
        "アイシン":       "7259.T",
    },
    "精密機器": {
        "キヤノン":       "7751.T",
        "ニコン":         "7731.T",
        "オリンパス":     "7733.T",
        "HOYA":           "7741.T",
        "テルモ":         "4543.T",
    },
    "防衛": {
        "三菱重工":       "7011.T",
        "川崎重工":       "7012.T",
        "IHI":            "7013.T",
        "住友重機械":     "6302.T",
        "NEC":            "6701.T",
    },
    "小売・消費": {
        "ファーストリテイリング": "9983.T",
        "セブン＆アイ":         "3382.T",
        "イオン":               "8267.T",
        "ニトリ":               "9843.T",
        "MonotaRO":             "3064.T",
    },
    "医療・ヘルスケア": {
        "武田薬品":       "4502.T",
        "アステラス製薬": "4503.T",
        "第一三共":       "4568.T",
        "エーザイ":       "4523.T",
        "塩野義製薬":     "4507.T",
    },
    "不動産": {
        "三井不動産":     "8801.T",
        "三菱地所":       "8802.T",
        "住友不動産":     "8830.T",
        "東急不動産HD":   "3289.T",
        "野村不動産HD":   "3231.T",
    },
    "エネルギー・資源": {
        "ENEOS HD":       "5020.T",
        "出光興産":       "5019.T",
        "三菱商事":       "8058.T",
        "三井物産":       "8031.T",
        "住友商事":       "8053.T",
    },
}

# ===== 注目銘柄候補（時価総額・規模問わず） =====
watchlist = {
    "テラドローン":         "278A.T",
    "サイバーエージェント": "4751.T",
    "ビジョナル":           "4194.T",
    "ディスコ":             "6146.T",
    "ルネサス":             "6723.T",
    "ソシオネクスト":       "6526.T",
    "安川電機":             "6506.T",
    "オービック":           "4684.T",
    "エムスリー":           "2413.T",
    "メドレー":             "4480.T",
    "くすりの窓口":         "5592.T",
    "インフォマート":       "2492.T",
}

# ===== セクターデータ取得 =====
sector_results = {}
all_stocks = []

for sector_name, stocks in sectors.items():
    changes = {}
    for name, symbol in stocks.items():
        change = get_change(symbol)
        changes[name] = change
        if change is not None:
            all_stocks.append((name, change, sector_name))
    sector_results[sector_name] = changes

# セクター平均
sector_avg = {}
for sector_name, stocks in sector_results.items():
    vals = [v for v in stocks.values() if v is not None]
    sector_avg[sector_name] = sum(vals) / len(vals) if vals else 0

sorted_sectors = sorted(sector_avg.items(), key=lambda x: x[1], reverse=True)
hot_sector  = sorted_sectors[0][0]  if sorted_sectors else "不明"
cold_sector = sorted_sectors[-1][0] if sorted_sectors else "不明"

sorted_stocks = sorted(all_stocks, key=lambda x: x[1], reverse=True)
top_stocks    = sorted_stocks[:5]
bottom_stocks = sorted_stocks[-5:]

# ===== 注目銘柄スキャン =====
watch_results = []
for name, symbol in watchlist.items():
    change = get_change(symbol)
    if change is not None:
        watch_results.append((name, change))
watch_results.sort(key=lambda x: x[1], reverse=True)
top_watch = watch_results[:5]

# ===== 米国連動分析 =====
def us_jp_correlation(spy, qqq, vix, usdjpy):
    signals = []
    if spy is not None and spy > 1.0:
        signals.append("米S&P500が強く上昇 → 日本株全体に追い風")
    elif spy is not None and spy < -1.0:
        signals.append("米S&P500が下落 → 日本株全体に逆風")

    if qqq is not None and qqq > 1.5:
        signals.append("NASDAQ強い → 半導体・テック・DXに追い風")
    elif qqq is not None and qqq < -1.5:
        signals.append("NASDAQ弱い → 半導体・テック系に注意")

    if vix is not None and vix < 15:
        signals.append("VIX低水準 → リスクオン、グロース株有利")
    elif vix is not None and 15 <= vix < 25:
        signals.append("VIX普通水準 → 特段のリスクなし")
    elif vix is not None and vix >= 25:
        signals.append("VIX高水準 → リスクオフ、ディフェンシブ有利")

    if usdjpy is not None and usdjpy > 150:
        signals.append(f"円安（{usdjpy:.1f}円） → 自動車・精密機器・輸出株に有利")
    elif usdjpy is not None and usdjpy < 140:
        signals.append(f"円高（{usdjpy:.1f}円） → 内需・小売・医療に有利")
    else:
        signals.append(f"ドル円 {usdjpy:.1f}円 → 特段の為替影響なし")

    return signals

correlation_signals = us_jp_correlation(spy_change, qqq_change, vix_price, usdjpy_price)

# ===== 今日の予測 =====
def predict_today(vix, spy, qqq, usdjpy, hot_sec):
    predictions = []

    if spy is not None and qqq is not None and spy > 0.5 and qqq > 0.5:
        predictions.append("半導体・AI（米国テック高連動）")
        predictions.append("テック・DX（リスクオン継続）")
    if usdjpy is not None and usdjpy > 150:
        predictions.append("自動車（円安恩恵）")
        predictions.append("精密機器（円安恩恵）")
    if vix is not None and vix < 20:
        predictions.append("小売・消費（安定相場）")
    if vix is not None and vix > 25:
        predictions.append("医療・ヘルスケア（ディフェンシブ）")
        predictions.append("不動産（ディフェンシブ）")
    if spy is not None and spy > 0:
        predictions.append("銀行・金融（景気敏感）")

    predictions.append(f"{hot_sec}（前日強セクター継続の可能性）")
    return list(dict.fromkeys(predictions))[:4]

predicted_sectors = predict_today(vix_price, spy_change, qqq_change, usdjpy_price, hot_sector)

# ===== 積立判定 =====
if vix_price is None:
    result = "データ取得失敗"
elif vix_price < 20:
    result = "通常積立"
elif vix_price < 30:
    result = "追加積立 +5万円検討"
elif vix_price < 40:
    result = "強気追加 +15万円検討"
else:
    result = "歴史的チャンス +30万円検討"

# ===== フォーマット関数 =====
def fmt(v):
    if v is None: return "取得失敗"
    sign = "+" if v >= 0 else ""
    arrow = "↑" if v >= 0 else "↓"
    return f"{arrow} {sign}{v:.2f}%"

def sector_bar(avg):
    if avg > 1.5:  return "🔥"
    if avg > 0:    return "↑ "
    if avg < -1.5: return "❄️"
    return "↓ "

# ===== メール本文 =====
body = f"""
━━━━━━━━━━━━━━━━━━━━
📊 投資アシスタント総合レポート
{today}
━━━━━━━━━━━━━━━━━━━━

【米国市場（前日結果）】
VIX:      {f"{vix_price:.2f}" if vix_price else "取得失敗"}
S&P500:   {fmt(spy_change)}
NASDAQ:   {fmt(qqq_change)}
ドル円:    {f"{usdjpy_price:.2f}円" if usdjpy_price else "取得失敗"}

💡 本日の積立判断: {result}

━━━━━━━━━━━━━━━━━━━━
【米国市場との連動分析】
━━━━━━━━━━━━━━━━━━━━
"""
for s in correlation_signals:
    body += f"  • {s}\n"

body += """
━━━━━━━━━━━━━━━━━━━━
【昨日の日本株セクター強弱】
━━━━━━━━━━━━━━━━━━━━
"""
for name, avg in sorted_sectors:
    sign = "+" if avg >= 0 else ""
    body += f"  {sector_bar(avg)} {name}: {sign}{avg:.2f}%\n"

body += f"""
🔥 最強: {hot_sector}
❄️  最弱: {cold_sector}

━━━━━━━━━━━━━━━━━━━━
【各セクター 時価総額トップ5 昨日の騰落】
━━━━━━━━━━━━━━━━━━━━
"""
for sector_name, stocks in sector_results.items():
    avg = sector_avg.get(sector_name, 0)
    sign = "+" if avg >= 0 else ""
    body += f"\n▶ {sector_name}（平均{sign}{avg:.2f}%）\n"
    for name, change in stocks.items():
        body += f"    {fmt(change) if change is not None else '取得失敗':>12}  {name}\n"

body += """
━━━━━━━━━━━━━━━━━━━━
【昨日 強い銘柄 トップ5】
━━━━━━━━━━━━━━━━━━━━
"""
for name, change, sector in top_stocks:
    body += f"  ▲ {name}（{sector}）: +{change:.2f}%\n"

body += """
【昨日 弱い銘柄 ワースト5】
"""
for name, change, sector in reversed(bottom_stocks):
    body += f"  ▼ {name}（{sector}）: {change:.2f}%\n"

body += """
━━━━━━━━━━━━━━━━━━━━
【注目銘柄スキャン（規模問わず）】
━━━━━━━━━━━━━━━━━━━━
"""
for name, change in top_watch:
    body += f"  ★ {name}: +{change:.2f}%\n"

body += f"""
━━━━━━━━━━━━━━━━━━━━
【今日の注目セクター予測】
━━━━━━━━━━━━━━━━━━━━
"""
for i, sec in enumerate(predicted_sectors, 1):
    body += f"  {i}. {sec}\n"

body += """
━━━━━━━━━━━━━━━━━━━━
⚠️ 本レポートは参考情報です。
   投資判断はご自身でお願いします。
━━━━━━━━━━━━━━━━━━━━
"""

# ===== メール送信 =====
gmail_user = os.environ["GMAIL_USER"]
gmail_pass = os.environ["GMAIL_PASS"]

subject = f"【投資レポート】{result} / 🔥{hot_sector} / {today}"

msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = subject
msg["From"]    = gmail_user
msg["To"]      = gmail_user

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(gmail_user, gmail_pass)
server.send_message(msg)
server.quit()

print(body)
