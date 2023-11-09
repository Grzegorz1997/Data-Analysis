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
        
    def get_stats_links(self):
        url_data = requests.get(self.url_path)
        soup = BeautifulSoup(url_data.text)
        league_table = soup.select('table.stats_table')[0]
        self.links = self.clean_links(league_table,"/squads/")
        return self.links
    
    def get_stats_table(self,team_index):
        team_link = self.links[team_index] # loop for each team - next function
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
        
    def loop_each_team(self):
        concat_df = pd.DataFrame()
        team_links = self.get_stats_links()
        for team in team_links:
            self.get_stats_table(team_links.index(team))
            self.get_shooting_table()
            df = self.merge()
            self.concat_df = concat_df.append(df)

    def scrap_epl_data(self):
        self.loop_each_team()
        return self.concat_df
    
if __name__ == "__main__":
    c1 = EplDataDownload("https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats#all_league_structure")
    df = c1.scrap_epl_data()
    print(df.head())
    df.to_excel(r"C:\Python Scripts\Data Analysis\Web Scraping Football Matches From The Premier League\test.xlsx")