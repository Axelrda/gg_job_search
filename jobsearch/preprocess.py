import pandas as pd
import numpy as np
import unicodedata
import re
import requests


def get_salary_currency(salaries):

  cond_period = [

    salaries.str.contains(r'\€|eur|euro|euros'),
    salaries.str.contains(r'\$us|\$'),
    salaries.str.contains(r'\£'),

  ]

  choices_period = [

    'euros',
    'us dollars',
    'sterling pounds'

  ]

  salary_currency = pd.Series(np.select(cond_period, choices_period, default=np.NaN))

  return salary_currency


def get_salary_period(salaries):

  cond_period = [

    salaries.str.contains(r'an|year'),
    salaries.str.contains(r'mois'),
    salaries.str.contains(r'par semaine'),
    salaries.str.contains(r'jour|tjm|per day'),
    salaries.str.contains(r'heure|par h|/h\b')

  ]

  choices_period = [

    'an',
    'mois',
    'semaine',
    'jour',
    'heure',

  ]

  salary_period = pd.Series(np.select(cond_period, choices_period, default=np.NaN))

  return salary_period



def get_salary_status(salaries):

  cond_status = [

     salaries.str.contains(r'net'),
     salaries.str.contains(r'brut'),

  ]

  choices_status = [

    'net',
    'brut'

  ]

  salary_status = pd.Series(np.select(cond_status, choices_status, default='brut'))

  return salary_status



def rm_non_digits(x):

    if x is None:
        return None
    if isinstance(x, str):
        x = ''.join([c for c in x if c is not None and (c.isdigit() or c == '.')])
        if len(x) == 0:
            return None
        else:
            return float(x)
    else:
        return None


def clean_salary(df):


        ####### targeted clean for easier parsing #######

        for index, salary_str in enumerate(df.extracted_salary):

                if 'nothing_found' not in salary_str:

                    # split salary period from rest of string
                    salary_str =  salary_str.split(' par')[0]

                    # remove single quote
                    salary_str = salary_str.split("'")[1]

                    # remove unicode chars
                    salary_str = salary_str.replace("\\xa0", "")
                    salary_str = salary_str.replace("\\u202f", "")

                    #remove currency
                    salary_str = salary_str.replace("€", "")
                    salary_str = salary_str.replace("$us", "")

                    df.at[index, 'extracted_salary'] = salary_str

        return df

def get_salary_range_and_mean(df):


        for index, row in df.iterrows():

            # extract boundaries of YEAR salaries given as a range + calculate mean salary
            if (row['og_salary_period'] == 'an') and 'à' in row['extracted_salary']:

                # remove k
                row['extracted_salary'] = row['extracted_salary'].replace('k', '000')

                # get upper and lower bounds
                lower_bound = float(row.extracted_salary.split(' à ')[0].split(',')[0])
                upper_bound = float(row.extracted_salary.split(' à ')[1].split(',')[0])

                # re-establish a consistent value regarding to common year salaries
                if lower_bound < 200:
                    lower_bound = lower_bound * 1000

                if upper_bound < 200:
                    upper_bound = upper_bound * 100

                # get upper / lower bound and discrete_salary columns
                df.at[index, 'lower_bound'] = lower_bound
                df.at[index, 'upper_bound'] = upper_bound
                df.at[index, 'discrete_salary'] = np.mean([lower_bound, upper_bound])





            # extract discrete YEAR salaries
            elif (row['og_salary_period'] == 'an') and 'à' not in row['extracted_salary']:

                # remove k
                row['extracted_salary'] = row['extracted_salary'].replace('k', '000')
                row['extracted_salary'] = row['extracted_salary'].replace(',', '.')

                # convert value to float
                row['extracted_salary'] = float(row['extracted_salary'])

                # re-establish a consistent value regarding to common year salaries
                if row['extracted_salary'] < 1000:
                    row['extracted_salary'] = row['extracted_salary'] * 1000

                # assign result to discrete salary column
                df.at[index, 'discrete_salary'] = row['extracted_salary']




            # extract boundaries of MONTH salaries given as a range + calculate mean salary
            elif (row['og_salary_period'] == 'mois') and 'à' in row['extracted_salary']:

                # remove k and replace commas
                row['extracted_salary'] = row['extracted_salary'].replace('k', '00')
                row['extracted_salary'] = row['extracted_salary'].replace(',', '.')

                # get upper and lower bounds
                lower_bound = float(row.extracted_salary.split(' à ')[0])
                upper_bound = float(row.extracted_salary.split(' à ')[1])

                # re-establish a consistent value regarding to common month salaries
                if lower_bound < 10:
                    lower_bound = lower_bound * 100

                if lower_bound < 1000:
                    lower_bound = lower_bound * 10

                if upper_bound < 10:
                    upper_bound = upper_bound * 100

                if upper_bound < 1000:
                    upper_bound = upper_bound * 10

                # get upper / lower bound and discrete_salary columns
                df.at[index, 'lower_bound'] = lower_bound
                df.at[index, 'upper_bound'] = upper_bound
                df.at[index, 'discrete_salary'] = np.mean([lower_bound, upper_bound])




            # extract discrete MONTH salaries
            elif (row['og_salary_period'] == 'mois') and 'à' not in row['extracted_salary']:

                # remove k and replace commas
                row['extracted_salary'] = row['extracted_salary'].replace('k', '00')
                row['extracted_salary'] = row['extracted_salary'].replace(',', '.')

                # convert value to float
                row['extracted_salary'] = float(row['extracted_salary'])


                # re-establish a consistent value regarding to common year salaries
                if row['extracted_salary'] < 1000 and type(row['employment_type']) == str and row['employment_type'] not in ['internship', 'apprenticeship']:
                    row['extracted_salary'] = row['extracted_salary'] * 1000

                elif row['extracted_salary'] < 100:
                    row['extracted_salary'] = row['extracted_salary'] * 1000

                elif row['extracted_salary'] < 1000 and type(row['employment_type']) == str and row['employment_type'] in ['internship', 'apprenticeship']:
                    row['extracted_salary'] = row['extracted_salary']

                # assign result to discrete salary column
                df.at[index, 'discrete_salary'] = row['extracted_salary']

            # extract boundaries of DAY salaries given as a range + calculate mean salary
            elif (row['og_salary_period'] == 'jour') and 'à' in row['extracted_salary']:

                # get upper and lower bounds
                lower_bound = float(row.extracted_salary.split(' à ')[0])
                upper_bound = float(row.extracted_salary.split(' à ')[1])

                # get upper / lower bound and discrete_salary columns
                df.at[index, 'lower_bound'] = lower_bound
                df.at[index, 'upper_bound'] = upper_bound
                df.at[index, 'discrete_salary'] = np.mean([lower_bound, upper_bound])


        return df


 # Define a global variable to cache the exchange rate value
cached_exchange_rate = None

# Define a function to get the exchange rate value
def get_exchange_rate():
    # Declare the variable as global to modify its value in the function
    global cached_exchange_rate

    try:
        # Send a network request to get the exchange rate
        response = requests.get('https://openexchangerates.org/api/latest.json?app_id=4820391575d04bdd8d07b7e15fb0a463')
        response.raise_for_status()

        # Parse the response and calculate the exchange rate
        data = response.json()
        exchange_rate = data['rates']['EUR'] / data['rates']['USD']

        # Cache the exchange rate value
        cached_exchange_rate = exchange_rate

    except (requests.exceptions.RequestException, json.decoder.JSONDecodeError) as e:
        # Handle any exceptions that occur during the API request
        # If the API request fails, use the cached exchange rate value if it exists
        if cached_exchange_rate is not None:
            exchange_rate = cached_exchange_rate
        else:
            # If there is no cached exchange rate value, raise the original exception
            raise e

    return exchange_rate

# This function converts salary values in US dollars to euro currency
def convert_salary_currency(df):

    # Create a boolean mask to select rows where salary is in US dollars
    mask = df['og_salary_currency'] == '$us'

    # Multiply the 'discrete_salary' column by the exchange rate
    df.loc[mask,'discrete_salary'] *= get_exchange_rate()

    # Return the modified dataframe
    return df


# This function converts salary values from their original period to yearly, monthly, and daily rates
def convert_salary_period(df):

    # Define constants used in the conversion calculations
    n_days_per_year = 250
    n_days_per_month = 20

    # Create a boolean mask to select rows where salary is reported annually
    mask = df['og_salary_period'] == 'an'

    # Convert the 'discrete_salary' values in the selected rows to yearly, monthly, and daily rates
    df.loc[mask, 'year_salary'] = df.loc[mask,'discrete_salary']
    df.loc[mask, 'month_salary'] = df.loc[mask,'discrete_salary'] / 12
    df.loc[mask, 'day_salary'] = df.loc[mask,'discrete_salary'] / n_days_per_year

    # Create a boolean mask to select rows where salary is reported monthly
    mask = df['og_salary_period'] == 'mois'

    # Convert the 'discrete_salary' values in the selected rows to yearly, monthly, and daily rates
    df.loc[mask, 'year_salary'] = df.loc[mask,'discrete_salary'] * 12
    df.loc[mask, 'month_salary'] = df.loc[mask,'discrete_salary']
    df.loc[mask, 'day_salary'] = df.loc[mask,'discrete_salary'] / n_days_per_month

    # Create a boolean mask to select rows where salary is reported daily
    mask = df['og_salary_period'] == 'jour'

    # Convert the 'discrete_salary' values in the selected rows to yearly, monthly, and daily rates
    df.loc[mask, 'year_salary'] = df.loc[mask,'discrete_salary'] * n_days_per_year
    df.loc[mask, 'month_salary'] = df.loc[mask,'discrete_salary'] * n_days_per_month
    df.loc[mask, 'day_salary'] = df.loc[mask,'discrete_salary']

    # Return the modified dataframe
    return df

def processing_extensions_salaries(df):

    df = get_salary_col(df)
    df = get_og_salary_period(df)
    df = get_og_salary_currency(df)
    df = clean_salary(df)
    df = get_salary_range_and_mean(df)
    df = convert_salary_period(df)
    df = convert_salary_currency(df)

    return df


def lowercase_and_remove_accents(df):

  # lowering cases
  df = df.applymap(lambda x: x.lower() if type(x) == str else x )

  # removing accents
  def remove_accents(text):
      normalized = unicodedata.normalize('NFKD', text)
      without_accents = [c for c in normalized if not unicodedata.combining(c)]
      return ''.join(without_accents)

  df = df.applymap(lambda x: remove_accents(x) if isinstance(x, str) else x)

  return df


def basic_cleaning(df):

  #fill null values
  df.fillna('na', inplace=True)

  # removing duplicated records
  df.drop_duplicates(['description'], inplace=True)

  # reset index
  df = df.reset_index(drop=True)

  return df


def matching_cols(df):

  # define mismatch value masks
  mismatch_postedat = df.posted_at.str.slice(0,6) != "il y a"
  mismatch_jobid = df.job_id.str.slice(0,6) != "eyjqb2"
  mismatch_extensions = df.extensions.str.slice(0,2) != "['"
  mismatch_schedule = (df.schedule_type != "a plein temps") & (df.schedule_type != "stage") & (df.schedule_type != "prestataire") & (df.schedule_type != "a temps partiel")
  mismatch_datetime = df.date_time.str.slice(0,2) != "20"

  # shift every column from 1 position starting at thumbnail col
  matched_df = df[mismatch_datetime & mismatch_schedule & mismatch_extensions & mismatch_jobid & mismatch_postedat].iloc[:,-7:].shift(axis=1, periods=1).fillna('na')

  # replace og data w/ shifted values
  df.loc[mismatch_datetime & mismatch_schedule & mismatch_extensions & mismatch_jobid & mismatch_postedat, df.columns[-7:]] = matched_df.copy().values

  # replace og data w/ shifted values
  df.loc[mismatch_datetime & mismatch_schedule & mismatch_extensions & mismatch_jobid & mismatch_postedat, df.columns[-7:]] = matched_df.copy().values


  mismatch_thumbnail = df.loc[df['job_id'].str.startswith(('https:')), df.columns[7:-4]].shift(axis=1, periods=1)

  mismatch_thumbnail['thumbnail'] = df.loc[df['job_id'].str.startswith(('https:')), 'job_id']

  df.loc[df['job_id'].str.startswith(('https:')), df.columns[7:-4]] = mismatch_thumbnail.copy().values


  # get location col values in job_id col + shift dataframe
  mismatch_cities = df.loc[~df['job_id'].str.startswith(('eyjqb2', 'il y a', 'https:', 'na'))].loc[:, 'location': 'job_id'].shift(axis=1, periods=1)

  # assign these values to location col
  mismatch_cities['location'] = df.loc[~df['job_id'].str.startswith(('eyjqb2', 'il y a', 'https:', 'na')), 'job_id']

  # replace og data w/ newly arranged values
  df.loc[~df['job_id'].str.startswith(('eyjqb2', 'il y a', 'https:', 'na')), df.columns[2:-4]] = mismatch_cities.copy().values


  extensions_in_thumbnail = df[df.thumbnail.str.slice(0,6) == "['il y"].loc[:, 'thumbnail': 'job_id'].shift(axis=1, periods=1).fillna('na')

  df.loc[df.thumbnail.str.slice(0,6) == "['il y", df.columns[7:-4]] = extensions_in_thumbnail.copy().values


  mismatch_postedat = df.loc[~df.posted_at.str.startswith(('il y a', 'na'))][['posted_at', 'schedule_type']]

  mismatch_postedat['posted_at'], mismatch_postedat['schedule_type'] = mismatch_postedat['schedule_type'], mismatch_postedat['posted_at']

  df.loc[~df.posted_at.str.startswith(('il y a', 'na')), df.columns[-4:-2]] = mismatch_postedat.copy().values

  return df



def basic_prepro(df):

  df = lowercase_and_remove_accents(df)
  df = basic_cleaning(df)
  df = matching_cols(df)

  return df


def get_last_records(df):
    """
    Returns the last records from a DataFrame based on the date_time column.

    Args:
        df (pandas.DataFrame): The DataFrame to extract the last records from.

    Returns:
        pandas.DataFrame: The last records from the DataFrame.
    """
    # Select the records where the date_time is equal to the maximum date_time value
    last_data = df[pd.to_datetime(df.date_time).dt.date == pd.to_datetime(df.date_time).dt.date.max()]

    return last_data


def get_lang_records(df, language):
    """
    Returns the records from a DataFrame that match a specific language.

    Args:
        df (pandas.DataFrame): The DataFrame to filter.
        language (str): The language to filter by.

    Returns:
        pandas.DataFrame: The filtered DataFrame containing only the records with the specified language.
    """
    # Filter the DataFrame based on the lang_labels column
    filtered_df = df[df['lang_labels'] == language]

    return filtered_df
