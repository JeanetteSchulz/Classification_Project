import pandas as pd
import numpy as np
import os
from env import host, user, password
from sklearn.model_selection import train_test_split



"""
This file is for the Codeup example dataframes used in the SQL database. This file saves functions
to be resued as necessary, so that this code does not need to be copied or rewritten. These
functions read the Titanic, Iris, and Telco data sets from the Codeup database. These functions indivdually read the 
databases into a variable, and then clean and split them. Each function works only for it's individually named dataset 
and can NOT be interchanged, since the cleaning process for each is unquie to the individual database.
"""


###################### Connect to the Codeup SQL Server ######################

def get_connection(database_name):
    '''
    This function takes in as arguments the database, username, host, and password for 
    the mysql database and returns a string that can be used to open a connection to the server
    and query the db in the read_sql function. 
    '''
    return f'mysql+pymysql://{user}:{password}@{host}/{database_name}'


############################ Acquire the Telco Data ##########################

def get_telco_data():
    '''
    This function reads the Telco data from the Codeup SQL database, writes data to
    a csv file if a local file does not exist, and returns a dataframe.
    '''
    if os.path.isfile('telco.csv'):
        # If csv file exists read in data from csv file.
        df = pd.read_csv('telco.csv', index_col=0)
        
    else:
        
        # Read fresh data from db into a DataFrame
        df =  pd.read_sql("""SELECT * FROM customers 
                            JOIN contract_types USING(contract_type_id) 
                            JOIN internet_service_types USING(internet_service_type_id) 
                            JOIN payment_types USING(payment_type_id)""", 
                            get_connection('telco_churn')
                        )
        
        # Cache data
        df.to_csv('telco.csv')
        
    return df


###################### Clean and Split the Telco Data ######################

def prep_telco(telco):
    """
    This function starts by changing total_charges from a string to a float. It then drops any duplicate information, and creates
    dummy variables for all of the categorical columns. The dummy variables are then concatinated to the base dataframe, which is 
    then put through an extensive list of renaming most of the columns for easier manipulation. The data is then split and returned 
    as three separate dataframes: 20% Test data, 24% Validation data, 56% Training data. 
    """
    # Some total_charges are blank. I'm going to convert those to zero for now, or I won't be able to 
    # change the dtype of total_charges
    telco = telco.assign(total_charges = telco.total_charges.replace(" ", "0.00"))

    # Total_Charges is currently a string, I want it to be a Float for future math
    telco["total_charges"]= telco["total_charges"].str.strip().replace(",","").replace("$","").astype(float)
    
    # Always drop them duplicates (if any)
    telco = telco.drop_duplicates()

    # Time to make a LOT of dummies for all the categorical columns
    telco_dummy1 = pd.get_dummies(
                                telco[[ 'gender', 
                                        'partner', 
                                        'dependents', 
                                        'phone_service', 
                                        'paperless_billing',
                                        'churn',
                                        'multiple_lines', 
                                        'online_security', 
                                        'online_backup', 
                                        'device_protection', 
                                        'tech_support',
                                        'streaming_tv']], 
                                        dummy_na= False, drop_first= True
                                )

    # Some of the categories had more than 2 options, so this separate dummy list will not drop any options
    telco_dummy2 = pd.get_dummies(
                                telco[[ 
                                        'internet_service_type',
                                        'payment_type',
                                        'contract_type']], 
                                        dummy_na= False
                                )
    # Now to concatenate my dummy dataframes to my telco dataframe
    telco = pd.concat([telco, telco_dummy1, telco_dummy2], axis=1)
    telco.head()

    # I want all my data represented as numbers so that it's easier to do statistics and modeling on them.
    telco = telco.drop(['payment_type_id', 
                        'internet_service_type_id', 
                        'contract_type_id', # a repeat of contract_type, which was turned into a dummy variable
                        'customer_id', 
                        'gender', 
                        'partner', 
                        'dependents', 
                        'phone_service', 
                        'multiple_lines', 
                        'online_security', 
                        'online_backup', 
                        'device_protection', 
                        'tech_support', 
                        'streaming_tv', 
                        'streaming_movies', 
                        'paperless_billing', 
                        'churn', 
                        'internet_service_type', 
                        'payment_type', 
                        'contract_type'], 1)


    # A lot of the dummy variables have spaces in them. I'm going to rename them so they are easier to manipulate:
    telco = telco.rename(columns={"gender_Male": "is_male"})
    telco = telco.rename(columns={"partner_Yes": "has_partner"})
    telco = telco.rename(columns={"dependents_Yes": "has_dependent"})
    telco = telco.rename(columns={"phone_service_Yes": "has_phone_service"})
    telco = telco.rename(columns={"paperless_billing_Yes": "has_paperless_billing"})
    telco = telco.rename(columns={"churn_Yes": "has_churned"})
    telco = telco.rename(columns={"contract_type_One year": "one_year_contract"})
    telco = telco.rename(columns={"contract_type_Two year": "two_year_contract"})
    telco = telco.rename(columns={"multiple_lines_Yes": "has_multiple_lines"})
    telco = telco.rename(columns={"multiple_lines_No phone service": "multiple_lines_no_phone_service"})
    telco = telco.rename(columns={"online_security_No internet service": "online_security_no_internet_service"})
    telco = telco.rename(columns={"online_security_Yes": "has_online_security"})
    telco = telco.rename(columns={"online_backup_No internet service": "online_backup_no_internet_service"})
    telco = telco.rename(columns={"online_backup_Yes": "has_online_backup"})
    telco = telco.rename(columns={"device_protection_No internet service": "device_protection_no_internet_service"})
    telco = telco.rename(columns={"device_protection_Yes": "has_device_protection"})
    telco = telco.rename(columns={"tech_support_No internet service": "tech_support_no_internet_service"})
    telco = telco.rename(columns={"tech_support_Yes": "has_tech_support"})
    telco = telco.rename(columns={"streaming_tv_No internet service": "streaming_tv_no_internet_service"})
    telco = telco.rename(columns={"streaming_tv_Yes": "has_streaming_tv"})
    telco = telco.rename(columns={"internet_service_type_Fiber optic": "internet_service_type_fiber_optic"})
    telco = telco.rename(columns={"payment_type_Bank transfer (automatic)": "payment_type_bank_transfer_A"})
    telco = telco.rename(columns={"payment_type_Credit card (automatic)": "payment_type_credit_card_A"})
    telco = telco.rename(columns={"payment_type_Electronic check": "payment_type_electronic_check_M"})
    telco = telco.rename(columns={"payment_type_Mailed check": "payment_type_mailed_check_M"})
    telco = telco.rename(columns={"contract_type_Month-to-month": "month_to_month_contract"})

    # Splitting the data for testing!
    train, test = train_test_split(telco, test_size = .2, random_state=22, stratify= telco.has_churned)
    train, validate = train_test_split(train, test_size=.3, random_state=22, stratify= train.has_churned)
    return train, validate, test
