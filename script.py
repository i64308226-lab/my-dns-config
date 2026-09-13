import re
import requests

# Конфигурация NextDNS (Ваши рабочие ключи)
API_KEY = "48f9050a00106fba82df54ac3cbe967d397b6d78"
PROFILE_ID = "78e1ed"

# Весь список доменов (без Discord)
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

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def get_actual_ips():
    # ТЕПЕРЬ АДРЕС АБСОЛЮТНО КОРРЕКТЕН
    raw_url = "https://gist.githubusercontent.com/iamwildtuna/7772b7c84a11bf6e1385f23096a73a15/raw/5b6d0cd45636d151c15da95f87a394ee6016e625/gistfile2.txt"
    api_url = "https://github.com"
    
    res = ""
    try:
        print("Пробуем скачать файл по прямой ссылке...")
        response = requests.get(raw_url, timeout=15)
        if response.status_code == 200:
            res = response.text
        else:
            raise Exception(f"Код ответа {response.status_code}")
    except Exception as e:
        print(f"Прямая ссылка не сработала ({e}). Пробуем через официальный API GitHub...")
        try:
            api_res = requests.get(api_url, timeout=15).json()
            file_key = list(api_res["files"].keys())[0]
            res = api_res["files"][file_key]["content"]
        except Exception as api_err:
            print(f"Критическая ошибка: Не удалось получить данные ни одним способом: {api_err}")
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
        print("Список IP-адресов пуст. Завершение работы.")
        return

    print(f"Успешно получено {len(ips)} IP. Начинаем синхронизацию с NextDNS профилем {PROFILE_ID}...")
    rewrites_url = f"https://nextdns.io{PROFILE_ID}/rewrites"
    
    try:
        response = requests.get(rewrites_url, headers=headers)
        current_rewrites = response.json().get("data", [])
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
            print(f"Успешно: {domain} -> {target_ip}")
        else:
            print(f"Ошибка для {domain}: {r.status_code} - {r.text}")

if __name__ == "__main__":
    update_nextdns()
