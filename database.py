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
            category INTEGER
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
    
    def new_user(self, user_id: int):
        self.database.insert([user_id, 0, 0, 0, 0, "Неизвестно"])
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