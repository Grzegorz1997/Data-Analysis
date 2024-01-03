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
    """  Load the data from CSV files into pandas dataframes.
        Converts the date column to datetime format and
        the numeric columns to float format."""
        
    df = pd.read_csv(path, delimiter=',')
    df['Data'] = pd.to_datetime(df['Data'], format='%d.%m.%Y')
    df['Ostatnio'] = df['Ostatnio'].str.replace(".","").str.replace(",",".").astype(float)
    return df

def prepare_data():
    """merges dataframes"""
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
    
def covid_analysis(df):
    """Filter merged dataframe by analysed period"""
    first_day = "2020-01-01"
    last_day = "2020-04-30"

    merged_df = df[(df['Data']>=first_day) & (df['Data']<= last_day)]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    wig20, = ax1.plot(merged_df['Data'], merged_df['WIG20'], label='WIG20', color='blue')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('WIG20 cena zamknięcia', color='black')
    ax2 = ax1.twinx()
    dax, = ax2.plot(merged_df['Data'], merged_df['DAX'], label='DAX', color='red')
    NASDAQ, = ax2.plot(merged_df['Data'], merged_df['NASDAQ'], label='NASDAQ', color='green')
    ax2.set_ylabel('DAX & NASDAQ cena zamknięcia', color='black')
    lines = [wig20, dax, NASDAQ]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    plt.title('Porównanie Cen Indeksów Giełdowych')
    plt.show()

    correlation_matrix = merged_df[['WIG20', 'DAX', 'NASDAQ']].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', square=True)
    plt.title('Macierz korelacji indeksów giełdowych')
    plt.show()

    merged_df.set_index('Data', inplace=True)

    monthly_df = merged_df.resample('M').last()
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
    ax.set_title('Miesięczne zmiany procentowe',y=0.57)
    plt.show()
    

    merged_df.reset_index(inplace=True)
    weekly_changes = merged_df.set_index('Data').resample('W').mean().pct_change()
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
    ax.set_title('Tygodniowe zmiany procentowe',y=0.8)
    plt.show()

    print(correlation_matrix)
    print(monthly_changes)
    print(weekly_changes)
    
def ru_ua_analysis(df):
    first_day = "2022-01-01"
    last_day = "2022-04-30"
    merged_df = df[(df['Data']>=first_day) & (df['Data']<= last_day)]
    fig, ax1 = plt.subplots(figsize=(10, 6))

    wig20, = ax1.plot(merged_df['Data'], merged_df['WIG20'], label='WIG20', color='blue')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('WIG20 cena zamknięcia', color='black')

    ax2 = ax1.twinx()

    dax, = ax2.plot(merged_df['Data'], merged_df['DAX'], label='DAX', color='red')
    NASDAQ, = ax2.plot(merged_df['Data'], merged_df['NASDAQ'], label='NASDAQ', color='green')
    ax2.set_ylabel('DAX & NASDAQ cena zamknięcia', color='black')

    lines = [wig20, dax, NASDAQ]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    plt.title('Porównanie Cen Indeksów Giełdowych')
    plt.show()

    correlation_matrix = merged_df[['WIG20', 'DAX', 'NASDAQ']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', square=True)
    plt.title('Macierz korelacji indeksów giełdowych')
    plt.show()

    merged_df.set_index('Data', inplace=True)
    monthly_df = merged_df.resample('M').last()
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
    table.scale(1.2, 1.2)
    ax.set_title('Miesięczne zmiany procentowe',y=0.57)
    plt.show()
    

    merged_df.reset_index(inplace=True)
    weekly_changes = merged_df.set_index('Data').resample('W').mean().pct_change()
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
    table.scale(1.2, 1.2)
    ax.set_title('Tygodniowe zmiany procentowe',y=0.74)
    plt.show()



    print(correlation_matrix)
    print(monthly_changes)
    print(weekly_changes)
    
def bank_crysis_analysis(df):
    first_day = "2008-06-01"
    last_day = "2008-12-31"

    merged_df = df[(df['Data']>=first_day) & (df['Data']<= last_day)]
    fig, ax1 = plt.subplots(figsize=(10, 6))

    wig20, = ax1.plot(merged_df['Data'], merged_df['WIG20'], label='WIG20', color='blue')
    NASDAQ, = ax1.plot(merged_df['Data'], merged_df['NASDAQ'], label='NASDAQ', color='green')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('WIG20 & NASDAQ cena zamknięcia', color='black')

    ax2 = ax1.twinx()

    dax, = ax2.plot(merged_df['Data'], merged_df['DAX'], label='DAX', color='red')
    ax2.set_ylabel('DAX cena zamknięcia', color='black')

    lines = [wig20, dax, NASDAQ]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels)
    plt.title('Porównanie Cen Indeksów Giełdowych')
    plt.show()

    correlation_matrix = merged_df[['WIG20', 'DAX', 'NASDAQ']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', square=True)
    plt.title('Macierz korelacji indeksów giełdowych')
    plt.show()

    merged_df.set_index('Data', inplace=True)
    monthly_df = merged_df.resample('M').last()
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
    table.scale(1.2, 1.2)
    ax.set_title('Miesięczne zmiany procentowe',y=0.6)
    plt.show()

    weekly_df = merged_df.resample('W').last()
    weekly_changes = weekly_df.pct_change()
    weekly_changes.reset_index(inplace=True)
    weekly_changes = weekly_changes.dropna()
    weekly_changes['Numer Tygodnia'] = weekly_changes["Data"].dt.week

    weekly_changes['Numer Tygodnia'] = weekly_changes['Numer Tygodnia'].map(lambda x: f'Tydzień {x}')
    # Drop Week 1
    weekly_changes = weekly_changes[weekly_changes['Numer Tygodnia'] != 'Week 1']
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
    table.scale(1.2, 1.2)
    ax.set_title('Tygodniowe zmiany procentowe',y=0.92)
    
    plt.show()

if __name__ == "__main__":
    final_df = prepare_data()
    covid_analysis(final_df)
    ru_ua_analysis(final_df)
    bank_crysis_analysis(final_df)
    print("DONE")
    