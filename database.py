import sqlite3
from sqsnip import database as db

class database:
    def __init__(self, db_name: str):
        #id - id телеграма, status - в поиске ли человек, rid - найден ли собеседник, gender - пол, age - возраст, category - категория поиска
        self.database = db(db_name, "users", """
            id INTEGER,
            status INTEGER,
            rid INTEGER,
            gender STRING,
            age INTEGER,
            category STRING,
            referral STRING
        """)

    def get_user_cursor(self, user_id: int) -> dict:
        result = self.database.select("*", {"id": user_id}, False)
        if result is None:
            return None
        result = list(result)

        return {
            "status": result[1],
            "rid": result[2]
        }
    
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
                #print(f"ID: {user[0]}")
                a.append(user[0])
                #print(a)
            return a
        else:
            print("No users found with the specified referral.")

    def new_user(self, user_id: int):
        self.database.insert([user_id, 0, 0, 0, 0, None, None])
        #при создании нового столбца в бд, не заыбывай добавить стартовое значение сюда

    def search(self, user_id: int):
        self.database.update(["rid = 0", {"status": 1}], {"id": user_id})
        result = self.database.select("*", {"status": 1}, True)

        if len(result) == 0:
            return None
        temp_res = list(result[0])[0]
        if temp_res == user_id:
            del result[0]
        if len(result) == 0:
            return None
        result = list(result[0])

        return {
            "id": result[0],
            "status": result[1],
            "rid": result[2]
        }
    
    def start_chat(self, user_id: int, rival_id: int):
        self.database.update({"status": 2, "rid": rival_id}, {"id": user_id})
        self.database.update({"status": 2, "rid": user_id}, {"id": rival_id})

    def stop_chat(self, user_id: int, rival_id: int):
        self.database.update({"status": 0, "rid": 0}, {"id": user_id})
        self.database.update({"status": 0, "rid": 0}, {"id": rival_id})

    def stop_search(self, user_id: int):
        self.database.update({"status": 0, "rid": 0}, {"id": user_id})

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