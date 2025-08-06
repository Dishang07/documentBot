def extract_metadata(df, table_name):
    metadata = {
        "table_name": table_name,
        "columns": []
    }

    for col in df.columns:
        dtype = str(df[col].dtype)#getting the data type of each column
        #adding each of the column name and its datatype to the metadata
        metadata["columns"].append({
            "name": col,
            "type": dtype
        })

    return metadata
