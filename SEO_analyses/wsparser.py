# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

# SEO_analyses/wsparser.py

import json
import urllib.error
import urllib.request


class WordstatParser:
    """
    Helper for Wordstat via the legacy Yandex Direct API.
    """

    def __init__(self, url: str, token: str, username: str):
        self.url = url
        self.token = token
        self.username = username

    def createReport(self, phrases, geo=None):
        """
        Create a new Wordstat report on the server.
        phrases: list of key phrases (Yandex API limits apply)
        geo: list of region IDs (e.g. [213] for Moscow)
        """
        if geo is None:
            geo = []
        data = {
            "method": "CreateNewWordstatReport",
            "token": self.token,
            "param": {"Phrases": phrases, "GeoID": geo},
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def getReportList(self):
        """
        Return a list of all available Wordstat reports on the server.
        """
        data = {"method": "GetWordstatReportList", "token": self.token}
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def readReport(self, report_id: int):
        """
        Read a finished Wordstat report by its ID.
        """
        data = {"method": "GetWordstatReport", "token": self.token, "param": report_id}
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def deleteReport(self, report_id: int):
        """
        Delete a Wordstat report by its ID.
        """
        data = {
            "method": "DeleteWordstatReport",
            "token": self.token,
            "param": report_id,
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response

    def getClientUnits(self):
        """
        Example method: return remaining API units for the configured client.
        """
        data = {
            "method": "GetClientsUnits",
            "token": self.token,
            "param": [self.username],
        }
        data_encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.urlopen(self.url, data_encoded)
        response = json.loads(request.read().decode("utf-8"))
        return response
