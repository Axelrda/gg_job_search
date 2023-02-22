def get_salary_col(df):
    
    # Extract salary from extensions col
    df['salary'] = pd.Series(df.extensions.str.split(', ', expand=True)[1])
       
    # Replace non-salary values to np.NaN
    df['salary'].replace(["'à plein temps']", "'à temps partiel']", "'stage']", "'prestataire']"], np.NaN, inplace=True)
    
    # Convert null values to Nothing_found to make parsing easier
    df.at[df.salary.isnull(), 'salary'] = "nothing_found"
    
    return df


def get_og_salary_currency(df):
    
    df['og_salary_currency'] = df.salary.str.extract(r'(\€|\$us)', flags=re.IGNORECASE)
    
    return df


def get_og_salary_period(df):
    
    df['og_salary_period'] = df.salary.str.extract(r'(\ban\b|\bmois\b|\bjour\b)', flags=re.IGNORECASE)
    
    return df
    

def clean_salary(df):
    
    
        ####### targeted clean for easier parsing #######

        for index, salary_str in enumerate(df.salary):
                
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

                    df.at[index, 'salary'] = salary_str
                    
        return df

def get_salary_range_and_mean(df):                    
                 
                                        
        for index, row in df.iterrows():
    
            # extract boundaries of YEAR salaries given as a range + calculate mean salary
            if (row['og_salary_period'] == 'an') and 'à' in row['salary']:

                # remove k 
                row['salary'] = row['salary'].replace('k', '000')

                # get upper and lower bounds
                lower_bound = float(row.salary.split(' à ')[0].split(',')[0])
                upper_bound = float(row.salary.split(' à ')[1].split(',')[0])

                # re-establish a consistent value regarding to common year salaries
                if lower_bound < 1000:
                    lower_bound = lower_bound * 1000

                if upper_bound < 1000:
                    upper_bound = upper_bound * 1000
                
                # get upper / lower bound and discrete_salary columns
                df.at[index, 'lower_bound'] = lower_bound
                df.at[index, 'upper_bound'] = upper_bound
                df.at[index, 'discrete_salary'] = np.mean([lower_bound, upper_bound])
                
                
                
            

            # extract discrete YEAR salaries        
            elif (row['og_salary_period'] == 'an') and 'à' not in row['salary']:

                # remove k
                row['salary'] = row['salary'].replace('k', '000')
                row['salary'] = row['salary'].replace(',', '.')

                # convert value to float
                row['salary'] = float(row['salary'])

                # re-establish a consistent value regarding to common year salaries
                if row['salary'] < 1000:
                    row['salary'] = row['salary'] * 1000

                # assign result to discrete salary column
                df.at[index, 'discrete_salary'] = row['salary']

                

            
            # extract boundaries of MONTH salaries given as a range + calculate mean salary   
            elif (row['og_salary_period'] == 'mois') and 'à' in row['salary']:

                # remove k and replace commas
                row['salary'] = row['salary'].replace('k', '00')
                row['salary'] = row['salary'].replace(',', '.')

                # get upper and lower bounds
                lower_bound = float(row.salary.split(' à ')[0])
                upper_bound = float(row.salary.split(' à ')[1])

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
            elif (row['og_salary_period'] == 'mois') and 'à' not in row['salary']:

                # remove k and replace commas
                row['salary'] = row['salary'].replace('k', '00')
                row['salary'] = row['salary'].replace(',', '.')

                # convert value to float
                row['salary'] = float(row['salary'])


                # re-establish a consistent value regarding to common year salaries
                if row['salary'] < 1000:
                    row['salary'] = row['salary'] * 1000

                # assign result to discrete salary column
                df.at[index, 'discrete_salary'] = row['salary']                 
            
            
            
            
            # extract boundaries of DAY salaries given as a range + calculate mean salary   
            elif (row['og_salary_period'] == 'jour') and 'à' in row['salary']:
                
                # get upper and lower bounds
                lower_bound = float(row.salary.split(' à ')[0])
                upper_bound = float(row.salary.split(' à ')[1])

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
    
def salary_prepro(df):
    
    df = get_salary_col(df)
    df = get_og_salary_period(df)
    df = get_og_salary_currency(df)
    df = clean_salary(df)
    df = get_salary_range_and_mean(df)
    df = convert_salary_period(df)
    df = convert_salary_currency(df)
    
    return df