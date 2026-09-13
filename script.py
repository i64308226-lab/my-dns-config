import re
import requests

# Вшиваем ключи напрямую, чтобы обойти ошибку с Secrets на GitHub
API_KEY = "48f9050a00106fba82df54ac3cbe967d397b6d78"
PROFILE_ID = "78e1ed"

# 1. Весь список доменов (без Discord)
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

# Удаляем дубликаты
DOMAINS = list(dict.fromkeys(DOMAINS))

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def get_actual_ips():
    # Ваша прямая raw ссылка на файл
    raw_url = "https://githubusercontent.com"
    try:
        res = requests.get(raw_url).text
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return []

    ips = []
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/[0-9]{1,2})?\b')

    for line in res.split("\n"):
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#") or "route ADD" in line:
            continue
        
        found = ip_pattern.findall(line)
        for item in found:
            if "/" in item:
                base_ip = item.split("/")[0]
                if base_ip.endswith(".0"):
                    item = base_ip[:-1] + "1"
                else:
                    item = base_ip
            ips.append(item)

    return list(dict.fromkeys(ips))

def update_nextdns():
    ips = get_actual_ips()
    if not ips:
        print("Список IP-адресов пуст.")
        return

    print(f"Успешно получено {len(ips)} IP из файла. Синхронизируем с NextDNS...")
    rewrites_url = f"https://api.nextdns.io/profiles/{PROFILE_ID}/rewrites"
    
    try:
        current_rewrites = requests.get(rewrites_url, headers=headers).json().get("data", [])
        current_map = {r["name"]: {"id": r["id"], "content": r["content"]} for r in current_rewrites}
    except Exception as e:
        print(f"Ошибка связи с NextDNS API: {e}")
        return

    for i, domain in enumerate(DOMAINS):
        target_ip = ips[i % len(ips)]
        
        if domain in current_map:
            if current_map[domain]["content"] == target_ip:
                continue
            else:
                requests.delete(f"{rewrites_url}/{current_map[domain]['id']}", headers=headers)
        
        payload = {"name": domain, "content": target_ip}
        r = requests.post(rewrites_url, headers=headers, json=payload)
        if r.status_code == 201:
            print(f"Синхронизировано: {domain} -> {target_ip}")
        else:
            print(f"Ошибка для {domain}: {r.status_code} - {r.text}")

if __name__ == "__main__":
    update_nextdns()
