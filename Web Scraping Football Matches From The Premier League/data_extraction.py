import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests

class EplDataDownload():
    def __init__(self,url_path:str):
        self.url_path = url_path
        
    
