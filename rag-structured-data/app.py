import streamlit as st
import pandas as pd
import os
import json
from metadata import extract_metadata#for creating metadata
from route_query import route_query#for selecting the functions 
from common.db import save_to_sqlite#for saving the data to the sqllite

#function to convert raw SQL results into a friendly natural language answer using an LLM.
#we are passing the data-result(output), query-original question and sql-query-sql query that is executed
def format_result_with_llm(data, query, sql_query):
    """Use LLM to convert SQL query results into natural language sentences"""
    from common.llm_config import model #importing gemini model
    
    #if the length of the result is 0 then sql query is not returning anything
    if not data or len(data) == 0:
        return "No data found matching your query."
    
    # Prepare the data for the LLM, by converting it into json
    data_str = json.dumps(data, indent=2)
    
    # Create a prompt for the LLM to format the answer
    prompt = f"""
You are a data assistant. Convert the SQL query result into a natural, conversational sentence.

User's Original Question: "{query}"
SQL Query Executed: {sql_query}
Query Result: {data_str}

Instructions:
- Write a clear, natural sentence that answers the user's question
- Use the actual values from the result
- Make it conversational and easy to understand
- If it's a count, say "The total number of rows is X"
- If it's a sum, say "The total sum of [column] is X"
- If it's an average, say "The average [column] is X"
- If it's multiple records, summarize appropriately
- Don't include technical SQL terms
- Just provide the natural language answer, nothing else

Answer:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback to simple formatting if LLM fails
        if len(data) == 1 and len(data[0]) == 1:#if there is only 1 row or column or the output is just a single number
            value = list(data[0].values())[0]
            return f"The result is {value}."
        else:
            return f"Found {len(data)} records in the data."
        

#st.title("📊 Gemini Structured Data Assistant (SQLite + SQL Routing)")

# Check if file was uploaded from main app, otherwise show file uploader
if 'uploaded_file_path' in st.session_state:
    file_path = st.session_state.uploaded_file_path
    file_name = st.session_state.uploaded_file_name
    table_name = os.path.splitext(file_name)[0]
    file_ext = os.path.splitext(file_name)[-1]
    
    #st.success(f"Processing file: {file_name}")
    
    if file_ext == ".csv":
        df = pd.read_csv(file_path)
    elif file_ext == ".xlsx":
        df = pd.read_excel(file_path)
    else:
        st.error("Unsupported file format")
        st.stop()
        
    uploaded_file_processed = True
else:
    uploaded_file = st.file_uploader("Upload CSV/Excel/JSON", type=["csv", "xlsx"])
    uploaded_file_processed = False
    
    if uploaded_file:
        #getting the file name
        table_name = os.path.splitext(uploaded_file.name)[0]
        #getting the file extension
        file_ext = os.path.splitext(uploaded_file.name)[-1]
        if file_ext == ".csv":
            df = pd.read_csv(uploaded_file)
        elif file_ext ==".xlsx":
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format")
            st.stop()
        uploaded_file_processed = True

if uploaded_file_processed:

    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    # Save the datadrame, table name to SQLite-uploaded_data.db
    save_to_sqlite(df, table_name, "uploaded_data.db")

    # Extract and display metadata pass the table name and the data frame
    metadata = extract_metadata(df, table_name)
    #st.subheader("🧠 Extracted Metadata")
    #st.json(metadata)  # Display metadata as formatted JSON

    # Ask a query
    st.subheader("💬 Ask a Question")
    user_query = st.text_input("Enter your query related to the data")

    if user_query:#when user query is entered
        with st.spinner("🤖 Thinking..."):
            response = route_query(user_query, metadata)
        st.subheader("📬 Gemini Response")
        
        # Check if there's an error
        if "error" in response:
            st.error(response["error"])
            if "raw" in response:#if raw data is given as the output then
                st.write("**Raw Response:**")
                st.text(response["raw"])
        else:
            # Successfully got a response
            function_call = response.get("function_call", {})#the function call from route query is called here
            function_name = function_call.get("name", "❌ No function returned by LLM")
            
            st.write("**Function Called**:", function_name)
            
            # Display the query if it's a SQL function
            if function_name == "execute_sql_query":
                query = function_call.get("arguments", {}).get("query", "No query found")
                st.code(query, language="sql")
            
            # Display the result/answer
            st.subheader("✅ Answer")
            result = response.get("result", "No result found")
            
            if isinstance(result, dict):
                if "result" in result:
                    # It's a SQL query result - format as sentence using LLM
                    sql_result = result["result"]
                    if isinstance(sql_result, list) and len(sql_result) > 0:
                        # Get the SQL query for context
                        sql_query = function_call.get("arguments", {}).get("query", "")
                        # Convert data to natural language using LLM
                        answer_text = format_result_with_llm(sql_result, user_query, sql_query)
                        st.write(answer_text)
                        
                    elif isinstance(sql_result, list) and len(sql_result) == 0:
                        st.write("No data found matching your query.")
                    else:
                        st.write(str(sql_result))
                elif "message" in result:
                    # It's a non-SELECT query result
                    st.write(result["message"])
                elif "error" in result:
                    # It's an SQL error
                    st.error(result["error"])
                else:
                    st.write(result)
            else:
                # It's a static response
                st.write(result)
