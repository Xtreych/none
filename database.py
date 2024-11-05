import sqlite3
from sqsnip import database as db


class database:
    def __init__(self, db_name: str):
        # id - id телеграма, status - в поиске ли человек, rid - найден ли собеседник, gender - пол, age - возраст, category - категория поиска
        self.database = db(db_name, "users", """
            id INTEGER,
            status INTEGER,
            rid INTEGER,
            gender STRING,
            age INTEGER,
            category STRING,
            referral STRING,
            preferred_gender STRING,
            min_age INTEGER,
            max_age INTEGER
        """)

        # Создаем таблицу для реферальных кодов, если её нет
        self.database.execute("""
                CREATE TABLE IF NOT EXISTS referral_codes (
                    code TEXT PRIMARY KEY,
                    owner_id INTEGER
                )
            """)

        # Создаем таблицу для администраторов, если её нет
        self.database.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        admin_id INTEGER PRIMARY KEY
                    )
                """)

        # Добавляем Bes, Besovskaya и Serj как постоянного администратора
        try:
            self.database.execute("INSERT OR IGNORE INTO admins (admin_id) VALUES (?)", (1978805110,))
            self.database.execute("INSERT OR IGNORE INTO admins (admin_id) VALUES (?)", (686803928,))
            self.database.execute("INSERT OR IGNORE INTO admins (admin_id) VALUES (?)", (1171214769,))
        except:
            pass

    def is_admin(self, user_id: int) -> bool:
        result = self.database.execute("SELECT admin_id FROM admins WHERE admin_id = ?", (user_id,))
        return bool(result)

    def add_admin(self, admin_id: int) -> bool:
        try:
            self.database.execute("INSERT INTO admins (admin_id) VALUES (?)", (admin_id,))
            return True
        except:
            return False

    def remove_admin(self, admin_id: int) -> bool:
        if admin_id not in [1978805110, 686803928, 1171214769]:  # Защита от удаления Bes
            try:
                self.database.execute("DELETE FROM admins WHERE admin_id = ?", (admin_id,))
                return True
            except:
                return False
        return False

    def get_admin_list(self):
        try:
            return self.database.execute("SELECT admin_id FROM admins")
        except:
            return []

    def add_referral_code(self, code: str, owner_id: int) -> bool:
        try:
            self.database.execute("INSERT INTO referral_codes (code, owner_id) VALUES (?, ?)",
                                  (code, owner_id))
            return True
        except:
            return False

    def remove_referral_code(self, code: str) -> bool:
        try:
            self.database.execute("DELETE FROM referral_codes WHERE code = ?", (code,))
            return True
        except:
            return False

    def get_all_referral_codes(self):
        try:
            return self.database.execute("SELECT code, owner_id FROM referral_codes")
        except:
            return []

    def get_referral_code_owner(self, code: str):
        try:
            result = self.database.execute("SELECT owner_id FROM referral_codes WHERE code = ?",
                                           (code,))
            return result[0] if result else None
        except:
            return None

    def get_user_cursor(self, user_id: int) -> dict | None:
        try:
            result = self.database.select("*", {"id": user_id}, False)
            if result is None:
                return None

            result = list(result)
            return {
                "status": result[1],
                "rid": result[2]
            }
        except Exception as e:
            print(f"Error in get_user_cursor: {e}")
            return None

    def get_users_in_search(self) -> int:
        result = self.database.select("*", {"status": 1}, True)
        num = 0
        if result:
            num = len(result)

        return num

    def check_user_age(self, user_id: int) -> int:
        result = self.database.select("age", {"id": user_id}, False)
        if result is None:
            return None
        return result[0]

    def check_user_referral(self, user_id: int) -> int:
        result = self.database.select("referral", {"id": user_id}, False)
        if result is None:
            return None
        return result[0]

    def count_referral(self, referral_value: str) -> int:
        query = "SELECT COUNT(*) FROM users WHERE referral = ?"
        result = self.database.execute(query, (referral_value,))
        return result[0] if result else 0

    def print_users_by_referral(self, referral: str):
        result = self.database.select("id", {"referral": referral}, True)
        if result:
            a = []
            for user in result:
                # print(f"ID: {user[0]}")
                a.append(user[0])
                # print(a)
            return a
        else:
            print("No users found with the specified referral.")

    def new_user(self, user_id: int):
        self.database.insert([
            user_id, # id
            0, # status
            0, # rid
            0, # gender
            0, # age
            None, # category
            None, # referral
            'any', # preferred_gender
            0, # min_age
            0 # max_age
        ])
        # при создании нового столбца в бд, не забывай добавить стартовое значение сюда

    def search(self, user_id: int):
        # Получаем предпочтения пользователя
        user_prefs = self.get_search_preferences(user_id)

        # Получаем данные текущего пользователя
        user_data = self.database.execute(
            "SELECT gender, age FROM users WHERE id = ?",
            (user_id,)
        )[0]

        # Обновляем статус пользователя на "в поиске"
        self.database.update({"status": 1, "rid": 0}, {"id": user_id})

        # Формируем базовый запрос
        query = f"""
            SELECT * FROM users 
            WHERE status = 1 
            AND id != {user_id}
        """

        # Добавляем условия поиска на основе предпочтений пользователя
        if user_prefs:
            if user_prefs["preferred_gender"] != "any" and user_prefs["preferred_gender"] is not None:
                query += f" AND gender = '{user_prefs['preferred_gender']}'"
            if user_prefs["min_age"] and user_prefs["min_age"] > 0:
                query += f" AND age >= {user_prefs['min_age']}"
            if user_prefs["max_age"] and user_prefs["max_age"] > 0:
                query += f" AND age <= {user_prefs['max_age']}"

        result = self.database.execute(query)

        if not result:
            return None

        # Фильтруем результаты, проверяя предпочтения других пользователей
        suitable_users = []
        for user in result:
            other_prefs = self.get_search_preferences(user[0])

            # Проверяем, подходит ли текущий пользователь под предпочтения найденного
            matches_preferences = True
            if other_prefs:
                # Проверка пола
                if other_prefs["preferred_gender"] != "any" and other_prefs["preferred_gender"] is not None:
                    if user_data[0] != other_prefs["preferred_gender"]:
                        matches_preferences = False

                # Проверка возраста
                if other_prefs["min_age"] and other_prefs["min_age"] > 0:
                    if user_data[1] < other_prefs["min_age"]:
                        matches_preferences = False
                if other_prefs["max_age"] and other_prefs["max_age"] > 0:
                    if user_data[1] > other_prefs["max_age"]:
                        matches_preferences = False

            if matches_preferences:
                suitable_users.append(user)

        if not suitable_users:
            return None

        # Выбираем первого подходящего пользователя
        suitable_user = suitable_users[0]

        # Соединяем пользователей
        self.start_chat(user_id, suitable_user[0])

        # Возвращаем информацию о найденном пользователе
        return {
            "id": suitable_user[0],
            "status": 2,
            "rid": user_id
        }

    def start_chat(self, user_id: int, rival_id: int):
        try:
            # Обновляем статусы обоих пользователей
            self.database.execute(
                "UPDATE users SET status = 2, rid = ? WHERE id = ?",
                (rival_id, user_id)
            )
            self.database.execute(
                "UPDATE users SET status = 2, rid = ? WHERE id = ?",
                (user_id, rival_id)
            )
            self.database.db.commit()
        except Exception as e:
            print(f"Error in start_chat: {e}")
            raise e

    def stop_chat(self, user_id: int, rival_id: int):
        try:
            # Сначала выполним прямой SQL-запрос для обновления
            self.database.execute("""
                UPDATE users 
                SET status = 0, rid = 0 
                WHERE id IN (?, ?)
            """, (user_id, rival_id))

            # Проверим результат обновления
            user_after = self.database.execute(
                "SELECT id, status, rid FROM users WHERE id IN (?, ?)",
                (user_id, rival_id)
            )

            print(f"Debug: After update - Users data: {user_after}")

            # Принудительно сохраняем изменения
            self.database.db.commit()

            return True
        except Exception as e:
            print(f"Error in stop_chat: {e}")
            return False

    def stop_search(self, user_id: int):
        self.database.update({"status": 0, "rid": 0}, {"id": user_id})

    def check_users_state(self, user_id: int, rival_id: int):
        """Проверяет текущее состояние пользователей"""
        result = self.database.execute(
            "SELECT id, status, rid FROM users WHERE id IN (?, ?)",
            (user_id, rival_id)
        )
        return result

    def close(self):
        self.database.close()

    def update_user_gender(self, user_id: int, gender: str):
        if gender == "male":
            self.database.update({"gender": "male"}, {"id": user_id})
        else:
            self.database.update({"gender": "female"}, {"id": user_id})

    def update_user_age(self, user_id: int, age: int):
        self.database.update({"age": age}, {"id": user_id})

    def update_user_referral(self, user_id: int, referral: str):
        self.database.update({"referral": referral}, {"id": user_id})

    def get_user_referral_codes(self, user_id: int):
        try:
            return self.database.execute(
                "SELECT code FROM referral_codes WHERE owner_id = ?",
                (user_id,)
            )
        except:
            return []

    def update_search_preferences(self, user_id: int, preferred_gender: str = None, min_age: int = None,
                                  max_age: int = None):
        updates = {}
        if preferred_gender is not None:
            updates["preferred_gender"] = preferred_gender
        if min_age is not None:
            updates["min_age"] = min_age
        if max_age is not None:
            updates["max_age"] = max_age
        if updates:
            self.database.update(updates, {"id": user_id})

    def get_search_preferences(self, user_id: int):
        result = self.database.select("preferred_gender, min_age, max_age", {"id": user_id}, False)
        if result:
            return {
                "preferred_gender": result[0],
                "min_age": result[1],
                "max_age": result[2]
            }
        return None