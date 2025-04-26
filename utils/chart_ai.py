import requests
import json
import os
from dotenv import load_dotenv


os.environ.pop('OPENAI_API_KEY', None)
load_dotenv()

# Define the URL and the API Key
url = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def chart_sql_query_generation(query,territory_list_str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    prompt = (
        "The table 'Invoice' contains the following columns:"
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
        )

    # Prepare the data payload
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                    "content": (
                        "You are an AI agent that translates natural language visualisation requests into chart type and relevant SQL queries for MS SQL Server. "
                        f"Based on the table structure provided: {prompt}, "
                        f"Additionally, filter the results to include only records where SalesManTerritory is : {territory_list_str}."
                        f"generate Chart types and SQL queries for the following request: '{query}'"
                    )
            }
        ],
        "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "Charts_and_SQL_Query",
            "schema": {
                "type": "object",
                "properties": {
                    "Chart Type": {
                        "description": "Chart Type Such as line, bar, pie etc",
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "SQL Query": {
                        "description": "SQL Queries (for SQL server) to fetch data relevant to this chart type",
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
            }


    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    res = response.json()
    content = res["choices"][0]["message"]["content"]

    parsed_content = json.loads(content)

    # Accessing data from the parsed JSON
    chart_types = parsed_content["Chart Type"]
    sql_queries = parsed_content["SQL Query"]
    return chart_types, sql_queries

def generate_chart_code_and_description(chart:str, result:str, query:str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    
    print(result)
    
    # Prepare the data payload
    data = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": (
                    f"create a matplotlib code to generate a chart of type: {chart} using the following data: {result}"
                    "Make sure you use correct labels and colors that gives a modern and minimal visual representation to the chart."
                    "If data is too large for charts you can remove data too but do it very carefully, always you double quote string for your labels and titles."
                    "Also, make sure to use the correct chart type according to the data provided and charts should look visually appealing."
                    "dont show the chart, save it to disk as 'chart.png'."
                    f"Also, provide a short description of the chart and its significance and analysis according to this query{query}."
                )
        }
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "Matplotlib_Code",
            "schema": {
                "type": "object",
                "properties": {
                    "Code": {
                        "description": "Python code using Matplotlib to generate the requested chart",
                        "type": "string",
                    },
                    "Text": {
                        "description": "Textual description of the data and chart, how it relates to the query.",
                        "type": "string",
                    }
                }
            }
        }
    }
    }



    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    res = response.json()
    content = res["choices"][0]["message"]["content"]

    parsed_content = json.loads(content)

    # Accessing data from the parsed JSON
    code = parsed_content["Code"]
    text = parsed_content["Text"]
    return code,text