import openai
import numpy as np
import pandas as pd

import datetime
import sqlite3

# convert literal list-like string representation to list type
import ast

# libraries used to remove duplicates using tf-idf and cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from scipy.sparse import coo_matrix

#from jobsearch.preprocess import preprocess
from jobsearch.params import DB_PATH


def convert_to_tfidf(corpus):
    """
    This function vectorizes a text corpus using Term Frequency-Inverse Document Frequency (TF-IDF) methodology
    and returns the resultant TF-IDF matrix.

    Args:
        corpus (iterable of str): The text corpus to vectorize. It can be a list or array-like structure containing text data.

    Returns:
        scipy.sparse.csr.csr_matrix: The TF-IDF matrix representation of the provided text corpus.
    """
    # Initialize a TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # Convert the corpus into a NumPy array of strings
    corpus_np = np.array(corpus, dtype=str)

    # Transform the corpus to a TF-IDF matrix
    tfidf_matrix_np = tfidf_vectorizer.fit_transform(corpus_np)

    return tfidf_matrix_np

def compute_cosine_similarity(tfidf_matrix_np):
    """
    Computes the cosine similarity between pairs of documents using their TF-IDF representations.

    Args:
        tfidf_matrix_np (scipy.sparse.csr.csr_matrix): The TF-IDF matrix representation of a text corpus.

    Returns:
        np.ndarray: A 2D numpy array containing cosine similarity values between each pair of documents.
    """
    # Compute cosine similarity between pairs of documents
    cosine_matrix = (tfidf_matrix_np) * (tfidf_matrix_np.T)

    # Convert cosine similarity to numpy array
    cosine_matrix = cosine_matrix.toarray()

    # Set diagonal of cosine similarity to 0, as we don't need to compare a document with itself
    np.fill_diagonal(cosine_matrix, 0)

    return cosine_matrix

def convert_cosine_similarity_to_coo(cosine_matrix):
    """
    Converts a cosine similarity matrix to a coordinate (COO) matrix representation for efficient operations.

    Args:
        cosine_sim (np.ndarray): A 2D numpy array containing cosine similarity values between pairs of documents.

    Returns:
        scipy.sparse.coo.coo_matrix: The COO matrix representation of the provided cosine similarity matrix.
    """
    # Convert cosine similarity to a coordinate (COO) matrix
    cosine_coo = coo_matrix(cosine_matrix)

    return cosine_coo


def filter_over_threshold(cosine_matrix, threshold=0.8):
    """
    Filter records based on cosine similarity.

    Args:
        cosine_matrix (np.ndarray): 2D numpy array containing cosine similarity values.
        threshold (float, optional): Minimum cosine similarity value to consider a record as similar. Defaults to 0.8.

    Returns:
        dict: Dictionary where keys are the index of the record and values are the indices of records above the threshold.
    """
    over_threshold_dict = {}

    for i in range(cosine_matrix.shape[0]):
        # Extract relevant similarity scores
        cos_val = cosine_matrix[i]

        # Get record indices with scores above the threshold
        over_threshold_indices = np.where(cos_val > threshold)[0]
        over_threshold_dict[i] = over_threshold_indices

    return over_threshold_dict

def filter_by_bounds(job_data, over_threshold_dict):
    """
    Filter down the compared records based on salary bounds using the indices filtered by cosine similarity.

    Args:
        job_data (pd.DataFrame): DataFrame containing job descriptions and extracted salary information.
        over_threshold_dict (dict): Dictionary from `filter_over_threshold` containing indices of records above the threshold.

    Returns:
        set: Indices of duplicated records.
    """
    duplicated_dict = {}

    for i, similar_indices in over_threshold_dict.items():
        # Filter by salary: identical lower & upper bound to original record
        og_record = job_data.iloc[i]
        same_bounds = job_data.iloc[similar_indices].loc[(job_data.lower_bound == og_record.lower_bound) &
                                                         (job_data.upper_bound == og_record.upper_bound)]

        # Add indices to dict
        duplicated_dict[i] = list(same_bounds.index.values)

    # Get duplicated record's indices
    duplicated_indices = set()
    # keep unique indices only
    for value in duplicated_dict.values():
        duplicated_indices = duplicated_indices.union(value)

    return duplicated_indices



def drop_columns(df, cols=['job_highlights', 'related_links', 'thumbnail']):
    """
    Drop specified columns from a pandas DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame from which columns are to be dropped.
    cols (list of str): List of column names to be dropped.

    Returns:
    pandas.DataFrame: A DataFrame with the specified columns removed.
    """
    df = df.drop(cols, axis=1)
    return df

def cast_cols_to_str(df, cols_to_str):
    """
    Convert specified columns of a DataFrame to string data type.

    Parameters:
    df (pandas.DataFrame): The DataFrame whose columns are to be converted.
    cols_to_str (list of str): List of column names to be converted to string.

    Returns:
    pandas.DataFrame: The DataFrame with specified columns converted to string.
    """
    df[cols_to_str] = df[cols_to_str].astype(str)
    return df

def cast_col_to_datetime(df, datetime_col='date_time'):
    """
    Convert a specified column in a DataFrame to datetime type.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the column.
    col (str): The name of the column to be converted to datetime. Defaults to 'date_time'.

    Returns:
    pandas.DataFrame: The DataFrame with the specified column converted to datetime.
    """
    df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')
    return df

def cast_cols_values_to_list(df, cols_to_list):
    """
    Convert the string representation of list-like values in specified columns
    of a DataFrame into actual lists using ast.literal_eval for safe evaluation.

    This function is useful for columns that contain string representations
    of list-like structures (e.g., "[1, 2, 3]").

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the columns.
    cols_to_list (list of str): List of column names whose string-represented list values
                                are to be converted to actual lists.

    Returns:
    pandas.DataFrame: The DataFrame with the values of specified columns converted to lists.
    """
    for col in cols_to_list:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    return df

def perform_data_casting(df,
                         cols_to_str=['title', 'company_name', 'location', 'via', 'description', 'extensions', 'job_id', 'schedule_type', 'posted_at', 'search_query'],
                         datetime_col='date_time',
                         cols_to_list=['extensions']):
    """
    Perform a series of data casting operations on a pandas DataFrame including
    casting columns to string, converting a column to datetime,
    and converting string-represented lists into actual lists.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be processed.
    cols_to_str (list of str, optional): Columns to cast to string type.
    datetime_col (str, optional): Column to convert to datetime type.
    cols_to_list (list of str, optional): Columns with string-represented list values to convert to actual lists.

    Returns:
    pandas.DataFrame: The processed DataFrame with specified casting operations applied.
    """
    if cols_to_str:
        df = cast_cols_to_str(df, cols_to_str)
    if datetime_col:
        df = cast_col_to_datetime(df, datetime_col)
    if cols_to_list:
        df = cast_cols_values_to_list(df, cols_to_list)

    return df
