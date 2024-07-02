import mysql.connector
from mysql.connector import errorcode

def connectDB():
    try:
        cnx = mysql.connector.connect(user='root', password='password',
                                      host='127.0.0.1',
                                      database='youtube_chat')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
    print("Connected to MySQL database")
    return cnx

def addGrubPoints(userIds):
    con = connectDB()  # connect to db
    userIds_list = ','.join(['%s'] * len(userIds))
    if con and con.is_connected() and userIds_list:
        try:
            with con.cursor() as cursor:
                # print("RAN")
                # print(userIds_list)
                # First, check for existing user IDs and update their grubPoints
                userIds_list = ','.join(['%s'] * len(userIds))
                query = f"SELECT userID FROM gambleinfo WHERE userID IN ({userIds_list})"
                cursor.execute(query, list(userIds))
                existing_ids = {row[0] for row in cursor.fetchall()}

                # Update grubPoints for existing users
                update_query = "UPDATE gambleinfo SET grubPoints = grubPoints + 10 WHERE userID = %s"
                for user_id in existing_ids:
                    cursor.execute(update_query, (user_id,))

                # Insert new users who do not exist in the database
                new_user_ids = set(userIds) - existing_ids
                insert_query = "INSERT INTO gambleinfo (userID, grubPoints) VALUES (%s, %s)"
                for user_id in new_user_ids:
                    cursor.execute(insert_query, (user_id, 100))
                # Commit the transaction
                con.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            con.close()
