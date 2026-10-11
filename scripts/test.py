import requests
from bs4 import BeautifulSoup

r = requests.get("https://books.toscrape.com")
soup = BeautifulSoup(r.text, "html.parser")
print(soup.title.text.strip())
