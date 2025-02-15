# SEO_analyses/wsparser.py
import json
import urllib.request
import urllib.error

class WordstatParser:
    """
    Класс для работы с Wordstat через API Яндекс.Директа.
    Предполагается, что у вас уже есть тестовый/полный доступ и отладочный токен.
    """

    def __init__(self, url: str, token: str, username: str):
        self.url = url
        self.token = token
        self.username = username

    def createReport(self, phrases, geo=None):
        """
        Создаёт новый отчёт Wordstat на сервере.
        phrases: список ключевых фраз (не более 10 за один раз)
        geo: список ID регионов (например, [213] для Москвы)
        """
        if geo is None:
            geo = []

        data = {
            "method": "CreateNewWordstatReport",
            "token": self.token,
            "param": {
                "Phrases": phrases,
                "GeoID": geo
            }
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def getReportList(self):
        """
        Получает список всех доступных отчётов Wordstat на сервере.
        """
        data = {
            "method": "GetWordstatReportList",
            "token": self.token
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def readReport(self, report_id: int):
        """
        Считывает готовый отчёт Wordstat по его ID.
        """
        data = {
            "method": "GetWordstatReport",
            "token": self.token,
            "param": report_id
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def deleteReport(self, report_id: int):
        """
        Удаляет отчёт Wordstat с сервера по его ID.
        """
        data = {
            "method": "DeleteWordstatReport",
            "token": self.token,
            "param": report_id
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def getClientUnits(self):
        """
        Пример метода, который возвращает оставшиеся баллы (единицы) API Директа.
        (Если нужно, можно вызвать в main.py для отладки)
        """
        data = {
            "method": "GetClientsUnits",
            "token": self.token,
            "param": [self.username]
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response
