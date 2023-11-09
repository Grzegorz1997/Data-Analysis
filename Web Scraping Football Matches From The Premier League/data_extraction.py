import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests

class EplDataDownload():
    def __init__(self,url_path:str):
        self.url_path = url_path
        
    def get_stats_table(self):
        url_data = requests.get(self.url_path)
        soup = BeautifulSoup(url_data.text)
        league_table = soup.select('table.stats_table')[0]
        links = league_table.select("a")
        links = [link.get("href") for link in links]
        cleaned_links = [link for link in links if "/squads/" in link]
        full_links = [f"https://fbref.com/{link}" for link in cleaned_links]
        team_link = full_links[0] # loop for each team - next function
        
        self.team_data = requests.get(team_link)
        self.stats_df = pd.read_html(self.team_data.text,match="Scores & Fixtures")[0]
    
    def get_shooting_table(self):
        soup_team = BeautifulSoup(self.team_data.text)
        links = soup_team.select("a")
        links = [link.get("href") for link in links]
        cleaned_links = [link for link in links if link and "/all_comps/shooting/" in link]
        cleaned_links = [f"https://fbref.com/{link}" for link in cleaned_links]
        shoot_link = cleaned_links[0]
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