import os
from os import environ
import psycopg2

conn = psycopg2.connect(dbname="postgres", user=f"{os.environ['USER']}",
                        password=f"{os.environ['PASSWORD']}", host=f"{os.environ['HOST']}")


def create_db(conn, db_name):

    cursor = conn.cursor()
    conn.autocommit = True

    create_db_query = f"CREATE DATABASE {db_name}"

    try:
        cursor.execute(create_db_query)

    except psycopg2.DatabaseError as err:
        print("Error: ", err)

    cursor.close()

def init_schema(conn, filename):

    cursor = conn.cursor()
    conn.autocommit = True

    try:
        cursor.execute(open("filename", "r").read())

    except psycopg2.DatabaseError as err:
        print("Error: ", err)

    cursor.close()



