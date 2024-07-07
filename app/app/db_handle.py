"""
Модуль получения информации из БД хранения
"""
from datetime import datetime
import psycopg2 as pg
from psycopg2 import errors
from api_handler import Getter
import os


class DBHandler:
    def __init__(self):
        database_url = os.environ['DATABASE_URL']
        self.conn = pg.connect(database_url)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def add_vac_to_favs(self, vac_id: list, user_id:int) -> list:
        """
        Добавление вакансии в избранное
        :param vac_id: список вакансий (list)
        :param user_id: ID пользователя-инициатора
        :return: Результат добавления (bool)
        """
        user_id = str(user_id)
        print(f"[LOG] 'add_vac_to_favs' function executed. [user_id]: {user_id} [vac_id]: {vac_id}")
        # Последний актуальный поиск для пользователя
        self.cursor.execute('SELECT "ID", key_val from search_history '
                            'WHERE created_by = %s '
                            'ORDER BY created_at desc '
                            'LIMIT 1', (user_id,))
        srch_id = self.cursor.fetchone()
        srch_id, key_val = srch_id
        print(f"[LOG] 'add_vac_to_favs' function proceeding. [srch_id]: {srch_id} [key_val]: {key_val}")
        # Вакансии по последнему поиску
        vac_id = tuple(vac_id)
        self.cursor.execute('SELECT t1.* FROM ('
                            'SELECT "ID", vac_name, emp_name, vac_link, ROW_NUMBER () OVER (ORDER BY "ID") as rn '
                            'FROM vacancies '
                            'WHERE "srch_ID" = %s ) t1 '
                            'WHERE t1.rn IN %s', (srch_id, vac_id))
        vac_found = self.cursor.fetchall()
        print(f"[LOG] 'add_vac_to_favs' function proceeding. [vac_found] length (number of vacancies found): {len(vac_found)}")
        if len(vac_found) == 0:
            return []
        else:
            vac_ids = [vac[0] for vac in vac_found]
            vac_ids = tuple(vac_ids)
            out_vacs = []
            for i in range(len(vac_found)):
                try:
                    self.cursor.execute("INSERT INTO favourites (vacancy_id, added_at, created_by) "
                                        "VALUES (%s, now(), %s)", (vac_ids[i], user_id))
                    out_vacs.append(vac_found[i])
                except errors.UniqueViolation:
                    pass
            return out_vacs

    def get_favs(self, user_id:str) -> list:
        """
        Получение списка избранных вакансий за последние сутки
        :return: Список избранных вакансий (list)
        """
        res = []
        user_id = str(user_id)
        print(f"[LOG] 'get_favs' function executed. [user_id]: {user_id}")
        # Проверка количества актуальных записей
        self.cursor.execute("SELECT count(*) FROM favourites "
                            "WHERE added_at >= current_date - interval '1' day "
                            "AND created_by = %s", (user_id,))
        cnt = self.cursor.fetchone()
        cnt = cnt[0]
        print(f"[LOG] 'search_vacs' function proceeding. [cnt]: (Count of found favourites) {cnt}")
        if cnt == 0:
            return res
        # Получение актуальных записей
        self.cursor.execute("SELECT t2.vac_name, t2.emp_name, t2.vac_link "
                            "FROM favourites t1 INNER JOIN vacancies t2 "
                            "ON t1.vacancy_id = t2.\"ID\" "
                            "WHERE t1.added_at >= current_date - interval '1' day "
                            "AND t1.created_by = %s", (user_id,))
        res = self.cursor.fetchall()
        return res

    def get_last_searches(self, user_id:int) -> list:
        """
        Получение поисковых запросов за последние сутки
        :param user_id: идентификатор пользователя, выполняющего запрос
        :return: список текстовых запросов (list)
        """
        print(f"[LOG] 'get_last_searches' function executed with [user_id]: {user_id}")
        res = []
        user_id = str(user_id)
        # Проверка количества актуальных записей
        self.cursor.execute("SELECT count(*) FROM search_history "
                            "WHERE created_at >= current_date - interval '1' day "
                            "AND created_by = %s", (user_id,))
        cnt = self.cursor.fetchone()
        cnt = cnt[0]
        print(f"[LOG] 'search_vacs' function proceeding. [cnt] (actual searches) found: {cnt}")
        if cnt == 0:
            return res
        # Получение актуальных записей
        self.cursor.execute("SELECT key_val FROM search_history "
                            "WHERE created_at >= current_date - interval '1' day "
                            "AND created_by = %s", (user_id,))
        res = self.cursor.fetchall()
        return res

    def search_vacs(self, key_val:str, user_id:str) -> list:
        """
        Поиск вакансий по паттерну
        :param key_val: паттерн поиска (str)
        :param user_id: идентификатор пользователя (str)
        :return: список вакансий (list)
        """
        res = []
        search_error = True
        # Проверка количества актуальных записей
        print(f"[LOG] 'search_vacs' function executed. [keyval]: {key_val} [user_id]: {user_id}")
        self.cursor.execute("SELECT count(*) "
                            "FROM search_history "
                            "WHERE refreshed_at < current_date - interval '5' minute "
                            "AND key_val = 'python middle'")
        cnt_to_refresh = self.cursor.fetchone()
        cnt_to_refresh = cnt_to_refresh[0]
        print(f"[LOG] 'search_vacs' function proceeding. [cnt_to_refresh]: {cnt_to_refresh}")
        gtr = Getter()
        vac_found = gtr.get_vacancies(keyword=key_val, per_page=10)
        print(f"[LOG] 'search_vacs' function proceeding. [vac_found] length: {len(vac_found)}")
        if len(vac_found) > 0:
            search_error = False
        print(f"[LOG] 'search_vacs' function proceeding. [search_error]: {search_error}")
        if not search_error:
            key_val_found = False
            self.cursor.execute("SELECT count(*) FROM search_history "
                                "WHERE key_val = %s AND created_by = %s", (key_val, str(user_id)))
            tmp = self.cursor.fetchone()
            tmp = int(tmp[0])
            print(f"[LOG] 'search_vacs' function proceeding. [tmp] (searches_count): {tmp}")
            if tmp > 0:
                key_val_found = True
            if not key_val_found:
                dt = datetime.now()
                self.cursor.execute('INSERT INTO search_history (key_val, created_by, created_at, refreshed_at) '
                                    'VALUES (%s, %s, %s, %s)', (key_val, user_id, dt, dt))
            self.cursor.execute('SELECT "ID" FROM search_history '
                                'WHERE key_val = %s', (key_val, ))
            srch_id = self.cursor.fetchone()
            srch_id = srch_id[0]
            print(f"[LOG] 'search_vacs' function proceeding. [ID] (search_id): {srch_id}")
            self.cursor.execute('DELETE FROM vacancies '
                                'WHERE "srch_ID" = %s', (srch_id,))
            print(f"[LOG] 'search_vacs' function proceeding. Vacancies table cleared.")
            if cnt_to_refresh > 0:
                self.cursor.execute('UPDATE search_history '
                                    'SET refreshed_at = now() '
                                    'WHERE "ID" = %s', (srch_id,))
                print(f"[LOG] 'search_vacs' function proceeding. Search_history table updated.")
            for i in range(len(vac_found)):
                res.append([])
                res[i].append(vac_found[i]["name"])
                res[i].append(vac_found[i]["employer"]["name"])
                res[i].append(str(srch_id))
                res[i].append(vac_found[i]["alternate_url"])
                tpl = tuple(res[i])
                self.cursor.execute('INSERT INTO vacancies (vac_name, emp_name, added_at, "srch_ID", vac_link) '
                                    'VALUES (%s, %s, now(), %s, %s)', tpl)
            print(f"[LOG] 'search_vacs' function proceeding. Inserted {len(vac_found)} records to vacancies table.")
        return res

    def __del__(self):
        self.cursor.close()
        self.conn.close()
