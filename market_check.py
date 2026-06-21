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
vix_price    = get_price("^VIX")
spy_change   = get_change("SPY")
qqq_change   = get_change("QQQ")
usdjpy_price = get_price("JPY=X")

# ===== 日本株セクター（全銘柄コード確認済み） =====
sectors = {
    "半導体・AI・電子部品": {
        "キオクシアHD":       "285A.T",   # 時価総額2位
        "東京エレクトロン":   "8035.T",   # 時価総額5位
        "アドバンテスト":     "6857.T",   # 時価総額10位
        "村田製作所":         "6981.T",   # 時価総額11位
        "キーエンス":         "6861.T",   # 時価総額12位
        "ルネサス":           "6723.T",
        "レーザーテック":     "6920.T",
        "ディスコ":           "6146.T",
        "ソシオネクスト":     "6526.T",
        "太陽誘電":           "6976.T",
    },
    "テック・DX・通信": {
        "ソフトバンクG":         "9984.T",   # 時価総額3位
        "日立製作所":           "6501.T",   # 時価総額7位
        "リクルートHD":         "6098.T",   # 時価総額15位
        "ソニーグループ":       "6758.T",   # 時価総額9位
        "NTT":                  "9432.T",
        "NEC":                  "6701.T",
        "富士通":               "6702.T",
        "さくらインターネット": "3778.T",
        "サイバーエージェント": "4751.T",
        "オービック":           "4684.T",
    },
    "電線・非鉄金属": {
        "フジクラ":         "5803.T",
        "古河電気工業":     "5801.T",
        "住友電気工業":     "5802.T",
        "JX金属":           "5016.T",
        "住友金属鉱山":     "5713.T",
    },
    "素材・化学": {
        "信越化学工業":   "4063.T",   # 時価総額17位
        "レゾナック":     "4004.T",
        "住友化学":       "4005.T",
        "三菱ケミカルG":  "4188.T",
        "旭化成":         "3407.T",
    },
    "鉄鋼": {
        "日本製鉄":             "5401.T",
        "JFEホールディングス":  "5411.T",
        "神戸製鋼所":           "5406.T",
    },
    "銀行・金融": {
        "三菱UFJ":          "8306.T",   # 時価総額4位
        "三井住友FG":        "8316.T",   # 時価総額8位
        "みずほFG":          "8411.T",   # 時価総額13位
        "三井住友トラスト":  "8309.T",
        "りそなHD":          "8308.T",
    },
    "保険": {
        "東京海上HD":              "8766.T",   # 時価総額19位
        "MS&ADインシュアランス":  "8725.T",
        "SOMPOホールディングス":  "8630.T",
        "第一生命HD":              "8750.T",
    },
    "商社": {
        "三菱商事":   "8058.T",   # 時価総額14位
        "伊藤忠商事": "8001.T",   # 時価総額16位
        "三井物産":   "8031.T",   # 時価総額18位
        "住友商事":   "8053.T",
        "丸紅":       "8002.T",
    },
    "自動車・輸送機器": {
        "トヨタ":   "7203.T",   # 時価総額1位
        "ホンダ":   "7267.T",
        "デンソー": "6902.T",
        "アイシン": "7259.T",
        "日産":     "7201.T",
    },
    "精密機器・ロボット": {
        "キヤノン":   "7751.T",
        "HOYA":       "7741.T",
        "テルモ":     "4543.T",
        "安川電機":   "6506.T",
        "ファナック": "6954.T",
    },
    "防衛・重工": {
        "三菱重工":     "7011.T",
        "川崎重工":     "7012.T",
        "IHI":          "7013.T",
        "住友重機械":   "6302.T",
        "テラドローン": "278A.T",
    },
    "小売・消費": {
        "ファーストリテイリング": "9983.T",   # 時価総額6位
        "セブン＆アイ":           "3382.T",
        "イオン":                 "8267.T",
        "ニトリ":                 "9843.T",
        "MonotaRO":               "3064.T",
    },
    "医療・ヘルスケア": {
        "武田薬品":       "4502.T",
        "第一三共":       "4568.T",
        "アステラス製薬": "4503.T",
        "エーザイ":       "4523.T",
        "メドレー":       "4480.T",
    },
    "不動産": {
        "三井不動産":   "8801.T",
        "三菱地所":     "8802.T",
        "住友不動産":   "8830.T",
        "東急不動産HD": "3289.T",
        "野村不動産HD": "3231.T",
    },
    "エネルギー・資源": {
        "ENEOS HD": "5020.T",
        "出光興産": "5019.T",
        "INPEX":    "1605.T",
        "コスモHD": "5021.T",
        "電源開発": "9513.T",
    },
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

sorted_stocks  = sorted(all_stocks, key=lambda x: x[1], reverse=True)
top_stocks     = sorted_stocks[:10]
bottom_stocks  = sorted_stocks[-5:]

# ===== 米国連動分析 =====
def us_jp_correlation(spy, qqq, vix, usdjpy):
    signals = []
    if spy is not None:
        if spy > 1.0:
            signals.append(f"米S&P500 {spy:+.2f}% → 日本株全体に追い風")
        elif spy < -1.0:
            signals.append(f"米S&P500 {spy:+.2f}% → 日本株全体に逆風")
        else:
            signals.append(f"米S&P500 {spy:+.2f}% → 小幅な動き")
    if qqq is not None:
        if qqq > 1.5:
            signals.append(f"NASDAQ {qqq:+.2f}% → 半導体・テック・DXに追い風")
        elif qqq < -1.5:
            signals.append(f"NASDAQ {qqq:+.2f}% → 半導体・テック系に注意")
        else:
            signals.append(f"NASDAQ {qqq:+.2f}% → 小幅な動き")
    if vix is not None:
        if vix < 15:
            signals.append(f"VIX {vix:.1f} → リスクオン、グロース株有利")
        elif vix < 25:
            signals.append(f"VIX {vix:.1f} → 通常水準、特段のリスクなし")
        else:
            signals.append(f"VIX {vix:.1f} → リスクオフ、ディフェンシブ有利")
    if usdjpy is not None:
        if usdjpy > 150:
            signals.append(f"円安 {usdjpy:.1f}円 → 自動車・精密機器・電線に有利")
        elif usdjpy < 140:
            signals.append(f"円高 {usdjpy:.1f}円 → 内需・小売・医療に有利")
        else:
            signals.append(f"ドル円 {usdjpy:.1f}円 → 特段の為替影響なし")
    return signals if signals else ["特段の連動シグナルなし"]

correlation_signals = us_jp_correlation(spy_change, qqq_change, vix_price, usdjpy_price)

# ===== 今日の予測 =====
def predict_today(vix, spy, qqq, usdjpy, hot_sec):
    predictions = []
    if spy is not None and qqq is not None and spy > 0.5 and qqq > 0.5:
        predictions.append("半導体・AI・電子部品（米テック高連動）")
        predictions.append("テック・DX・通信（リスクオン継続）")
    if usdjpy is not None and usdjpy > 150:
        predictions.append("自動車・輸送機器（円安恩恵）")
        predictions.append("電線・非鉄金属（円安・資源高恩恵）")
    if vix is not None and vix < 20:
        predictions.append("小売・消費（安定相場・内需）")
    if vix is not None and vix > 25:
        predictions.append("医療・ヘルスケア（ディフェンシブ）")
        predictions.append("不動産（ディフェンシブ）")
    if spy is not None and spy > 0:
        predictions.append("銀行・金融（景気敏感・金利上昇期待）")
        predictions.append("保険（景気敏感）")
    if usdjpy is not None and usdjpy > 148:
        predictions.append("商社（資源・円安恩恵）")
    predictions.append(f"{hot_sec}（前日強セクター継続の可能性）")
    return list(dict.fromkeys(predictions))[:5]

predicted_sectors = predict_today(
    vix_price, spy_change, qqq_change, usdjpy_price, hot_sector
)

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
    if v is None:
        return "－"
    return f"{'↑' if v >= 0 else '↓'} {'+' if v >= 0 else ''}{v:.2f}%"

def bar(avg):
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
VIX:     {f"{vix_price:.2f}" if vix_price else "取得失敗"}
S&P500:  {fmt(spy_change)}
NASDAQ:  {fmt(qqq_change)}
ドル円:   {f"{usdjpy_price:.2f}円" if usdjpy_price else "取得失敗"}

💡 本日の積立判断: {result}

━━━━━━━━━━━━━━━━━━━━
【米国市場との連動分析】
━━━━━━━━━━━━━━━━━━━━
"""
for s in correlation_signals:
    body += f"  • {s}\n"

body += """
━━━━━━━━━━━━━━━━━━━━
【昨日のセクター強弱ランキング】
━━━━━━━━━━━━━━━━━━━━
"""
for name, avg in sorted_sectors:
    sign = "+" if avg >= 0 else ""
    body += f"  {bar(avg)} {name}: {sign}{avg:.2f}%\n"

body += f"""
🔥 最強セクター: {hot_sector}
❄️  最弱セクター: {cold_sector}

━━━━━━━━━━━━━━━━━━━━
【各セクター 全銘柄 前日騰落】
━━━━━━━━━━━━━━━━━━━━
"""
for sector_name, stocks in sector_results.items():
    avg = sector_avg.get(sector_name, 0)
    sign = "+" if avg >= 0 else ""
    body += f"\n▶ {sector_name}（平均{sign}{avg:.2f}%）\n"
    sorted_s = sorted(
        stocks.items(),
        key=lambda x: x[1] if x[1] is not None else -99,
        reverse=True
    )
    for name, change in sorted_s:
        body += f"    {fmt(change):>14}  {name}\n"

body += """
━━━━━━━━━━━━━━━━━━━━
【昨日 強い銘柄 トップ10】
━━━━━━━━━━━━━━━━━━━━
"""
for i, (name, change, sector) in enumerate(top_stocks, 1):
    body += f"  {i:2}. {name}（{sector}）: +{change:.2f}%\n"

body += """
━━━━━━━━━━━━━━━━━━━━
【昨日 弱い銘柄 ワースト5】
━━━━━━━━━━━━━━━━━━━━
"""
for name, change, sector in reversed(bottom_stocks):
    body += f"  ▼ {name}（{sector}）: {change:.2f}%\n"

body += f"""
━━━━━━━━━━━━━━━━━━━━
【今日の注目セクター予測】
━━━━━━━━━━━━━━━━━━━━
"""
for i, sec in enumerate(predicted_sectors, 1):
    body += f"  {i}. {sec}\n"

body += "\n【今日の注目銘柄候補（予測セクターより）】\n"
shown = 0
for name, change, sector in sorted_stocks:
    if any(sector in ps for ps in predicted_sectors) and shown < 8:
        body += f"  ★ {name}（{sector}）前日 +{change:.2f}%\n"
        shown += 1

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
