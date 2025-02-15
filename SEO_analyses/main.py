# SEO_analyses/main.py
import os
import time
import asyncio
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .wsparser import WordstatParser

# Конфигурация для доступа к Wordstat
YANDEX_URL = os.getenv("YANDEX_URL", "https://api-sandbox.direct.yandex.ru/v4/json/")
YANDEX_TOKEN = os.getenv("YANDEX_TOKEN", "ВАШ_ТОКЕН")
YANDEX_USERNAME = os.getenv("YANDEX_USERNAME", "ВАШ_ЛОГИН")

# Инициализируем парсер Wordstat
parser = WordstatParser(YANDEX_URL, YANDEX_TOKEN, YANDEX_USERNAME)

app = FastAPI(title="SEO Analyses Service")

class WordstatRequest(BaseModel):
    keywords: List[str]

@app.post("/wordstat")
async def get_wordstat(request: WordstatRequest):
    """
    Принимает список ключевых слов,
    запрашивает статистику в Wordstat (регион Москва = 213),
    возвращает найденные фразы и их частотность.
    """

    # Используем run_in_executor, чтобы не блокировать event loop
    loop = asyncio.get_running_loop()

    def process_wordstat(keywords: list[str]) -> dict:
        # Шаг 1: Создаём отчёт для заданных ключевых слов и региона Москва (ID = 213)
        response = parser.createReport(keywords, [213])
        if "data" not in response:
            raise Exception("Не удалось создать отчет: " + str(response))

        report_id = response["data"]

        # Шаг 2: Ждём, пока отчёт будет готов (максимум 30 итераций)
        attempts = 0
        while True:
            report_list = parser.getReportList()
            if "data" not in report_list or not report_list["data"]:
                raise Exception("Не удалось получить список отчетов: " + str(report_list))

            # Предполагаем, что только что созданный отчёт - последний в списке
            last_report = report_list["data"][-1]
            status = last_report.get("StatusReport")

            if status == "Done":
                break
            elif status == "Failed":
                raise Exception("Отчет не может быть сформирован (Failed).")

            time.sleep(2)
            attempts += 1
            if attempts > 30:
                raise Exception("Слишком долго ждем формирования отчета.")

        # Шаг 3: Читаем отчёт
        report_data = parser.readReport(report_id)
        if "data" not in report_data:
            raise Exception("Не удалось прочитать отчет: " + str(report_data))

        # Шаг 4: Формируем итоговый список (левая колонка SearchedWith)
        result_keywords = []
        for entry in report_data["data"]:
            searched_with = entry.get("SearchedWith", [])
            for item in searched_with:
                phrase = item.get("Phrase")
                shows = item.get("Shows")
                result_keywords.append({"phrase": phrase, "shows": shows})

        # Шаг 5: Удаляем отчёт (чтобы не превысить лимит в 5 отчётов)
        parser.deleteReport(report_id)

        return {"keywords": result_keywords}

    try:
        # Запускаем синхронную функцию в пуле потоков
        result = await loop.run_in_executor(None, process_wordstat, request.keywords)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

if __name__ == "__main__":
    import uvicorn
    # Запускаем сервис на порту 8001 (или другом)
    uvicorn.run("SEO_analyses.main:app", host="0.0.0.0", port=8001, reload=True)
