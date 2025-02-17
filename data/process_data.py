import sys
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    """
    To Load Data
    
    Parameters:
    messages_filepath - filepath to messages data
    categories_filepath  - filepath to categories data
    
    Returns:
    Combined Dataframe with messages and categories
    
    """
    messages = pd.read_csv(messages_filepath)
    messages.drop_duplicates(subset=['id'],inplace = True)
    
    categories = pd.read_csv(categories_filepath)
    categories.drop_duplicates(subset=['id'],inplace = True)

    df = messages.merge(categories,on='id',how="left")
    return df
    
def clean_data(df):
    """
    Function to clean the data
    
    Parameters:
    df - Dataframe to be cleaned
    
    Returns:
    df - cleaned df
    """
    categories = df['categories'].str.split(';',expand=True)
    row = categories.iloc[0]
    category_colnames = row.apply(lambda x: x.split('-')[0])
    categories.columns = category_colnames
    for column in categories:
        categories[column] = categories[column].apply(lambda x: (x.split('-')[1]) )
        categories[column] = categories[column].astype('int32')
    df = df.drop('categories',axis = 1)
    df = pd.concat([df,categories],axis=1)
    df = df[df['related'] != 2]
    
    return df
    
def save_data(df, database_filename):
    """
    To save data to a SQL database
    
    Parameters:
    df - dataframe to be stored in database
    database_filename - Name of the database
    
    """
    engine = create_engine('sqlite:///'+database_filename)
    df.to_sql('Dataset', engine, index=False,if_exists='replace')


def main():
    """
    Main Function to clean the data for training and load it into a SQL Database
    """
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()