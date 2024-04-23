import json
from jsonschema import validate
import uule_grabber
from openai import OpenAI
from jobsearch.params import OPENAI_API_KEY

def convert_canonical_name_to_uule_code(canonical_name):

    # convert canonical_name to uule code
    uule_code = uule_grabber.uule(canonical_name)

    return uule_code

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

def convert_json_columns_to_dict(df, columns: list = ['related_links', 'job_highlights']):
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

def request_openai(instructions, input, temperature=0.2, model='gpt-3.5-turbo-1106', json_output=True, print_output=True):

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # specify json output as response format 
    if json_output:
        response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": instructions},
        {"role": "user", "content": input}
        ])
        
    else:
        response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
        {"role": "system", "content": instructions},
        {"role": "user", "content": input}
        ])
    
    # generate    
    output = response.choices[0].message.content
    
    if print_output:
        print(output)
    
    return output

def validate_jsonschema(schema, json_string):

    # Attempt to validate the JSON response against the schema
    try:
        validate(instance=json.loads(json_string), schema=schema)
        return True
    except Exception as e:
        return e  

def count_null_values(json_str):
    # Parse the JSON string
    data = json.loads(json_str)

    null_count = 0

    salary_dict = data['salaire'][0]
    
    null_count += sum(1 for value in salary_dict.values() if value is None)

    return null_count

def read_file(file_path):
    with open(file_path, "r") as f:
        file = f.read()
        
    return file

def create_tagged_prompts(instructions, input):
    
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    B_INST, E_INST = "[INST]", "[/INST]"
    
    func = lambda x: f"{B_INST} {B_SYS}{instructions.strip()}{E_SYS}{str(x).strip()} {E_INST}\n\n"
    
    prompts = list(map(func, input))

    return prompts

def measure_inference_time(llm_inference_function, *args, **kwargs):
    """
    A wrapper function to measure the inference time of an LLM inference call.

    Parameters:
    - llm_inference_function: The LLM inference function to be called.
    - *args: Non-keyword arguments passed to the LLM inference function.
    - **kwargs: Keyword arguments passed to the LLM inference function.

    Returns:
    - result: The result of the LLM inference.
    - inference_time: The time taken for the LLM to generate a response, in seconds.
    """
    start_time = time.time()  # Start time
    result = llm_inference_function(*args, **kwargs)  # Perform the LLM inference
    end_time = time.time()  # End time
    inference_time = end_time - start_time  # Calculate inference time

    return result, inference_time