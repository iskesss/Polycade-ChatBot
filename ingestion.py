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

    sites_to_crawl = {  # using a set prevents accidental duplicates
        "https://polycade.com/",
        "https://polycade.com/collections/arcade-machines",
        "https://polycade.com/collections/arcade-machines/products/polycade-sente-white-with-stripes",
        "https://polycade.com/collections/arcade-machines/products/polycade-retro?variant=42403902390464",
        "https://polycade.com/collections/arcade-machines/products/polycade-squadcade",
        "https://polycade.com/products/polycade-gamepad",
        "https://polycade.com/products/light-guns",
        "https://polycade.com/products/light-gun-holsters",
        "https://polycade.com/products/light-guns-holsters-set",
        "https://polycade.com/products/trackball-arcade-controller",
        "https://polycade.com/products/spinflight-arcade-controller",
        "https://polycade.com/products/retro-4-way-arcade-controller",
        "https://polycade.com/products/dual-stick-arcade-controller",
        "https://polycade.com/products/buttonmash-arcade-controller",
        "https://polycade.com/products/standard-joystick-panel",
        "https://polycade.com/products/neo-arcade-controller-board",
        "https://polycade.com/products/magnet-pack",
        "https://polycade.com/products/storage-rack",
        "https://polycade.com/products/cupholders-panel-inserts",
        "https://polycade.com/products/console-shelf",
        "https://polycade.com/products/atx-pc-chassis",
        "https://polycade.com/products/retro-bar-stool",
        "https://polycade.com/products/modern-bar-stool",
        "https://polycade.com/collections/commercial-pay-to-play-accessories/products/commercial-kit",
        "https://polycade.com/collections/commercial-pay-to-play-accessories/products/credit-card-reader",  # exclude? offers very little info
        "https://polycade.com/collections/commercial-pay-to-play-accessories/products/bill-validator",  # exclude? offers very little info
    }

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

raw_site_text(
    "https://polycade.com/collections/commercial-pay-to-play-accessories/products/credit-card-reader"
)

# TODO: Ingest polycade machine locations.

# TODO: Ingest all the info you manually compiled in that Obsidian file

# TODO: MAYBE implement MMR to reduce repetition.

# TODO: Once you have copy priviledges, add this to your corpus of product info: https://docs.google.com/spreadsheets/d/1DDXZDdminwp1kD0hk1KWA1Q55nerNY1uERJt7sufy-4/edit?gid=0#gid=0
