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
        "The table 'InvoiceView' contains the following columns:"
        "CustNo (nvarchar), CustName (nvarchar), Address (nvarchar), Address2 (nvarchar), "
        "BarangayName (nvarchar), CityName (nvarchar), ProvinceName (varchar), "
        "PostCode (varchar), Country (varchar), Phone (float), ContactPerson (nvarchar), "
        "Balance (float), CreditLimit (float), FaxNo (varchar), Email (varchar), "
        "PriceGroup (nvarchar), PaymentTerms (varchar), DueDateCalc (varchar), Nation (nvarchar), "
        "SalesRegion (nvarchar), Territory (nvarchar), SalesOffice (nvarchar), DistributorName (nvarchar), "
        "SalesManTerritory (nvarchar), InvNo (nvarchar), InvDt (datetime), DoNo (nvarchar), "
        "DoDt (datetime), OrdNo (nvarchar), DeliveryDate (datetime), Salesman (varchar), "
        "SubTotal (float), GstAmt (float), Discount (float), TotalAmt (float), LineNo (int), "
        "ItemNo (varchar), UOM (varchar), Qty (float), Price (float), LineItemDiscount (float), "
        "SubAmt (float), LineItemGstAmt (float), SalesType (varchar), ItemName (nvarchar), Brand (varchar), "
        "BrandDisplayNo (int), Category (varchar), CategoryDisplayNo (int), Barcode (varchar), "
        "SalesmanTargetAmount (float), PriceFactor (float), DistributorTargetQuantity (float), BaseUOM (nvarchar), "
        "BaseQty (float), SubChannelName (nvarchar), OutletTypeName (varchar), ChannelName (nvarchar), "
        "SalesLocation (nvarchar), SalesmanType (varchar), InventoryQty (float), NationName (varchar), "
        "RegionName (varchar), TerritoryName (varchar), SalesmanTerritoryName (varchar)."
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
                        f"the data is for charts, so you have to make sure data is not too large for charts, put ms sql filters in query accordingly"
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
    print("Chart Types:", chart_types)
    print("SQL Queries:", sql_queries)
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
