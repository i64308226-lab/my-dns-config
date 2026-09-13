import re
import time
import requests

# Конфигурация API (используйте ваши актуальные данные)
API_KEY = "ВАШ_API_KEY"
PROFILE_ID = "ВАШ_PROFILE_ID"

DOMAINS = [
    "youtube.googleapis.com", "yt3.ggpht.com", "yt4.ggpht.com", "yt3.googleusercontent.com",
    "googlevideo.com", "jnn-pa.googleapis.com", "wide-youtube.l.google.com", "youtube-nocookie.com",
    "youtube-ui.l.google.com", "youtube.com", "youtubeembeddedplayer.googleapis.com",
    "youtubekids.com", "youtubei.googleapis.com", "youtu.be", "yt-video-upload.l.google.com",
    "ytimg.com", "ytimg.l.google.com",
    "t.me", "tg.dev", "tg.org", "tx.me", "teleg.xyz", "telegram.ai", "telegram.asia", "telegram.biz",
    "telegram.cloud", "telegram.cn", "telegram.co", "telegram.com", "telegram.de", "telegram.dev",
    "telegram.dog", "telegram.eu", "telegram.fr", "telegram.host", "telegram.in", "telegram.info",
    "telegram.io", "telegram.jp", "telegram.me", "telegram.net", "telegram.org", "telegram.qa",
    "telegram.ru", "telegram.services", "telegram.solutions", "telegram.space", "telegram.team",
    "telegram.tech", "telegram.uk", "telegram.us", "telegram.website", "telegram.xyz", "telegramapp.org",
    "telegra.ph", "telesco.pe", "nicegram.app", "telegramdownload.com", "cdn-telegram.org", "comments.app",
    "contest.com", "fragment.com", "graph.org", "quiz.directory", "tdesktop.com", "telega.one",
    "telegram-cdn.org", "usercontent.dev", "tgram.org", "torg.org"
]

DOMAINS = list(dict.fromkeys(DOMAINS))
headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def load_clean_ips():
    url = "https://gist.githubusercontent.com/iamwildtuna/7772b7c84a11bf6e1385f23096a73a15/raw/5b6d0cd45636d151c15da95f87a394ee6016e625/gistfile2.txt"
    try:
        print("Скачиваем файл с IP...")
        res = requests.get(url, timeout=15).text
    except Exception as e:
        print(f"Критическая ошибка загрузки: {e}")
        return []

    found_ips = []
    pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/[0-9]{1,2})?\b')
    
    for line in res.split("\n"):
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#") or "route ADD" in line:
            continue
        for item in pattern.findall(line):
            if "/" in item:
                clean_ip = item.split("/")[0]
            else:
                clean_ip = item
                
            if clean_ip.endswith(".0"):
                clean_ip = clean_ip[:-2] + ".1"
            found_ips.append(clean_ip)
            
    return list(dict.fromkeys(found_ips))

def run_dns_sync():
    ips = load_clean_ips()
    if not ips:
        print("Список IP-адресов пуст. Завершение работы.")
        return

    base_api_url = f"https://api.nextdns.io/profiles/{PROFILE_ID}/rewrites"
    print(f"Успешно получено {len(ips)} IP. Получаем текущий список правил...")
    
    try:
        response = requests.get(base_api_url, headers=headers)
        if response.status_code != 200:
            print(f"Ошибка API. Статус-код: {response.status_code}")
            return
        current_rules = response.json().get("data", [])
    except Exception as e:
        print(f"Критическая ошибка разбора JSON: {e}")
        return

    if len(current_rules) > 0:
        print(f"Найдено {len(current_rules)} старых записей. Очистка...")
        for rule in current_rules:
            del_url = f"{base_api_url}/{rule['id']}"
            requests.delete(del_url, headers=headers)
            print(f"Удалено старое правило: {rule['name']}")
            time.sleep(1.5)  # Пауза между запросами для обхода лимитов API
    else:
        print("Старых записей нет. Переходим к добавлению.")

    print("Начинаем добавление новых правил...")
    for i, domain in enumerate(DOMAINS):
        target_ip = ips[i % len(ips)]
        payload = {"name": domain, "content": target_ip}
        r = requests.post(base_api_url, headers=headers, json=payload)
        
        if r.status_code < 300:
            print(f"Успешно добавлено: {domain} -> {target_ip}")
        else:
            print(f"Ошибка добавления {domain}: {r.status_code} - {r.text}")
            
        time.sleep(1.5)  # Пауза 1.5 секунды для соблюдения Rate Limit

if __name__ == "__main__":
    run_dns_sync()
