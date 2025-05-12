from flask import Flask, request, jsonify
from utils.charts import execute_matplotlib_and_get_base64
from utils.chart_sql import execute_sql_query
from utils.chart_ai import chart_sql_query_generation, generate_chart_code_and_description
from flask_cors import CORS
from utils.ai import natural_to_sql_query, sql_result_description
from utils.sql import execute_sql_query
from utils.logger import log_message


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/sqlgpt')
def index():
    return jsonify({'message': 'APP running successfully'}), 200

@app.route('/sqlgpt/query', methods=['POST'])
def convert_query():
    try:
        # Extract JSON data from the POST request
        data = request.get_json()

        # If no data or the required 'query' field is missing, return an error
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        if not data or 'territory_id' not in data:
            return jsonify({"error": "Territory ID is required"}), 400
        
        natural_query = data['query'] # Get the natural language query from the input data
        salesman_territory_list = data.get('territory_id', [])
        customer_list = data.get('customer_no', [])

        # Generate SQL query from the natural language query
        sql_query,p1,c1 = natural_to_sql_query(natural_query,salesman_territory_list,customer_list)

        # Check for SQL injection by analyzing the generated SQL query
        if sql_query == 'Injection':
            return jsonify({
                "warning": "Potential SQL injection detected. We recommend modifying your query to read-only.",
                "error": "Data-modifying queries are not allowed for security reasons."
            }), 403

        # Execute the generated SQL query and retrieve the result
        sql_result = execute_sql_query(sql_query)

        # Describe the SQL result in a user-friendly way
        described_result,p2,c2 = sql_result_description(sql_result, natural_query)
        
        # Log the request details including timestamp, queries, and result
        log_message('logs.csv',natural_query,sql_query,sql_result,described_result,p1+p2,c1+c2)
        
        # Return the SQL query, the result, and the human-readable description as JSON response
        return jsonify({
            "sql_query": sql_query,
            "sql_result": sql_result,
            "described_result": described_result
        }), 200

    # Handle missing keys (e.g., if the 'query' key is not present in the JSON data)
    except KeyError as ke:
        error_message = f'Missing key: {ke}'
        log_message('logs.csv',Error=error_message)  # Log the error
        return jsonify({"error": error_message}), 400

    # Handle all other exceptions, log the error, and return a generic server error
    except Exception as e:
        error_message = str(e)
        log_message('logs.csv',Error=error_message)  # Log the error details
        return jsonify({"error": "Internal server error", "details": error_message}), 500

@app.route("/sqlgpt/generate_charts", methods=["POST"])
def generate_charts():
    data = request.get_json()

    # Read query and territory from request
    query = data.get("query")
    sales_territory_id = data.get("sales_territory_id")

    # Check if required fields are present
    if not query or not sales_territory_id:
        return jsonify({"error": "Missing 'query' or 'sales_territory_id' in request."}), 400

    # Step 1: Generate chart types and SQL queries
    chart_types, queries = chart_sql_query_generation(query, sales_territory_id)
    
    results = []
    
    for query in queries:
        result = execute_sql_query(query)
        if result is None:
            return jsonify({"error": f"No results for query: {query}"}), 400
        results.append(result)
    
    codes = []
    texts = []
    for chart, result in zip(chart_types, results):
        code, text = generate_chart_code_and_description(chart, result, query)
        codes.append(code)
        texts.append(text)
    
    images = []
    for code in codes:
        image = execute_matplotlib_and_get_base64(code)
        images.append(image)
    
    # Step 2: Create the final response array
    response_data = []
    for sql_query, text, image in zip(queries, texts, images):
        obj = {
            "sql_query": sql_query,
            "text": text,
            "image_base64": image
        }
        response_data.append(obj)
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)
