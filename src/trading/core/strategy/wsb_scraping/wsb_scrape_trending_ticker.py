"""Get a single WSB trending ticker from an auto-refreshed list. We want the most rising mentions within the top 5."""

from heapq import nlargest

import requests  # type: ignore
from bs4 import BeautifulSoup


def get_html() -> str:
    """Scrape the HTML to get a list of tickers."""
    # The URL of the page you want to scrape
    url = "https://altindex.com/wallstreetbets"

    # Send a GET request to the URL
    response = requests.get(url, timeout=60)
    soup = BeautifulSoup(response.content, "html.parser")
    html_content: str = soup.prettify()

    return html_content


def get_stock_dictionary(html: str) -> dict[str, float]:
    """Parse the HTML to obtain a list of tickers and their corresponding % mentions"""
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')

    stock_data = {}

    # Iterate through each row in the table
    for row in rows:
        # Find the stock name
        company_cell = row.find('span', class_="text-gray text-small")
        if company_cell:
            company_cell = company_cell.text.strip()

            # Find the percentage of mentions
            mention_cell = row.find_all('td')[2]
            if mention_cell:
                percentage = mention_cell.find('span').text.strip()
                stock_data[company_cell] = float(percentage.replace('%', ''))

    return stock_data


def get_final_ticker(stock_data: dict[str, float], top_k: int = 5, top_p: int = 2) -> list[str]:
    """Get the ticker with the most recent mentions"""
    top_keys = [key for key in stock_data if key not in ["RDDT", "SPY"]][:top_k]
    filtered_data = {key: stock_data[key] for key in top_keys}
    top_p_keys = nlargest(top_p, filtered_data, key=filtered_data.get)  # type: ignore

    return top_p_keys


def scrape_top_trending_wsb_ticker() -> list[str] | None:
    """Return the final ticker with most mentions"""
    try:
        html_content = get_html()
        stocks_dict = get_stock_dictionary(html_content)
        ticker_symbol = get_final_ticker(stocks_dict)
    except (ValueError, IndexError, TimeoutError):
        ticker_symbol = None
    return ticker_symbol
