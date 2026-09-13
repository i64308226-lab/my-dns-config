import re
import requests

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
    url = "https://githubusercontent.com"
    try:
        print("Скачиваем файл с IP по точной ссылке...")
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
            # Если есть маска (149.154.164.0/22), забираем только сам IP до слэша
            if "/" in item:
                item = item.split("/")[0]
            # Теперь item гарантированно строка. Если она кончается на .0, меняем на .1
            if item.endswith(".0"):
                item = item[:-2] + ".1"
            found_ips.append(item)
            
    return list(dict.fromkeys(found_ips))

def run_dns_sync():
    ips = load_clean_ips()
    if not ips:
        print("Список IP-адресов пуст. Завершение работы.")
        return

    base_api_url = "https://nextdns.io" + str(PROFILE_ID) + "/rewrites"
    print(f"Успешно получено {len(ips)} IP. Получаем текущий список Rewrites...")
    
    try:
        response = requests.get(base_api_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"API вернул код {response.status_code}: {response.text}")
        current_rules = response.json().get("data", [])
    except Exception as e:
        print(f"Ошибка связи с NextDNS API: {e}")
        return

    if len(current_rules) > 0:
        print(f"Найдено {len(current_rules)} старых записей. Полная очистка...")
        for rule in current_rules:
            del_url = base_api_url + "/" + str(rule['id'])
            del_res = requests.delete(del_url, headers=headers)
            if del_res.status_code < 300:
                print(f"Удалено старое правило: {rule['name']}")
            else:
                print(f"Не удалось удалить {rule['name']}: {del_res.status_code}")
    else:
        print("Старых записей в профиле нет. Переходим к добавлению.")

    print("Начинаем добавление новых правил...")
    for i, domain in enumerate(DOMAINS):
        target_ip = ips[i % len(ips)]
        payload = {"name": domain, "content": target_ip}
        r = requests.post(base_api_url, headers=headers, json=payload)
        if r.status_code < 300:
            print(f"Успешно добавлено: {domain} -> {target_ip}")
        else:
            print(f"Ошибка добавления {domain}: {r.status_code} - {r.text}")

if __name__ == "__main__":
    run_dns_sync()
