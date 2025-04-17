import mysql.connector
from mysql.connector import Error


def create_connection(host_name, user_name, user_password, db_name, port_number):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            port=port_number
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            print(row)
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def main():
    # MySQL database credentials
    host_name = "localhost"
    user_name = "root"
    user_password = "1234"
    db_name = "mydatabase"
    port_number = "3306"
    # Create a database connection
    connection = create_connection(host_name, user_name, user_password, db_name, port_number)
    # Example query to test the connection
    test_query = "SELECT * FROM your_table LIMIT 5;"
    # Execute the query
    execute_query(connection, test_query)
    # Close the connection
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")


if __name__ == "__main__":
    main()