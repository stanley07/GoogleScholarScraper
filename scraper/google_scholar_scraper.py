import requests
from bs4 import BeautifulSoup

def fetch_research_papers(keyword):
    url = f'https://scholar.google.com/scholar?q={keyword}&hl=en&as_sdt=0,5'

    # Download the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract paper tags
    paper_tags = soup.find_all('div', class_='gs_ri')

    papers = []

    # Extract paper information
    for tag in paper_tags:
        title = tag.find('h3', class_='gs_rt').text
        citation_count = tag.find('a', class_='gs_or_cit').text
        url = tag.find('h3', class_='gs_rt').a['href']
        author = tag.find('div', class_='gs_a').text

        paper_info = {
            'Title': title,
            'Citation Count': citation_count,
            'URL': url,
            'Author': author
        }

        papers.append(paper_info)

    return papers
