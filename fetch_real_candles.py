import urllib.request
import xml.etree.ElementTree as ET
import json
import time
import sys

stocks_to_fetch = [
    # Default watchlist
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("035420", "NAVER"),
    ("005380", "현대차"),
    ("247540", "에코프로비엠"),
    ("042700", "한미반도체"),
    # Screener & high attention stocks
    ("009150", "삼성전기"),
    ("086520", "에코프로"),
    ("196170", "알테오젠"),
    ("035720", "카카오"),
    ("000270", "기아"),
    ("373220", "LG에너지솔루션"),
    ("207940", "삼성바이오로직스"),
    ("105560", "KB금융"),
    ("005490", "POSCO홀딩스"),
    ("068270", "셀트리온"),
    ("259960", "크래프톤"),
    ("267260", "HD현대일렉트릭"),
    ("003230", "삼양식품"),
    ("012450", "한화에어로스페이스"),
    ("034020", "두산에너빌리티"),
    ("028300", "에이치엘비"),
    ("066570", "LG전자"),
    ("055550", "신한지주"),
    ("010130", "고려아연"),
    ("015760", "한국전력"),
    ("033780", "KT&G"),
    ("011200", "HMM"),
    ("003550", "LG"),
    ("000810", "삼성화재")
]

def fetch_candles_for_stock(code, tf, count):
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe={tf}&count={count}&requestType=0"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            xml_text = resp.read().decode("euc-kr", errors="replace")
            root = ET.fromstring(xml_text)
            chartdata = root.find("chartdata")
            if chartdata is None:
                return []
            items = chartdata.findall("item")
            candles = []
            for it in items:
                raw = it.get("data")
                if not raw:
                    continue
                parts = raw.split("|")
                if len(parts) < 6:
                    continue
                d = parts[0]
                date_str = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
                candles.append([
                    date_str,
                    int(parts[1]), # open
                    int(parts[2]), # high
                    int(parts[3]), # low
                    int(parts[4]), # close
                    int(parts[5])  # volume
                ])
            return candles
    except Exception as e:
        print(f"Error fetching {code} {tf}: {e}", file=sys.stderr)
        return []

all_data = {}
print(f"Starting fetch for {len(stocks_to_fetch)} stocks...")
start_time = time.time()

for idx, (code, name) in enumerate(stocks_to_fetch):
    print(f"[{idx+1}/{len(stocks_to_fetch)}] Fetching {name} ({code})...")
    day_candles = fetch_candles_for_stock(code, "day", 750)
    week_candles = fetch_candles_for_stock(code, "week", 350)
    month_candles = fetch_candles_for_stock(code, "month", 180)
    
    all_data[code] = {
        "name": name,
        "day": day_candles,
        "week": week_candles,
        "month": month_candles
    }
    time.sleep(0.05)

out_file = "/home/antigravity/stock-discovery-dashboard/stock_candles_history.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, separators=(',', ':'))

elapsed = time.time() - start_time
file_size_kb = len(open(out_file, 'rb').read()) / 1024
print(f"Done in {elapsed:.2f}s! Saved to {out_file} ({file_size_kb:.1f} KB)")
