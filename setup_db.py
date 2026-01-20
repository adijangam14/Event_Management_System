
import oracledb
import os
from dotenv import load_dotenv
import re

load_dotenv()

def setup_database():
    try:
        connection = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=os.getenv("DB_DSN")
        )
        cursor = connection.cursor()

        with open('event_system/database_setup.sql', 'r') as f:
            sql_script = f.read()
            # Split the script into individual statements
            sql_commands = re.split(r';\s*|/\s*', sql_script)

            for command in sql_commands:
                # Skip empty commands
                if command.strip():
                    try:
                        cursor.execute(command)
                    except oracledb.DatabaseError as e:
                        # We can ignore errors during drop if objects don't exist
                        if "ORA-00942" not in str(e) and "ORA-02289" not in str(e):
                            print(f"Error executing command: {command.strip()}")
                            print(f"Error message: {e}")


        connection.commit()
        print("Database setup completed successfully.")

    except oracledb.DatabaseError as e:
        print(f"Database connection error: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    setup_database()
