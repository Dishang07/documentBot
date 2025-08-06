#in this file ot os decided which function has to be executed
#and converts the natural language to sql query
from common.llm_config import model #importing gemini-2.5 model
from common.sql_executor import execute_sql_query  # getting the sql executor function
import json
import re

def route_query(user_query, metadata):
    # 1. System instruction
    system_instruction = """
You are a data assistant. Your task is to analyze the user query and metadata of the uploaded table and decide:
- Whether the query requires SQL or just a static response.
-Keep it as case insensitive, dont always expect the case sensitive values for the cloumn names.
- If SQL, generate a SQL query based on the metadata.
- If NOT, respond directly with a static answer (without querying anything).
Output format:
{
  "function_call": {
    "name": "execute_sql_query" or "get_static_response",
    "arguments": {
      "query": "<SQL query or static response>"
    }
  }
}
Only use column names and table name from metadata. Don’t assume extra fields.
"""

    # 2. Create input message
    message = [
        {"role": "user", "parts": [
            f"{system_instruction}\n\n"
            f"Table Metadata:\n{json.dumps(metadata, indent=2)}\n\n"
            f"User Query: {user_query}"
        ]}
    ]

    # 3. Call Gemini
    try:
        response = model.generate_content(message)
    except Exception as e:
        return {"error": f"❌ Error calling Gemini: {e}"}

    # 4. Parse JSON from Gemini
    try:
        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```[a-zA-Z]*\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)

        result_json = json.loads(raw_text)
        function_call = result_json.get("function_call", {})#from the function call defined above in system istructions getting the objects

        name = function_call.get("name")
        args = function_call.get("arguments", {})
        query_or_text = args.get("query")

        # 5. If SQL, execute it and return result
        if name == "execute_sql_query":
            query_result = execute_sql_query(query_or_text)
            return {
                "function_call": function_call,
                "result": query_result
            }

        # 6. If static response
        elif name == "get_static_response":
            return {
                "function_call": function_call,
                "result": query_or_text
            }

        else:
            return {
                "error": "❌ Unknown function name in Gemini response.",
                "function_call": function_call,
                "raw": raw_text
            }

    except Exception as e:
        return {
            "error": f"❌ Error parsing LLM response: {e}",
            "raw": response.text
        }
