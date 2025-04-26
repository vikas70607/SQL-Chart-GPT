import csv
import os
from datetime import datetime

USD_to_SGD = 1.35
USD_to_INR = 87

def log_message(Natural_Query: str = '',
                SQL_Query: str = '',
                SQL_Result: str = '',
                SQL_Description: str = '',
                Input_Tokens: int = 0,
                Output_Tokens: int = 0,
                Error: str = ''):
    
    try:
        # Generate filename based on current date
        file_name = f'./logs_{datetime.now().strftime("%Y-%m-%d")}.csv'
        file_exists = os.path.isfile(file_name)  # Check if file already exists

        fieldnames = [
            'Date', 'Natural Query', 'SQL Query', 'SQL Result', 'SQL Description', 
            'Input Tokens', 'Output Tokens', 'Total Tokens', 'Error', 
            'Total Cost (USD)', 'Total Cost (SGD)', 'Total Cost (INR)'
        ]
        
        # Open the CSV file in append mode
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists or os.stat(file_name).st_size == 0:
                writer.writeheader()
            
            # Calculate cost
            USD_cost = (Input_Tokens * 0.00000015) + (Output_Tokens * 0.00000060)

            # Write log row
            writer.writerow({
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Natural Query': Natural_Query,
                'SQL Query': SQL_Query,
                'SQL Result': SQL_Result,
                'SQL Description': SQL_Description,
                'Input Tokens': Input_Tokens,
                'Output Tokens': Output_Tokens,
                'Total Tokens': Input_Tokens + Output_Tokens,
                'Error': Error,
                'Total Cost (USD)': USD_cost,
                'Total Cost (SGD)': USD_cost * USD_to_SGD,
                'Total Cost (INR)': USD_cost * USD_to_INR
            })
    
    except Exception as e:
        print(f"Failed to write to log file: {str(e)}")

