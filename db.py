import mysql.connector
from mysql.connector import errorcode

import utils


def connectDB():
    try:
        cnx = mysql.connector.connect(user='root', password='*******',
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
    return cnx


def CheckHandle(userId):
    con = connectDB()
    if con and con.is_connected():
        try:
            with con.cursor() as cursor:
                query = f"SELECT userName FROM gambleinfo WHERE userId = %s"
                cursor.execute(query, (userId,))
                result = cursor.fetchone()
                if result:
                    con.close()
                    return result[0][0]
                else:
                    con.close()
                    return None
        except mysql.connector.Error as err:
            print(err)
        finally:
            con.close()
            return None
    con.close()
    return None


def CheckIfHandleExists(handle):
    con = connectDB()
    if con and con.is_connected():
        try:
            with con.cursor() as cursor:
                query = f"SELECT userName FROM gambleinfo WHERE userId = %s"
                cursor.execute(query, (handle,))
                result = cursor.fetchone()
                if result:
                    con.close()
                    return True
                else:
                    con.close()
                    return False
        except mysql.connector.Error as err:
            print(err)
        finally:
            con.close()
            return False
    con.close()
    return False

def CheckPermissions(userId):
    con = connectDB()
    userIds_list = ','.join(['%s'] * len(userId))
    if con and con.is_connected() and userIds_list:
        try:
            with con.cursor() as cursor:
                query = f"SELECT userID FROM gambleinfo WHERE userID = %s"
                cursor.execute(query, (userId,))
                result = cursor.fetchall()
                if result:  # Check if there is any result
                    pass
                    # print(f"USER IS IN DB")
                else:
                    insert_query = "INSERT INTO gambleinfo (userID, userName, grubPoints) VALUES (%s, %s, %s)"
                    youtubeHandle = utils.getChannelHandle(userId)
                    cursor.execute(insert_query, (userId, youtubeHandle, 100))
                    # Commit the transaction
                    con.commit()
                    print(f"No grub points found for user {userId}")
        except mysql.connector.Error as err:
            print(err)
        finally:
            con.close()
    else:
        print("Database connection failed")
        con.close()


def addGrubPoints(userIds):
    con = connectDB()  # connect to db
    userIds_list = ','.join(['%s'] * len(userIds))
    if con and con.is_connected() and userIds_list:
        try:
            with con.cursor() as cursor:
                # print("RAN")
                # print(userIds_list)
                # First, check for existing user IDs and update their grubPoints
                query = f"SELECT userID FROM gambleinfo WHERE userID IN ({userIds_list})"
                cursor.execute(query, list(userIds))
                existing_ids = {row[0] for row in cursor.fetchall()}

                # Update grubPoints for existing users
                update_query = "UPDATE gambleinfo SET grubPoints = grubPoints + 50 WHERE userID = %s"
                for user_id in existing_ids:
                    cursor.execute(update_query, (user_id,))

                # Insert new users who do not exist in the database
                new_user_ids = set(userIds) - existing_ids
                insert_query = "INSERT INTO gambleinfo (userID, userName, grubPoints) VALUES (%s, %s, %s)"
                for user_id in new_user_ids:
                    youtubeHandle = utils.getChannelHandle(user_id)
                    cursor.execute(insert_query, (user_id, youtubeHandle, 100))
                # Commit the transaction
                con.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            con.close()
    else:
        con.close()
        print("addGrubPoints: Database connection failed")


def checkGrubPoints(userId):
    con = connectDB()
    userIds_list = ','.join(['%s'] * len(userId))
    grub_points = 0
    if con and con.is_connected() and userIds_list:
        try:
            with con.cursor() as cursor:
                query = f"SELECT grubPoints FROM gambleinfo WHERE userID = %s"
                cursor.execute(query, (userId,))
                result = cursor.fetchall()
                if result:  # Check if there is any result
                    grub_points = result[0][0]  # Access the first row and first column value
                    print(f"Grub Points for user {userId}: {grub_points}")
                else:
                    print(f"No grub points found for user {userId}")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            con.close()
            return 0
        finally:
            con.close()
    else:
        print("checkGrubPoints Database connection failed")
        con.close()
    return grub_points


def addGambleResults(userId, resultValue):
    con = connectDB()
    if con and con.is_connected():
        try:
            with con.cursor() as cursor:
                query = "UPDATE gambleinfo SET grubPoints = grubPoints + %s WHERE userID = %s"
                cursor.execute(query, (resultValue, userId))
            con.commit()  # Commit the transaction
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            con.close()
            return 0
        finally:
            con.close()
    else:
        con.close()
        print("addGambleResults: Database connection failed")


def donatePoints(donor, acceptor, value):
    con = connectDB()
    if con and con.is_connected():
        try:
            with con.cursor() as cursor:
                query = "UPDATE gambleinfo SET grubPoints = grubPoints + %s WHERE userID = %s"
                cursor.execute(query, (-value, donor))
                query2 = "UPDATE gambleinfo SET grubPoints = grubPoints + %s WHERE userName = %s"
                cursor.execute(query2, (value, acceptor))
            con.commit()  # Commit the transaction
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            con.close()
            return 0
        finally:
            con.close()
    else:
        con.close()
        print("addGambleResults: Database connection failed")