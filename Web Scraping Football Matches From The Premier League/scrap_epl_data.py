import pandas as pd
from data_extraction import EplDataDownload

def get_multiple_seasons(output_path):
    """"return dataframe with each team statistics from multiple premier league season
    Parameters:
    "otuput_path - path where excel file will be saved"""
    concat_df = pd.DataFrame()
    for year in range(2016,2024):
        start_year = year -1
        end_year = year
        season_url = fr"https://fbref.com/en/comps/9/{start_year}-{end_year}/{start_year}-{end_year}-Premier-League-Stats#all_league_structure"
        try:
            c1 = EplDataDownload(season_url)
            df = c1.scrap_epl_data()
            concat_df = concat_df.append(df)
        except:
            print(f"Couldnt connect to {season_url}")
    concat_df.to_excel(output_path)

if __name__ == "__main__":
    get_multiple_seasons()
    print("Done")
