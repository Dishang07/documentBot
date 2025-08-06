import sqlite3
import pandas as pd

DB_PATH = "uploaded_data.db"

def execute_sql_query(query: str):
    try:
        conn = sqlite3.connect(DB_PATH)

        # Check if it's a SELECT query-as it returns the data
        if query.strip().lower().startswith("select"):
            df = pd.read_sql_query(query, conn)
            result = df.to_dict(orient="records")#converts the df to list of dictionaries
            message = {
                "query": query,
                "result": result
            }
        

        conn.close()
        return message

    except Exception as e:
        return {
            "query": query,
            "error": f"❌ SQL Execution Error: {e}"
        }

def get_static_response():
    return "⚠️ Your query doesn't seem to be related to the uploaded data."
