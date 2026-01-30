# db.py
# Handles the connection to the Oracle database using a connection pool.

import oracledb
import threading
from .config import DB_CONFIG

# Global variable to hold the connection pool
pool = None

def init_pool():
    """
    Initializes the connection pool.
    This should be called once when the application starts.
    """
    global pool
    try:
        pool = oracledb.create_pool(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dsn=DB_CONFIG["dsn"],
            min=2,  # Minimum number of connections in the pool
            max=5,  # Maximum number of connections in the pool
            increment=1  # How many connections to create when more are needed
        )
        print("Connection pool created successfully.")

    except oracledb.DatabaseError as e:
        print(f"Error creating the connection pool: {e}")
        # The application should not proceed without a database connection
        raise

def get_connection():
    """
    Acquires a connection from the pool.
    """
    global pool
    if not pool:
        print("Pool is not initialized. Call init_pool() first.")
        # Depending on the app's design, you might want to auto-initialize here,
        # but explicit initialization is safer.
        init_pool()

    try:
        connection = pool.acquire()
        return connection
    except oracledb.DatabaseError as e:
        print(f"Error acquiring connection from pool: {e}")
        return None

def close_pool():
    """
    Closes the connection pool.
    This should be called when the application is shutting down.
    """
    global pool
    if pool:
        # The busy_timeout forces connections to be returned to the pool,
        # which is useful if some threads failed to release their connections.
        pool.close(force=True)
        print("Connection pool closed.")
        pool = None
