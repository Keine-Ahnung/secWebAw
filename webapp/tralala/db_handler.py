class DB_Handler:
    db_connection_data = {}

    def __init__(self, db_connection_data):
        if db_connection_data == None:
            self.db_connection_data["MYSQL_DATABASE_USER"] = "db_admin_tralala"
            self.db_connection_data["MYSQL_DATABASE_PASSWORD"] = "tr4l4l4_mysql_db."
            self.db_connection_data["MYSQL_DATABASE_DB"] = "tralala"
            self.db_connection_data["MYSQL_DATABASE_HOST"] = "localhost"

            print("default... " + str(self.db_connection_data))

        else:
            self.db_connection_data = db_connection_data

            print("custom... " + str(self.db_connection_data))

    def add_user(self):

