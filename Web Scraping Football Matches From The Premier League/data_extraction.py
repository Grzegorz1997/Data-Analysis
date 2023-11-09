import pandas as pd
from bs4 import BeautifulSoup
import requests

class EplDataDownload():
    def __init__(self,url_path:str):
        self.url_path = url_path
        
    def clean_links(self,soup_object,url_text):
        links = soup_object.select("a")
        links = [link.get("href") for link in links]
        links = [link for link in links if link and url_text in link]
        full_links = [f"https://fbref.com/{link}" for link in links]
        return full_links
        
    def get_stats_table(self):
        url_data = requests.get(self.url_path)
        soup = BeautifulSoup(url_data.text)
        league_table = soup.select('table.stats_table')[0]
        links = self.clean_links(league_table,"/squads/")
        team_link = links[0] # loop for each team - next function
        self.team_data = requests.get(team_link)
        self.stats_df = pd.read_html(self.team_data.text,match="Scores & Fixtures")[0]
        print(self.stats_df.head())
    
    def get_shooting_table(self):
        soup_team = BeautifulSoup(self.team_data.text)
        links = self.clean_links(soup_team,"/all_comps/shooting/")
        shoot_link = links[0]
        shoot_data = requests.get(shoot_link)
        self.shoot_df = pd.read_html(shoot_data.text, match = "Shooting",header=1)[0]
    
    def merge(self):
        self.merged_df = self.stats_df.merge(self.shoot_df[['Date','Sh', 'SoT','Dist', 'FK','PK', 'PKatt']], on="Date",how="inner")
        
    def scrap_and_merge(self):
        self.get_stats_table()
        self.get_shooting_table()
        self.merge()
        return self.merged_df
        
if __name__ == "__main__":
    c1 = EplDataDownload("https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats#all_league_structure")
    df = c1.scrap_and_merge()
    print(df.head())