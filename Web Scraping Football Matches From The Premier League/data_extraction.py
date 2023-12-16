import pandas as pd
from bs4 import BeautifulSoup
import requests

class EplDataDownload():
    def __init__(self,url_path:str):
        self.url_path = url_path
        
    def clean_links(self,soup_object,url_text):
        """
        Cleans and filters links from a BeautifulSoup object based on a given URL text.
        Parameters:
        - soup_object (BeautifulSoup): The BeautifulSoup object containing links.
        - url_text (str): The text to filter links.
        Returns a list of cleaned and filtered full links.
        """
        links = soup_object.select("a")
        links = [link.get("href") for link in links]
        links = [link for link in links if link and url_text in link]
        full_links = [f"https://fbref.com/{link}" for link in links]
        return full_links
        
    def get_stats_links(self):
        """
        Returns list of team links based on the 'stats_table' class in the HTML content.
        with /squads/ inside link
        """
        url_data = requests.get(self.url_path)
        soup = BeautifulSoup(url_data.text)
        league_table = soup.select('table.stats_table')[0]
        self.links = self.clean_links(league_table,"/squads/")
        return self.links
    
    def get_stats_table(self,team_index):
        """
        Fetches and assignes the 'stats_df' attribute with the scores and fixtures t
        table for a specific team from a given webpage.
        Parameters:
        team_index: The index of the team link in the 'links' attribute.
        """
        team_link = self.links[team_index]
        self.team_data = requests.get(team_link)
        self.stats_df = pd.read_html(self.team_data.text,match="Scores & Fixtures")[0]
    
    def get_shooting_table(self):
        """Fetches and assignes the 'shoot_df' attribute with the shooting statistics table
        for a specific team from a given webpage.
        """
        soup_team = BeautifulSoup(self.team_data.text)
        links = self.clean_links(soup_team,"/all_comps/shooting/")
        shoot_link = links[0]
        shoot_data = requests.get(shoot_link)
        self.shoot_df = pd.read_html(shoot_data.text, match = "Shooting",header=1)[0]
        
    def merge(self):
        """Merge Scores & Fixtures and Shooting tables"""
        self.merged_df = self.stats_df.merge(self.shoot_df[['Date','Sh', 'SoT','Dist', 'FK','PK', 'PKatt']], on="Date",how="inner")
    
    def filter_df(self):
        """Filter dataframe, keep only rows where it was Premier League match"""
        self.filtered_df = self.merged_df[self.merged_df["Comp"] == "Premier League"]
        return self.filtered_df
    
    def loop_each_team(self):
        """
        Iterates through each team, fetches and processes statistics tables, merges and appends
        the results to 'concat_df'.
        """
        self.concat_df = pd.DataFrame()
        team_links = self.get_stats_links()
        for team in team_links:  
            self.get_stats_table(team_links.index(team))
            self.get_shooting_table()
            self.merge()
            df = self.filter_df()
            df["team_name"] = team.split("/")[-1].split("-Stats")[0].replace("-"," ")
            start_year = (pd.to_datetime(df["Date"]).dt.year).min()
            end_year = (pd.to_datetime(df["Date"]).dt.year).max()
            df["season"] = f"{start_year}-{end_year}"
            self.concat_df = self.concat_df.append(df)
            print(self.concat_df.shape[0])
        print(self.concat_df.shape[0])
    
    def scrap_epl_data(self):
        self.loop_each_team()
        return self.concat_df