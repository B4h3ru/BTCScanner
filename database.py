import mysql.connector
# from mysql.connector import Error, MySQLConnection
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import MySQLConnection

from config.settings import db_settings

load_dotenv()

def get_db_connection() -> MySQLConnection:
    """Create and return a database connection"""
    try:
        return mysql.connector.connect(
            host=db_settings.host,
            port=db_settings.port,
            database=db_settings.name,
            user=db_settings.user,
            password=db_settings.password,
            ssl_disabled=False,
            ssl_verify_cert=False,
        )
    
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
    
def get_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=db_settings.host,
        port=db_settings.port,
        database=db_settings.name,
        user=db_settings.user,
        password=db_settings.password,
        ssl_disabled=False,
        ssl_verify_cert=False,
    )

def create_table():
    """Create the bitcoin_wallets table if it doesn't exist"""
    connection = get_db_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS bitcoin_wallets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            private_key_wif VARCHAR(255) NOT NULL,
            private_key_hex VARCHAR(255) NOT NULL,
            public_key TEXT NOT NULL,
            bitcoin_address VARCHAR(120) NOT NULL UNIQUE,
            network VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'bitcoin_wallets' created successfully")
        return True
    except Error as e:
        print(f"Error creating table: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_wallet_data(private_key_wif, private_key_hex, public_key, bitcoin_address, network):
    """Insert wallet data into the database"""
    connection = get_db_connection()
    if connection is None:
        print("Failed to connect to database - skipping database insert")
        return False

    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO bitcoin_wallets (private_key_wif, private_key_hex, public_key, bitcoin_address, network)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (private_key_wif, private_key_hex, public_key, bitcoin_address, network))
        connection.commit()
        print(f"Wallet data inserted successfully for address: {bitcoin_address}")
        return True
    except Error as e:
        print(f"Error inserting wallet data: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()