import os
import time
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from wsparser import WordstatParser  # Убедитесь, что wsparser.py находится рядом

# Конфигурация для доступа к API Яндекс.Директа
YANDEX_URL = os.getenv("YANDEX_URL", "https://api-sandbox.direct.yandex.ru/v4/json/")
YANDEX_TOKEN = os.getenv("YANDEX_TOKEN", "REMOVED_PRIVATE_CREDENTIAL")
YANDEX_USERNAME = os.getenv("YANDEX_USERNAME", "yandex.username")

# Инициализация FastAPI приложения
app = FastAPI(title="Wordstat API FastAPI")

# Создаем глобальный объект парсера
parser = WordstatParser(YANDEX_URL, YANDEX_TOKEN, YANDEX_USERNAME)

# Модель запроса: список ключевых слов
class WordstatRequest(BaseModel):
    keywords: list[str]

def process_wordstat(keywords: list[str]) -> dict:
    """
    Синхронная функция для обработки ключевых слов через API Wordstat.
    1. Создаем отчёт по переданным ключевым словам для региона Москва.
    2. Ждем, пока отчёт будет сформирован.
    3. Читаем отчёт и извлекаем набор ключевых фраз (левая колонка).
    4. Удаляем отчёт с сервера.
    5. Возвращаем данные.
    """
    # Подготавливаем данные для запроса (список фраз без модификаций)
    data = []
    for kw in keywords:
        data.append(kw)
    
    # Регион Москва. Обычно для Москвы используют geo ID = 213
    geo = [213]
    
    # Создаем отчёт на сервере
    response = parser.createReport(data, geo)
    if 'data' not in response:
        raise Exception("Не удалось создать отчет: " + str(response))
    report_id = response['data']

    # Ожидаем формирования отчёта (максимум 30 попыток, с интервалом 2 сек)
    attempts = 0
    while True:
        report_list = parser.getReportList()
        if 'data' not in report_list or not report_list['data']:
            raise Exception("Не удалось получить список отчетов: " + str(report_list))
        last_report = report_list['data'][-1]
        status = last_report.get('StatusReport')
        if status == 'Done':
            break
        elif status == 'Failed':
            raise Exception("Отчет не может быть сформирован.")
        time.sleep(2)
        attempts += 1
        if attempts > 30:
            raise Exception("Слишком долго ждем формирования отчета.")

    # Читаем сформированный отчет
    report = parser.readReport(report_id)
    if 'data' not in report:
        raise Exception("Не удалось прочитать отчет: " + str(report))

    # Извлекаем ключевые фразы из левой колонки отчета (SearchedWith)
    keywords_result = []
    for entry in report['data']:
        for item in entry.get('SearchedWith', []):
            keywords_result.append({
                'phrase': item.get('Phrase'),
                'shows': item.get('Shows')
            })

    # Удаляем отчет с сервера (чтобы не превышать лимит отчетов)
    parser.deleteReport(report_id)

    return {"report_id": report_id, "keywords": keywords_result}

@app.post("/wordstat")
async def get_wordstat(req: WordstatRequest):
    """
    HTTP POST эндпоинт, который принимает список ключевых слов,
    обрабатывает их через API Wordstat и возвращает набор ключевых фраз.
    """
    loop = asyncio.get_running_loop()
    try:
        # Запускаем синхронную функцию в отдельном потоке, чтобы не блокировать event loop
        result = await loop.run_in_executor(None, process_wordstat, req.keywords)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Запускаем приложение через uvicorn на порту 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
