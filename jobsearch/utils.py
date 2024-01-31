import json

def convert_dict_columns_to_json(df, columns):
    """
    Converts specified dictionary columns in a DataFrame to JSON strings.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the columns to be converted.
    columns (list): A list of column names to convert from dictionaries to JSON strings.

    Returns:
    pandas.DataFrame: The DataFrame with the specified columns converted to JSON strings.
    """
    for column in columns:
        if column in df:
            df[column] = df[column].apply(json.dumps)
    return df

def convert_json_columns_to_dict(df, columns):
    """
    Converts specified JSON string columns in a DataFrame back to dictionaries.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the columns to be converted.
    columns (list): A list of column names to convert from JSON strings to dictionaries.

    Returns:
    pandas.DataFrame: The DataFrame with the specified columns converted back to dictionaries.
    """
    for column in columns:
        if column in df:
            df[column] = df[column].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    return df

def export_dataframe_to_csv(df, output_path="."):
    df.to_csv(output_path, mode='a', index=False, header=False)

def get_dataframe_memory_usage(df):
    mem = (df.memory_usage(deep=True) / (1024*1024)).round(2)
    return mem
