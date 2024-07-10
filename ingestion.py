from text_to_doc import get_doc_chunks
from web_crawler import get_data_from_website
import time
import random


def pause() -> None:
    pause_time = random.uniform(0.5, 2)
    time.sleep(pause_time)


def ingest_all_polycade_data() -> (
    None
):  # very purpose-built for this project. not generalizable!

    outfile = open("development/everything_ingested.txt", "w")

    sites_to_crawl = [
        "https://polycade.com/",
        "https://polycade.com/collections/arcade-machines",
        "https://polycade.com/collections/arcade-machines/products/polycade-sente-white-with-stripes",
    ]

    random.shuffle(sites_to_crawl)  # to prevent a blacklist from the Polycade server

    for site in sites_to_crawl:
        pause()  # to prevent a blacklist from the Polycade server
        print(f"\t> Now ingesting {site}...")

        text, metadata = get_data_from_website(site)
        docs = get_doc_chunks(text, metadata)

        outfile.write(f"\n\n----------------- FROM {site} -----------------")
        for doc in docs:
            outfile.write("\n\n")
            outfile.write(doc.page_content)
            # outfile.write(str(doc.metadata)) # very repetitive and would clog up the vectorstore if actually ingested

    outfile.close()
    return


def test_single_site_ingestion(url: str) -> None:
    text, metadata = get_data_from_website(url)
    docs = get_doc_chunks(text, metadata)

    outfile = open("development/single_site_test.txt", "w")
    for doc in docs:
        outfile.write("\n\n")
        outfile.write(doc.page_content)
        outfile.write(str(doc.metadata))
    outfile.close()

    return


def raw_site_text(url: str) -> None:
    text, metadata = get_data_from_website(url)
    outfile = open("development/show_raw_site_text.txt", "w")
    outfile.write(text)
    outfile.close()
    return


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

# ingest_all_polycade_data()

# test_single_site_ingestion("https://polycade.com/collections/arcade-machines")

raw_site_text("https://polycade.com/collections/arcade-machines")

# TODO: Ingest polycade machine locations.

# TODO: MAYBE implement MMR to reduce repetition.
