import re
import openai
from dotenv import load_dotenv
import os
from typing import List

os.environ.pop('OPENAI_API_KEY', None)

load_dotenv()

# Regex pattern to find individual words in the query
word_pattern = re.compile(r'\b\w+\b')

# Set of SQL keywords that can modify data (write operations)
modify_keywords = {'ALTER', 'CREATE', 'DELETE', 'DROP', 'INSERT', 'MERGE',
                   'REPLACE', 'TRUNCATE', 'UPDATE', 'UPSERT'}

# OpenAI API key for GPT-4 API access (ensure to secure this key in production)
openai.api_key = os.getenv('OPENAI_API_KEY')

def convert_mysql_to_sqlserver(query: str) -> str:
    """
    Detects if a query is written for MySQL and converts it to SQL Server format.
    Returns the converted query if MySQL syntax is detected, else returns the original query.
    """
    # Detect if query uses MySQL-specific syntax (e.g., LIMIT)
    if "LIMIT" in query.upper():
        # Convert LIMIT clause to TOP clause for SQL Server
        # Regex pattern to capture LIMIT with optional offset (e.g., LIMIT 5 or LIMIT 2, 10)
        limit_pattern = re.compile(r"LIMIT\s+(\d+)(?:,\s*(\d+))?", re.IGNORECASE)
        limit_match = limit_pattern.search(query)
        
        if limit_match:
            if limit_match.group(2):  # If there's an offset and limit, e.g., LIMIT 2, 10
                offset = int(limit_match.group(1))
                limit = int(limit_match.group(2))
                
                # SQL Server equivalent: use ROW_NUMBER() with offset and limit
                converted_query = re.sub(r"SELECT", f"SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS RowNum,", query, 1, re.IGNORECASE)
                converted_query = re.sub(limit_pattern, f"WHERE RowNum BETWEEN {offset + 1} AND {offset + limit}", converted_query)
                return f"WITH NumberedResults AS ({converted_query}) SELECT * FROM NumberedResults WHERE RowNum BETWEEN {offset + 1} AND {offset + limit};"
            else:  # If there's only a limit, e.g., LIMIT 10
                limit = limit_match.group(1)
                converted_query = re.sub(r"SELECT", f"SELECT TOP {limit}", query, 1, re.IGNORECASE)
                converted_query = re.sub(limit_pattern, "", converted_query)
                return converted_query

    # If no MySQL-specific syntax is detected, return the original query
    return query


# Function to determine if a SQL query is read-only (safe from modifying data)
def is_read_only_query(query):
    # Convert query to uppercase and extract all the words
    words = set(word_pattern.findall(query.upper()))
    
    # If any modifying keywords are found, the query is not read-only
    if words & modify_keywords:
        return False
    
    # Ensure the query has a SELECT statement to verify it's a read operation
    return 'SELECT' in words

# Function to extract the SQL query from a block of text formatted in Markdown
def extract_sql_query(text):
    # Regex pattern to match SQL query inside a code block (```sql ... ```)
    match = re.search(r"```sql\n(.*?)\n```", text, re.DOTALL)
    
    # If match is found, return the SQL query, else return None
    if match:
        return match.group(1).strip()
    else:
        return None

# Function to convert natural language queries into SQL using GPT-4 API

def natural_to_sql_query(natural_query: str, salesman_territory_list: List[str], customer_no:List[str]=[]) -> str:
    # Define the prompt describing the structure of the 'InvoiceView' table and the SalesManTerritory filter
    prompt = (
        "The table 'InvoiceView' contains the following columns:"
        "CustNo (nvarchar), CustName (varchar), Address (varchar), Address2 (varchar), "
        "BarangayName (nvarchar), CityName (nvarchar), ProvinceName (nvarchar), "
        "PostCode (varchar), Country (varchar), Phone (varchar), ContactPerson (varchar), "
        "Balance (float), CreditLimit (float), FaxNo (varchar), Email (varchar), "
        "PriceGroup (varchar), PaymentTerms (varchar), DueDateCalc (varchar), Nation (varchar), "
        "SalesRegion (nvarchar), Territory (nvarchar), SalesOffice (nvarchar), DistributorName (nvarchar), "
        "SalesManTerritory (nvarchar), InvNo (varchar), InvDt (datetime), DoNo (varchar), "
        "DoDt (datetime), OrdNo (varchar), DeliveryDate (datetime), Salesman (varchar), Discount (float), "
        "SubTotal (float), GstAmt (float), TotalAmt (float), PaidAmt (float), EWTAmt (float), DueDate (datetime), "
        "LineNo (varchar), ItemNo (varchar), UOM (varchar), Qty (float), Price (float), LineItemDiscount (float), "
        "SubAmt (float), LineItemGstAmt (float), SalesType (varchar), ItemName (varchar), Brand (varchar), "
        "Category (varchar), Barcode (varchar), SalesmanTargetAmount (float), Pricefactor (float), "
        "DistributorTargetQuantity (float), BaseUOM (varchar), BaseQty (float), SubChannelName (nvarchar), "
        "OutletTypeName (nvarchar), ChannelName (nvarchar), SalesLocation (nvarchar), SalesmanType (varchar), "
        "ts (timestamp)."
        "\n"
        "and"
        "\n"
        "The table 'MonthlyRoutePlan' contains the following columns:"
        "CustNo (nvarchar), RouteDate (datetime), Name (nvarchar), WD (int), SalesManTerritory (nvarchar)"
        
        "Additionally, filter the results to include only records where SalesManTerritory is one of the values provided in the list."
        "Additionally, a CustNo is also provided, please try to filter results based on it but only if the query is relevant to the customer details otherwise ignore it"

        "There are some terms like, Customers are called outlet too, distinct custno for total outlets"
        
    )

    # Convert the salesman_territory_list and customer nameto a string format for inclusion in the prompt
    territory_list_str = ', '.join([f"'{territory}'" for territory in salesman_territory_list])
    customer_no_str = ', '.join([f"'{no}'" for no in customer_no])

    # GPT-4 model completion call to generate a SQL query based on natural language input and SalesManTerritory filter
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": (
                    "You are an AI agent that translates natural language queries into SQL queries for MS SQL Server. "
                    "Write only the SQL query, nothing else. "
                    f"Based on the table structures provided: {prompt}, "
                    f"generate an SQL query for the following request: '{natural_query}', "
                    f"including a filter to limit the SalesManTerritory to the following list: {territory_list_str}."
                    f"these are the customer no: {customer_no_str}, use this only if query is relevant to customer details."
                )
            }
        ]
    )

    # Extract the generated SQL query
    sql_query = response.choices[0].message.content.strip()

    # Check if the query is safe (read-only) and return the query or flag it as 'Injection'
    sql_query = extract_sql_query(sql_query)
    if is_read_only_query(sql_query):
        return convert_mysql_to_sqlserver(sql_query), response.usage.prompt_tokens, response.usage.completion_tokens
    else:
        return 'Injection'


# Function to describe SQL results in natural language, based on the question
def sql_result_description(formatted_result: str, natural_query: str) -> str:
    
    # GPT-4 model completion call to generate a description of SQL query results
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You describe SQL results in natural language based on the given question. (Don't use any Currency Signs)"},
            {"role": "user", "content": f"Question : {natural_query} \nSQL Result : {formatted_result}"}
        ]
    )
    
    described_result = response.choices[0].message.content
    return described_result,response.usage.prompt_tokens, response.usage.completion_tokens

# Example usage for testing the script
if __name__ == "__main__":
    natural_query = "show me total revenue"
    print(natural_to_sql_query(natural_query,['002-PSS11']))
