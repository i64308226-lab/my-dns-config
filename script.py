import re
import time
import requests
import sys

# Конфигурация NextDNS
API_KEY = "48f9050a00106fba82df54ac3cbe967d397b6d78"
PROFILE_ID = "78e1ed"

DOMAINS = [
    "://googleapis.com", "://ggpht.com", "://ggpht.com", "://googleusercontent.com",
    "googlevideo.com", "://googleapis.com", "://google.com", "youtube-nocookie.com",
    "://google.com", "youtube.com", "://googleapis.com",
    "youtubekids.com", "://googleapis.com", "youtu.be", "://google.com",
    "ytimg.com", "://google.com", "googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com", "://googlevideo.com", "://googlevideo.com",
    "://googlevideo.com",
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
        print("Шаг 1: Скачиваем файл с IP...", flush=True)
        # Жесткий таймаут 5 секунд, чтобы скрипт не висел вечно
        res = requests.get(url, timeout=5).text
    except Exception as e:
        print(f"❌ Критическая ошибка загрузки файла: {e}", flush=True)
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
        print("❌ Список IP-адресов пуст. Завершение.", flush=True)
        return

    base_api_url = f"https://api.nextdns.io/profiles/{PROFILE_ID}/rewrites"
    print(f"Шаг 2: Успешно получено {len(ips)} IP. Запрос к NextDNS...", flush=True)
    
    try:
        response = requests.get(base_api_url, headers=headers, timeout=5)
        if response.status_code != 200:
            print(f"❌ Ошибка API. Код: {response.status_code}, Текст: {response.text}", flush=True)
            return
        current_rules = response.json().get("data", [])
    except Exception as e:
        print(f"❌ Ошибка связи с NextDNS: {e}", flush=True)
        return

    if len(current_rules) > 0:
        print(f"Шаг 3: Найдено {len(current_rules)} старых записей. Очистка...", flush=True)
        for rule in current_rules:
            del_url = f"{base_api_url}/{rule['id']}"
            del_res = requests.delete(del_url, headers=headers, timeout=5)
            if del_res.status_code < 300:
                print(f"Удалено: {rule['name']}", flush=True)
            else:
                print(f"Ошибка удаления {rule['name']}: {del_res.status_code}", flush=True)
            time.sleep(1.5)
    else:
        print("Старых записей нет. Переходим к добавлению.", flush=True)

    print("Шаг 4: Начинаем добавление новых правил...", flush=True)
    for i, domain in enumerate(DOMAINS):
        target_ip = ips[i % len(ips)]
        payload = {"name": domain, "content": target_ip}
        r = requests.post(base_api_url, headers=headers, json=payload, timeout=5)
        if r.status_code < 300:
            print(f"Добавлено: {domain} -> {target_ip}", flush=True)
        else:
            print(f"Ошибка {domain}: {r.status_code} - {r.text}", flush=True)
        time.sleep(1.5)

if __name__ == "__main__":
    run_dns_sync()
