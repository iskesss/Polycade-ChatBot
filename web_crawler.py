import requests
from bs4 import BeautifulSoup
import html2text


def get_data_from_website(url):
    """
    Retrieve text content and metadata from a given URL.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        tuple: A tuple containing the text content (str) and metadata (dict).
    """
    # Get response from the server
    response = requests.get(url)
    if response.status_code == 500:
        print("Server error")
        return
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # outfile = open("development/show_raw_site_text.txt", "w")  # DELETE LATER!
    # outfile.write(str(soup.find("main")))  # DELETE LATER!
    # outfile.close()  # DELETE LATER!

    # Removing js and css code
    for script in soup(["script", "style"]):
        script.extract()

    # Extract page metadata
    try:
        page_title = soup.title.string.strip()
    except:
        page_title = url.path[1:].replace("/", "-")
    meta_description = soup.find("meta", attrs={"name": "description"})
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    if meta_description:
        description = meta_description.get("content")
    else:
        description = page_title
    if meta_keywords:
        meta_keywords = meta_description.get("content")
    else:
        meta_keywords = ""

    metadata = {
        "title": page_title,
        "url": url,
        "description": description,
        "keywords": meta_keywords,
    }

    # Ensure that only the main content of the Polycade webpage is extracted, not the main menu or footers
    soup = soup.find("main")

    # Extract text in markdown format
    html = str(soup)
    html2text_instance = html2text.HTML2Text()
    html2text_instance.images_to_alt = True
    html2text_instance.body_width = 0
    html2text_instance.single_line_break = True
    text = html2text_instance.handle(html)

    return text, metadata


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

get_data_from_website(
    "https://polycade.com/collections/arcade-machines/products/polycade-sente-white-with-stripes"
)
