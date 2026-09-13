import re
import time
import requests

# ========================================================
# ФИНАЛЬНАЯ КОНФИГУРАЦИЯ С ВАШИМ РАБОЧИМ IP
# ========================================================
API_KEY = "48f9050a00106fba82df54ac3cbe967d397b6d78"
PROFILE_ID = "78e1ed"
YOUR_CLOUDFLARE_IP = "185.14.30.185"
# ========================================================

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

# Удаляем возможные дубликаты из списка доменов
DOMAINS = list(dict.fromkeys(DOMAINS))
headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def run_dns_sync():
    base_api_url = f"https://api.nextdns.io/profiles/{PROFILE_ID}/rewrites"
    print("Шаг 1: Подключаемся к NextDNS API для проверки старых записей...", flush=True)
    
    try:
        response = requests.get(base_api_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Ошибка получения данных API. Код: {response.status_code}, Ответ: {response.text}", flush=True)
            return
        current_rules = response.json().get("data", [])
    except Exception as e:
        print(f"❌ Ошибка связи с серверами NextDNS: {e}", flush=True)
        return

    # ПОЛНАЯ ОЧИСТКА СТАРЫХ ЗАПИСЕЙ
    if len(current_rules) > 0:
        print(f"Шаг 2: Найдено {len(current_rules)} старых записей. Начинаем полную очистку...", flush=True)
        for rule in current_rules:
            del_url = f"{base_api_url}/{rule['id']}"
            del_res = requests.delete(del_url, headers=headers, timeout=10)
            if del_res.status_code < 300:
                print(f"Удалено старое правило: {rule['name']}", flush=True)
            else:
                print(f"Не удалось удалить {rule['name']}: {del_res.status_code}", flush=True)
            time.sleep(1.5)  # Интервал 1.5 секунды во избежание ошибки 429 rateLimit
    else:
        print("Шаг 2: Старых записей в профиле нет. Переходим к добавлению новых.", flush=True)

    # ЧИСТАЯ ЗАПИСЬ НОВЫХ ДОМЕНОВ НА ВАШ CLOUDFLARE PROXY IP
    print(f"Шаг 3: Начинаем привязку доменов к прокси {YOUR_CLOUDFLARE_IP}...", flush=True)
    for domain in DOMAINS:
        payload = {"name": domain, "content": YOUR_CLOUDFLARE_IP}
        r = requests.post(base_api_url, headers=headers, json=payload, timeout=10)
        if r.status_code < 300:
            print(f"Успешно добавлено: {domain} -> {YOUR_CLOUDFLARE_IP}", flush=True)
        else:
            print(f"Ошибка добавления {domain}: {r.status_code} - {r.text}", flush=True)
        time.sleep(1.5)  # Интервал 1.5 секунды для соблюдения лимитов NextDNS API

    print("🎉 Синхронизация успешно завершена! Все домены обновлены.", flush=True)

if __name__ == "__main__":
    run_dns_sync()
