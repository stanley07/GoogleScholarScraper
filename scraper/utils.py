from bs4 import BeautifulSoup


def get_tags(soup, tag_name, **kwargs):
    """
    Extracts and returns a list of tags with the specified tag name and attributes from the given BeautifulSoup object.
    """
    tags = soup.find_all(tag_name, **kwargs)
    return tags


def extract_paper_info(tag):
    """
    Extracts and returns the title, citation count, URL, and author information from the given paper tag.
    """
    title_tag = tag.find('h3', class_='gs_rt')
    title = title_tag.text.strip() if title_tag else None

    citation_tag = tag.find('a', class_='gs_or_cit')
    citation_count = citation_tag.text.split()[-1] if citation_tag else '0'

    url_tag = tag.find('a', class_='gs_rt')
    url = url_tag['href'] if url_tag else None

    author_tags = tag.find_all('a', class_='gs_a')
    authors = [author.text for author in author_tags]

    paper_info = {
        'Title': title,
        'Citation Count': citation_count,
        'URL': url,
        'Author': ', '.join(authors)
    }

    return paper_info
