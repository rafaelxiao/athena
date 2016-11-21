import requests
from bs4 import BeautifulSoup

# Extract urls to form a list
def get_urls(url):
    header = {'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}
    response = requests.get(url, header)
    soup = BeautifulSoup(response.text.encode(response.encoding).decode('utf-8'), 'lxml')
    links = soup.find_all('a')
    list = []
    for i in links:
        link = i.get('href', None)
        # Make sure that link is not null
        if link is not None and link !='':
            # Get rid of 'javascript'
            if link[0]!='j':
                list.append(link)
    return list

list = get_urls('http://www.eastmoney.com')
for i in list:
    print(i)