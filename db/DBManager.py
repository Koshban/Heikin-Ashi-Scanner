import mysql.connector

query = """ 
insert  into signal (date, Name, Id, WeeklyBuy, WeeklyApproxBuy, WeeklySell, WeeklyApproxSell)
values (20200610, 'Testing', 1, 1, 0, 1, 0)
"""


def insert_or_update():
    try:
        conn = mysql.connector.connect(host='localhost', database='stockscan',
                                       user='stockscan', password='s')  # Use your DB and Credentials
        cursor = conn.cursor()
        cursor.execute(query)
        print(cursor.rowcount, "Record inserted successfully into Laptop table")
        cursor.close()
    except Exception as e:
        print(str(e))
    finally:
        if (conn.is_connected()):
            conn.close()
            print("MySQL connection is closed")
