from flask import Flask
from flaskext.mysql import MySQL


class DB_Handler:
    db_connection_data = {}

    def __init__(self):
        self.db_connection_data = None

    # if db_connection_data == None:
    #     self.db_connection_data["MYSQL_DATABASE_USER"] = "db_admin_tralala"
    #     self.db_connection_data["MYSQL_DATABASE_PASSWORD"] = "tr4l4l4_mysql_db."
    #     self.db_connection_data["MYSQL_DATABASE_DB"] = "tralala"
    #     self.db_connection_data["MYSQL_DATABASE_HOST"] = "localhost"
    #     self.db_connection_data["DB_TABLE_TRALALA_USERS"] = "tralala_users"
    #
    # else:
    #     self.db_connection_data = db_connection_data


    def add_new_user(self, app, email, pw_hash):
        """
            DB-Verbindung nach jedem Call wieder schließen
        """
        mysql = MySQL()
        mysql.init_app(app)
        conn = mysql.connect()
        cursor = conn.cursor()

        
        verified = 0
