import os
import re
import requests

# Конфигурация из секретов GitHub (подставит ваши данные)
API_KEY = os.environ.get("NEXTDNS_API_KEY")
PROFILE_ID = os.environ.get("NEXTDNS_PROFILE_ID")

# 1. Прямой список доменов, которые вы указали (исключая discord)
RAW_DOMAINS = [
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

# Удаляем случайные дубликаты доменов, если они есть
DOMAINS = list(dict.fromkeys(RAW_DOMAINS))

headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def get_actual_ips():
    # Ваша прямая raw ссылка на файл
    raw_url = "https://gist.githubusercontent.com/iamwildtuna/7772b7c84a11bf6e1385f23096a73a15/raw/5b6d0cd45636d151c15da95f87a394ee6016e625/gistfile2.txt"
    try:
        res = requests.get(raw_url).text
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        return []

    ips = []
    # Поиск IPv4 адресов и CIDR подсетей
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/[0-9]{1,2})?\b')

    for line in res.split("\n"):
        line = line.strip()
        # Пропускаем комментарии, команды роутера и пустые строки
        if not line or line.startswith("//") or line.startswith("#") or "route ADD" in line:
            continue
        
        found = ip_pattern.findall(line)
        for item in found:
            # Превращаем подсеть (например, 149.154.164.0/22) в рабочий IP с .1 на конце
            if "/" in item:
                base_ip = item.split("/")[0]
                if base_ip.endswith(".0"):
                    item = base_ip[:-1] + "1"
                else:
                    item = base_ip
            ips.append(item)

    # Убираем дубликаты IP, сохраняя порядок
    return list(dict.fromkeys(ips))

def update_nextdns():
    ips = get_actual_ips()
    if not ips:
        print("Список IP-адресов пуст. Проверьте источник.")
        return

    print(f"Успешно получено {len(ips)} уникальных IP-адресов из Gist.")
    
    rewrites_url = f"https://api.nextdns.io/profiles/{PROFILE_ID}/rewrites"
    
    # Получаем текущие записи из NextDNS, чтобы не забивать лимиты API повторами
    try:
        current_rewrites = requests.get(rewrites_url, headers=headers).json().get("data", [])
        current_map = {r["name"]: {"id": r["id"], "content": r["content"]} for r in current_rewrites}
    except Exception as e:
        print(f"Не удалось получить текущие настройки NextDNS: {e}")
        return

    # Синхронизация доменов и IP по цепочке
    for i, domain in enumerate(DOMAINS):
        target_ip = ips[i % len(ips)] # Зацикливаем IP, если доменов больше
        
        # Если домен уже прописан в NextDNS
        if domain in current_map:
            # И IP совпадает — пропускаем
            if current_map[domain]["content"] == target_ip:
                continue
            # Если IP изменился в Gist — удаляем старое правило
            else:
                requests.delete(f"{rewrites_url}/{current_map[domain]['id']}", headers=headers)
        
        # Отправляем обновленное/новое правило по API
        payload = {"name": domain, "content": target_ip}
        r = requests.post(rewrites_url, headers=headers, json=payload)
        if r.status_code == 201:
            print(f"Синхронизировано: {domain} -> {target_ip}")
        else:
            print(f"Ошибка API для {domain}: {r.status_code} - {r.text}")

if __name__ == "__main__":
    if not API_KEY or not PROFILE_ID:
        print("Ошибка: Переменные NEXTDNS_API_KEY или NEXTDNS_PROFILE_ID не найдены в GitHub Secrets!")
    else:
        update_nextdns()
