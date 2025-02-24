import cx_Oracle
import json
from flask import Flask, request, jsonify
from transformers import T5ForConditionalGeneration, AutoTokenizer
from rapidfuzz import fuzz, process
import inflect
import re
from typing import Dict
import logging
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

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
# Helper: Execute SQL query on Oracle DB
# Create a connection pool during app initialization
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

# Helper: Generate SQL query using T5 model
def generate_sql_query(prompt: str, context: Dict) -> str:
    logging.info(f"Prompt: {prompt}")
    logging.info(f"Context: {context}")
    input_text = f"{prompt} Context: {json.dumps(context)}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs["input_ids"], max_length=512)
    generated_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    logging.info(f"Generated SQL query: {generated_query}")
    return generated_query.strip()



# Helper: Execute SQL query with connection pooling
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
        generated_query = generate_sql_query(prompt, context)

        # Step 3: Execute the SQL query
        execution_result = execute_sql_query(generated_query)

        # Step 4: Return results
        return jsonify({
            "prompt": prompt,
            "generated_query": generated_query,
            "execution_result": execution_result
        })
    except Exception as e:
        logging.error(f"Error in /generate-and-execute: {e}")
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
