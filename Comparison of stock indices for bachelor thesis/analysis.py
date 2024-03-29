import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

BASE_DIR = os.path.dirname(__file__)

TRANSLATE_MONTH = {"January":"Styczeń",
                  "February":"Luty",
                  "March":"Marzec",
                  "April":"Kwiecień",
                  "May":"Maj",
                  "June":"Czerwiec",
                  "July":"Lipiec",
                  "August":"Sierpień",
                  "September":"Wrzesień",
                  "October":"Październik",
                  "November":"Listopad",
                  "December":"Grudzień"}

def clean_data(path):
    """
    Loads the data from a CSV file into a pandas dataframe. Converts the 'Data' column to datetime format and the 'Ostatnio' column to float format.
    Parameters:
    - path: The path to the CSV file.
        """
    df = pd.read_csv(path, delimiter=',')
    df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y')
    df['Ostatnio'] = df['Ostatnio'].str.replace(".","").str.replace(",",".").astype(float)
    return df

def prepare_data():
    """
    Merges dataframes for WIG20, DAX, and NASDAQ indices, selecting only the 'Data' and 'Ostatnio' columns. 
    Renames columns and returns the merged dataframe.
    Returns merged dataframe containing data for WIG20, DAX, and NASDAQ indices.
    """
    wig20_df = clean_data(rf"{BASE_DIR}\Dane\Dane historyczne dla WIG20.csv")
    dax_df = clean_data(rf"{BASE_DIR}\Dane\Dane historyczne dla DAX.csv")
    nasdaq_df = clean_data(rf"{BASE_DIR}\Dane\Dane historyczne dla NASDAQ Composite.csv")
    merged_df = (
        wig20_df[['Data', 'Ostatnio']]
        .merge(dax_df[['Data', 'Ostatnio']], on='Data')
        .merge(nasdaq_df[['Data', 'Ostatnio']], on='Data')
)
    merged_df.columns = ['Data', 'WIG20', 'DAX', 'NASDAQ']
    return merged_df
    
def create_correlation_matrix(df):
    """ 
    Creates and displays a heatmap of the correlation matrix for WIG20, DAX, and NASDAQ indices.
    Parameters:
    - df: Dataframe containing data for WIG20, DAX, and NASDAQ indices.
    """
    correlation_matrix = df[['WIG20', 'DAX', 'NASDAQ']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', square=True)
    plt.title('Macierz korelacji indeksów giełdowych')
    plt.show()
    
def create_monthly_changes_plot(df):
    """ 
    Creates and displays a table showing the monthly percentage changes for WIG20, DAX, and NASDAQ indices.
    Parameters:
    - df: Dataframe containing data for WIG20, DAX, and NASDAQ indices.
    """
    data_df = df.set_index('Data')
    monthly_df = data_df.resample('M').last()
    monthly_changes = monthly_df.pct_change()
    monthly_changes.dropna(how = "all", inplace=True)
    monthly_changes['Miesiąc'] = monthly_changes.index.strftime('%B %Y')
    monthly_changes['Miesiąc'] = monthly_changes['Miesiąc'].apply(lambda x: x.split()[0]).map(TRANSLATE_MONTH) + " " + monthly_changes.index.year.astype(str)
    monthly_changes.reset_index(inplace=True)
    monthly_changes = monthly_changes[['Miesiąc', 'WIG20', 'DAX', 'NASDAQ']]

    fig, ax = plt.subplots(figsize=(6, 10))
    ax.axis('off')
    table_data = monthly_changes.applymap(lambda x: f'{x:.2%}' if not isinstance(x, str) else x)
    col_labels = table_data.columns.tolist()

    table = ax.table(cellText=table_data.values,
                    colLabels=col_labels,
                    cellLoc='center',
                    loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax.set_title('Miesięczne zmiany procentowe')
    plt.show()
    
def create_weekly_changes_plot(df):
    """ 
    Creates and displays a table showing the weekly percentage changes for WIG20, DAX, and NASDAQ indices.
    Parameters:
    - df: Dataframe containing data for WIG20, DAX, and NASDAQ indices.
    """
    weekly_changes = df.set_index('Data').resample('W').mean().pct_change()
    weekly_changes.dropna(how = 'all',inplace=True)
    weekly_changes['Numer Tygodnia'] = weekly_changes.index.week
    weekly_changes['Numer Tygodnia'] = weekly_changes['Numer Tygodnia'].map(lambda x: f'Tydzień {x}')
    weekly_changes = weekly_changes[['Numer Tygodnia', 'WIG20', 'DAX', 'NASDAQ']]

    fig, ax = plt.subplots(figsize=(6, 10))
    ax.axis('off')

    table_data = weekly_changes.applymap(lambda x: f'{x:.2%}' if not isinstance(x, str) else x)
    col_labels = table_data.columns.tolist()

    table = ax.table(cellText=table_data.values,
                    colLabels=col_labels,
                    cellLoc='center',
                    loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax.set_title('Tygodniowe zmiany procentowe')
    plt.show()
    
def covid_analysis(df):
    """ 
    Analyzes the performance of WIG20, DAX, and NASDAQ indices during the COVID-19 selected period. 
    Plots the closing prices and generates correlation matrices, monthly, and weekly percentage change tables.
    Parameters:
    - df: Dataframe containing data for WIG20, DAX, and NASDAQ indices.
    """
    first_day = "2020-01-01"
    last_day = "2020-04-30"
    filtered_df = df[(df['Data']>=first_day) & (df['Data']<= last_day)]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    wig20, = ax1.plot(filtered_df['Data'], filtered_df['WIG20'], label='WIG20', color='blue')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('WIG20 cena zamknięcia', color='black')
    ax2 = ax1.twinx()
    dax, = ax2.plot(filtered_df['Data'], filtered_df['DAX'], label='DAX', color='red')
    NASDAQ, = ax2.plot(filtered_df['Data'], filtered_df['NASDAQ'], label='NASDAQ', color='green')
    ax2.set_ylabel('DAX & NASDAQ cena zamknięcia', color='black')
    lines = [wig20, dax, NASDAQ]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    plt.title('Porównanie Cen Indeksów Giełdowych')
    plt.show()
    create_correlation_matrix(filtered_df)
    create_monthly_changes_plot(filtered_df)
    create_weekly_changes_plot(filtered_df)
    
def ru_ua_analysis(df):
    """ 
    Analyzes the performance of WIG20, DAX, and NASDAQ indices during a specified period of Russian invasion on Ukraine.
    Plots the closing prices and generates correlation matrices, monthly, and weekly percentage change tables.
    Parameters:
    - df: Dataframe containing data for WIG20, DAX, and NASDAQ indices.
    """
    first_day = "2022-01-01"
    last_day = "2022-04-30"
    filtered_df = df[(df['Data']>=first_day) & (df['Data']<= last_day)]
    fig, ax1 = plt.subplots(figsize=(10, 6))

    wig20, = ax1.plot(filtered_df['Data'], filtered_df['WIG20'], label='WIG20', color='blue')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('WIG20 cena zamknięcia', color='black')

    ax2 = ax1.twinx()

    dax, = ax2.plot(filtered_df['Data'], filtered_df['DAX'], label='DAX', color='red')
    NASDAQ, = ax2.plot(filtered_df['Data'], filtered_df['NASDAQ'], label='NASDAQ', color='green')
    ax2.set_ylabel('DAX & NASDAQ cena zamknięcia', color='black')

    lines = [wig20, dax, NASDAQ]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    plt.title('Porównanie Cen Indeksów Giełdowych')
    plt.show()

    create_correlation_matrix(filtered_df)
    create_monthly_changes_plot(filtered_df)
    create_weekly_changes_plot(filtered_df)
    
def bank_crysis_analysis(df):
    """ 
    Analyzes the performance of WIG20, DAX, and NASDAQ indices during the selected period of 2008 financial crisis.
    Plots the closing prices and generates correlation matrices, monthly, and weekly percentage change tables.
    """
    first_day = "2008-06-01"
    last_day = "2008-12-31"
    filtered_df = df[(df['Data']>=first_day) & (df['Data']<= last_day)]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    wig20, = ax1.plot(filtered_df['Data'], filtered_df['WIG20'], label='WIG20', color='blue')
    NASDAQ, = ax1.plot(filtered_df['Data'], filtered_df['NASDAQ'], label='NASDAQ', color='green')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('WIG20 & NASDAQ cena zamknięcia', color='black')
    ax2 = ax1.twinx()
    dax, = ax2.plot(filtered_df['Data'], filtered_df['DAX'], label='DAX', color='red')
    ax2.set_ylabel('DAX cena zamknięcia', color='black')
    lines = [wig20, dax, NASDAQ]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    plt.title('Porównanie Cen Indeksów Giełdowych')
    plt.show()
    
    create_correlation_matrix(filtered_df)
    create_monthly_changes_plot(filtered_df)
    create_weekly_changes_plot(filtered_df)

def main():
    final_df = prepare_data()
    covid_analysis(final_df)
    ru_ua_analysis(final_df)
    bank_crysis_analysis(final_df)

main()