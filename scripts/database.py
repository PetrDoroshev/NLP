import os
from os import environ
import psycopg2

import scripts_shared_functions

pg_data = scripts_shared_functions.get_pg_data()
conn = scripts_shared_functions.get_db_connetion(pg_data)

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
