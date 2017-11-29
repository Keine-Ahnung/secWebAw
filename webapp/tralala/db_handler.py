from flask import Flask
from flaskext.mysql import MySQL


class DB_Handler:
    db_connection_data = {}
    DB_TABLE_TRALALA_USERS = "tralala_users"

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


    def add_new_user(self, mysql, email, pw_hash):
        """
            DB-Verbindung nach jedem Call wieder schließen

            1: User wurde angelegt
            0: User existiert bereits
            -1: User konnte nicht angelegt werden
        """
        conn = mysql.connect()
        cursor = conn.cursor()

        pid = 1  # unverified
        role_id = 3  # unverified
        verified = 0

        record = [pid, email, pw_hash, role_id, verified]

        # Überprüfe ob User schon existiert
        cursor.execute("select email from " + self.DB_TABLE_TRALALA_USERS + " where email=\"" + email + "\"")
        data = cursor.fetchone()

        if cursor.rowcount != 0: # User existiert bereits
            return 0

        # Füge neuen User zur DB
        try:
            cursor.execute(
                "insert into " + self.DB_TABLE_TRALALA_USERS + " (pid, email, password, role_id, verified) values (%s,%s,%s,%s,%s)",
                record)
            conn.commit()
            conn.close()
            return 1
        except Exception as e:
            conn.close()
            return -1
