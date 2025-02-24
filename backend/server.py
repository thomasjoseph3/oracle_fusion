import cx_Oracle
import json
from flask import Flask, request, jsonify, send_file
from transformers import T5ForConditionalGeneration, AutoTokenizer,T5Tokenizer
from rapidfuzz import fuzz, process
import inflect
import re
from typing import Dict
import logging
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time
import torch
import time
from functools import wraps

def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time} seconds to execute")
        return result
    return wrapper
# Load environment variables from .env file
load_dotenv()
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device,'============')
# Configure logging
logging.basicConfig(level=logging.INFO)

# Database connection details from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME")

# Model path and CORS origin
MODEL_PATH =os.getenv("MODEL_PATH")
CORS_ORIGIN = os.getenv("CORS_ORIGIN")
print(f"Model Path: {MODEL_PATH}")

# Load schema from a file
with open("schema.json", "r") as f:
    schema = json.load(f)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": CORS_ORIGIN}})

# Inflect engine for plural/singular variations
inflect_engine = inflect.engine()

# Define stop words to exclude
STOP_WORDS = {
    "is", "as", "list", "all", "get", "retrieve", "find", "to", "for",
    "on", "by", "in", "and", "of", "the", "from", "assigned"
}

dsn_tns = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE_NAME)
pool = cx_Oracle.SessionPool(DB_USER, DB_PASSWORD, dsn_tns, min=2, max=10, increment=1, threaded=True)
# Load the model and tokenizer
logging.info("Loading model and tokenizer...")
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
logging.info("Model and tokenizer loaded successfully.")




# Helper: Generate variations for singular/plural forms
def generate_variations(word):
    return {word, inflect_engine.singular_noun(word) or word, inflect_engine.plural(word)}

# Helper: Traverse relationships to find related tables
def traverse_relationships(table, schema, relevant_tables):
    if table not in schema:
        return
    foreign_keys = schema[table].get("foreign_keys", {})
    for related_table in foreign_keys.values():
        if related_table not in relevant_tables:
            relevant_tables.add(related_table)
            traverse_relationships(related_table, schema, relevant_tables)

# Main logic to find relevant tables
def find_relevant_tables(prompt, schema):
    prompt_words = [word for word in re.findall(r'\w+', prompt.lower()) if word not in STOP_WORDS]

    table_map = {}
    column_map = {}
    for table, details in schema.items():
        for variation in generate_variations(table.lower()):
            table_map[variation] = table
        for column in details.get("columns", []):
            for variation in generate_variations(column.lower()):
                column_map[variation] = table

    matched_tables = set()
    for word in prompt_words:
        table_match = process.extractOne(word, table_map.keys(), scorer=fuzz.token_set_ratio)
        if table_match and table_match[1] > 60:
            matched_tables.add(table_map[table_match[0]])

        column_match = process.extractOne(word, column_map.keys(), scorer=fuzz.token_set_ratio)
        if column_match and column_match[1] > 60:
            matched_tables.add(column_map[column_match[0]])

    relevant_tables = set(matched_tables)
    for table in matched_tables:
        traverse_relationships(table, schema, relevant_tables)

    return relevant_tables


from datetime import datetime

def format_if_date(value):
    if value is None:
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y")  # Format as "DD Mon YYYY"
    
    # If the value is a string, try to parse it
    try:
        dt = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%d %b %Y")
    except ValueError:
        return value  # Return the original value if parsing fails

# Helper: Generate SQL query using T5 model
def generate_sql_query(prompt: str, context: Dict) -> str:
    logging.info(f"Prompt: {prompt} ")
    logging.info(f"Context: {context}")
    input_text = f"Generate Oracle DB query for the prompt based on the prompt and context.{prompt} Context: {json.dumps(context)}"
    print(f"Input text: {input_text}")
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs["input_ids"], max_length=512)
    generated_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    logging.info(f"Generated SQL query: {generated_query}")
    return generated_query.strip()

@timer_decorator
def create_desc_query_result(prompt, response):
    # res={}
    # keys = response['columns']
    # for i in range(len(keys)):
    #     res[keys[i]]=[]
    #     for j in range(len(response['rows'])):
    #         res[keys[i]].append(response['rows'][j][i])

    input_text = f"instruction : give me a descriptive answer (at least three words) to prompt based on datasbase query result .prompt :  {prompt} , context:{json.dumps(response)}"
    
    print(input_text, "@@@@")  # Debugging

    # Tokenize input
    inputs = tokenizer(
        input_text, 
        return_tensors="pt", 
        max_length=512, 
        truncation=True, 
        padding="max_length"
    )  # Ensure tensors are on the correct device

    # # Generate output
    # outputs = model_general.generate(inputs["input_ids"], max_length=512)

    # # Decode and return
    # description = tokenizer.decode(outputs[0], skip_special_tokens=True)
    description='good'
    print(description, "@@@@")
    return description.replace("\"", "").strip()


import re

def determine_rendering_type(response):
    """
    Determines the rendering type based on the structure of execution results after removing ID and UPDATEDAT columns.

    Conditions:
    - If there is one string column and the rest are numeric -> "graph"
    - If there are 2 or fewer total columns -> "text"
    - Otherwise -> "table"

    :param response: Dictionary containing execution results
    :return: Updated dictionary with rendering_type
    """
    execution_result = response.get("execution_result", {})
    columns = execution_result.get("columns", [])
    rows = execution_result.get("rows", [])

    if not columns or not rows:
        response["rendering_type"] = "text"  # Default fallback if data is empty
        return response

    # Identify ID columns and "UPDATEDAT"
    id_columns = {col for col in columns if re.search(r'\bID\b', col, re.IGNORECASE)}
    columns_to_remove = id_columns | {"UPDATEDAT"}  # Remove both ID columns and UPDATEDAT

    # Filter columns and corresponding row values
    filtered_columns = [col for col in columns if col not in columns_to_remove]
    filtered_indexes = [i for i, col in enumerate(columns) if col not in columns_to_remove]
    filtered_rows = [[format_if_date(row[i]) for i in filtered_indexes] for row in rows]

    # Check if we have any valid columns left
    if not filtered_columns:
        response["rendering_type"] = "text"
        return response

    # Determine column types from the first row
    string_columns = []
    number_columns = []

    first_row = filtered_rows[0]  # Assume all rows have the same structure
    for i, value in enumerate(first_row):
        if isinstance(value, (int, float)):
            number_columns.append(filtered_columns[i])
        else:
            string_columns.append(filtered_columns[i])

    # Apply conditions to determine rendering type
    if len(string_columns) == 1 and len(number_columns) >= 1:
        rendering_type = "graph"
    elif len(filtered_columns) <= 1 and len(filtered_rows)<=1:
        rendering_type = "text"
    else:
        print(string_columns,number_columns,'======================')
        rendering_type = "table"

    # Update response with filtered data and rendering type
    response["execution_result"]["columns"] = filtered_columns
    response["execution_result"]["rows"] = filtered_rows
    response["type"] = rendering_type

    return response







def execute_sql_query(query: str):
    connection = None
    cursor = None
    try:
        connection = pool.acquire()  # Acquire connection from the pool
        cursor = connection.cursor()

        query = query.strip()
        if query.endswith(";"):  # Remove trailing semicolon
            query = query[:-1]
        logging.info(f"Executing SQL query: {query}")
        cursor.execute(query)
        if query.lower().startswith("select"):
            result = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return {"columns": columns, "rows": result}
        else:
            connection.commit()
            return {"message": "Query executed successfully"}
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logging.error(f"Database error: {error.message}")
        raise Exception(f"Database error: {error.message}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            pool.release(connection)  # Release connection back to the pool



# API endpoint to find relevant tables, generate query, and execute
@app.route("/generate-and-execute", methods=["POST"])
def generate_and_execute():
    try:
        # Parse user input
        data = request.get_json()
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing 'prompt' in the request body."}), 400

        prompt = data["prompt"].strip()
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # Step 1: Find relevant tables
        relevant_tables = find_relevant_tables(prompt, schema)
        context = {table: schema[table] for table in relevant_tables}

        # Step 2: Generate SQL query using the T5 model
        start_time = time.time()
        generated_query = generate_sql_query(prompt, context)
        end_time = time.time()

        print(f"Function took {end_time - start_time} seconds to execute")

        

        # Step 3: Execute the SQL query
        execution_result = execute_sql_query(generated_query)
        print(execution_result,'======================')
        response={
            "prompt": prompt,
            "generated_query": generated_query,
            "execution_result": execution_result
        }
        response = determine_rendering_type(response)
        response["description"] = create_desc_query_result(prompt, execution_result)

        # Step 4: Return results
        return jsonify(response)
        return jsonify({
            "prompt": prompt,
            "generated_query": generated_query
        })
    except Exception as e:
        logging.error(f"Error in /generate-and-execute: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/generate_oracledb_query", methods=["POST"])
def generate_oracledb_query():
    try:
        # Parse user input
        data = request.get_json()
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing 'prompt' in the request body."}), 400

        prompt = data["prompt"].strip()
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # Step 2: Generate SQL query using the T5 model
        start_time = time.time()
        generated_query = generate_sql_query(prompt, schema)
        end_time = time.time()

        print(generated_query,'[][][][][][][][]')

        print(f"Function took {end_time - start_time} seconds to execute")

        # Step 4: Return results
        return jsonify({
            "prompt": prompt,
            "generated_query": generated_query
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500    






# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
