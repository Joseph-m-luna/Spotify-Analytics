import requests
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

class AZLyrics:
    def __init__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        self.xparam = self.get_search_token()
        

    def get_search_token(self):
        # Turns out in order to search, we need a valid token. 
        # If error occurs, we'll need some logic to get a new token to search, 
        # as it seems to expire after on creation of a new session

        url = "https://search.azlyrics.com/"
        self.driver.get(url)
        
        try:
            # Wait for the hidden input field to be present
            hidden_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='hidden' and @name='x']"))
            )
            token = hidden_input.get_attribute("value")
        except Exception as e:
            print(f"Exception occurred while getting the search token: {e}")
            token = None
        
        self.driver.quit()

        return token

    def fetch_all_lyrics(self, query):
        query = query.replace(" ", "+")

        wparam = "lyrics"
        page = 1
        url = f"https://search.azlyrics.com/search.php?q={query}&w={wparam}&p={page}&x={self.xparam}"

        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        lyrics_section = soup.find_all("div", class_="panel-heading")

        if not lyrics_section:
            return []
        
        pages_section = lyrics_section[0].find("small").text.strip("[]").split(" ")
        page_size = int(pages_section[0].split("-")[1])
        total_pages = int(pages_section[2])

        num_pages = -(total_pages // -page_size)

        all_results = []
        for i in range(num_pages):
            page = self.fetch_lyrics_page(query, i+1, xparam=self.xparam)
            all_results.extend(page)

        return all_results
    
    def fetch_lyrics_page(self, query, page, xparam):
        wparam = "lyrics"
        url = f"https://search.azlyrics.com/search.php?q={query}&w={wparam}&p={page}&x={xparam}"

        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        # lyric results
        lyrics_section = soup.find_all("div", class_="panel-heading")
        
        if len(lyrics_section) > 0:
            lyrics_section = lyrics_section[0].find_parent().find_all("td", class_="text-left visitedlyr")
        else:
            return []

        all_results = []
        
        for i, lyrics in enumerate(lyrics_section):
            result = {}

            href = lyrics.find("a")["href"]

            title = lyrics.find("span").text[1:-1]
            artist = lyrics.find_all("b")[1].text
            result["href"] = href
            result["title"] = title
            result["artist"] = artist

            all_results.append(result)

        return all_results
    
    def fetch_lyrics(self, url):
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        descriptor = soup.find("h1").text
        lyrics = soup.find(string=lambda text: isinstance(text, Comment) and "Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement" in text).find_parent("div")

        with open("test.html", "w") as file:
            file.write(soup.prettify())
        if lyrics is None:
            return None
        else:
            return lyrics.text

if __name__ == "__main__":
    lyric_api = AZLyrics()
    search_results = lyric_api.fetch_all_lyrics("somebody to lean on")
    lyrics = lyric_api.fetch_lyrics(search_results[0]["href"])