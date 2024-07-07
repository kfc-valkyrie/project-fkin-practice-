"""
Модуль получения информации от API HeadHunter
"""
import requests


class Getter:
    def __init__(self):
        self.vac_url = "https://api.hh.ru/vacancies"
        self.search_area = 113  # Россия

    def get_vacancies(self, keyword:str, per_page:int) -> list:
        """
        Получение списка вакансий из API по ключевому слову
        :param keyword: ключевое слово (str)
        :param per_page: количество вакансий в пачке (int)
        :return: список словарей-вакансий (list)
        """
        # TODO: Реализовать логику работы с несколькими пачками
        params = {
            "text": keyword,
            "area": self.search_area,
            "page": 1,  # Номер пачки
            "per_page": per_page,
        }
        response = requests.get(self.vac_url, params=params)

        if response.status_code == 200:
            data = response.json()
            res = []
            vacancies = data.get("items", [])
            return vacancies
        else:
            return []
