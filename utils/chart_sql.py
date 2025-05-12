import pyodbc
from dotenv import load_dotenv
import os

os.environ.pop('DB_CONNECTION_STRING', None)

load_dotenv()

# Function to execute the provided SQL query and return formatted results
def execute_sql_query(sql_query):
    """
    Executes a SQL query on a SQL Server database and returns the result in a textual format.

    Args:
        sql_query (str): The SQL query to be executed.

    Returns:
        str: A formatted string of the query results or an error message.
    """

    # Database connection string using pyodbc
    conn = pyodbc.connect(os.getenv('DB_CONNECTION_STRING'))
    # Check if the connection was successful
    if conn is None:
        return "Failed to connect to the database."
    cursor = conn.cursor()  # Create a cursor object to interact with the database

    try:
        # Execute the SQL query
        cursor.execute(sql_query)

        # Fetch the column names from the query result
        columns = [column[0] for column in cursor.description]
        
        # Fetch all rows from the executed query
        results = cursor.fetchall()

        # If no results are returned, return an appropriate message
        if not results:
            return None

        # Format the results into a readable string
        formatted_result = "Here are the results:\n"
        for idx, row in enumerate(results, start=1):
            # Format each row with column names and corresponding values
            formatted_result += f"Row {idx}: [" + ", ".join([f"{columns[i]}: {row[i]}" for i in range(len(columns))]) + "]\n"

        return formatted_result,os.getenv('DB_CONNECTION_STRING')
    
    except pyodbc.Error as e:
        # Return an error message if the query fails
        return f"Error executing query: {str(e)}"

    finally:
        # Always close the cursor and connection to free up resources
        cursor.close()
        conn.close()


# Example usage of the function
if __name__ == "__main__":
    # Define the SQL query to be executed
    sql_query = "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_CATALOG = 'SimplrPayGateway' ORDER BY TABLE_NAME, ORDINAL_POSITION;"    
    # Call the function to execute the query and get results
    data = execute_sql_query(sql_query)
    
    # Print the results to the console
    print(data)
