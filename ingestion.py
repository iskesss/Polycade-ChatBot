from text_to_doc import get_doc_chunks
from web_crawler import get_data_from_website
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
import time
import random
import tiktoken


def pause() -> None:
    pause_time = random.uniform(0.5, 5)
    time.sleep(pause_time)


def ingest_all_polycade_data() -> (
    None
):  # very purpose-built for this project. not generalizable!

    ingest_tech_specs_table()  # call this first
    ingest_handmade_nontabular_knowledgebase()  # then call this

    outfile = open("development/everything_ingested.txt", "w")

    # now we crawl the Polycade webpages for additional information
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
        "https://polycade.com/pages/ags-game-list",
        "https://polycade.com/collections/merch/products/polycade-logo-tee-unisex",
        "https://polycade.com/collections/merch/products/polycade-logo-t-dark"
        "https://polycade.com/collections/merch/products/retro-future-tee",
        "https://polycade.com/collections/merch/products/long-sleeve-t-shirt",
        "https://polycade.com/collections/merch/products/joystick-emoji-dad-cap",
        "https://polycade.com/collections/merch/products/polycade-logo-tee-toddler",
        "https://polycade.com/collections/merch/products/unisex-zip-hoodie",
        "https://polycade.com/collections/support/products/system-support-30-minutes",
        "https://polycade.com/collections/support/products/polycade-3-year-extended-warranty",
        "https://polycade.com/pages/polycade-software",
        "https://polycade.com/pages/neo-arcade-board-setup",
    }

    # random.shuffle(sites_to_crawl)  # to prevent a blacklist from the Polycade server. but we can't .shuffle() a set. shit!

    pc = Pinecone()  # i don't think we actually need this here

    embeddings_instance = OpenAIEmbeddings(model="text-embedding-3-large")

    for site in sites_to_crawl:
        pause()  # to prevent a blacklist from the Polycade server
        print(f"\t> Now ingesting {site}...")

        text, metadata = get_data_from_website(site)
        documents = get_doc_chunks(text, metadata)
        PineconeVectorStore.from_documents(
            documents, embeddings_instance, index_name="website-knowledgebase"
        )

        outfile.write(f"\n\n----------------- FROM {site} -----------------")
        for doc in documents:
            # let's send only the page content to the outfile for legibility's sake
            outfile.write("\n\n")
            outfile.write(doc.page_content)

    outfile.close()
    print("Done! Yay! You didn't get ratelimited!")

    return


def ingest_handmade_nontabular_knowledgebase() -> None:
    with open(
        "/Users/jordanbouret/Library/Mobile Documents/iCloud~md~obsidian/Documents/JordansVault/Polycade ChatBot Handmade Nontabular Knowledgebase.md",
        "r",
    ) as file:
        markdown_text = file.read()

    documents = get_doc_chunks(
        markdown_text, {"source": "https://polycade.com/"}
    )  # metadata is just a general link to the Polycade website homepage since the markdown data came from a multitude of sources around it

    embeddings_instance = OpenAIEmbeddings(model="text-embedding-3-large")
    print(f"\t> Now ingesting handmade nontabular knowledgebase...")
    PineconeVectorStore.from_documents(
        documents, embeddings_instance, index_name="website-knowledgebase"
    )

    # outfile = open("development/ingest_handmade_nontabular_knowledgebase.txt", "w")
    # for doc in documents:
    #     outfile.write("\n\n\n\n")
    #     outfile.write(doc.page_content)
    # outfile.close()

    return None


def ingest_tech_specs_table() -> None:
    with open(
        "/Users/jordanbouret/Library/Mobile Documents/iCloud~md~obsidian/Documents/JordansVault/Polycade ChatBot Tech Spec Comparisons.md",
        "r",
    ) as file:
        markdown_text = file.read()

    documents = get_doc_chunks(
        text=markdown_text,
        metadata={"source": "https://polycade.com/pages/compare"},
        chunk_size=2048,
        chunk_overlap=0,
    )  # metadata is just a general link to the Polycade website homepage since the markdown data came from a multitude of sources around it

    embeddings_instance = OpenAIEmbeddings(model="text-embedding-3-large")
    print(f"\t> Now ingesting tech specs table...")
    PineconeVectorStore.from_documents(
        documents, embeddings_instance, index_name="website-knowledgebase"
    )

    # outfile = open("development/ingest_tech_specs_table.txt", "w")
    # for doc in documents:
    #     outfile.write("\n\n\n\n")
    #     outfile.write(doc.page_content)
    # outfile.close()

    return None


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


def calculate_embedding_cost(file_path: str) -> float:
    with open(file_path, "r") as file:
        markdown_text = file.read()


def num_tokens_from_md_file(filepath: str, encoding_name: str) -> int:
    """Returns the number of tokens from a given markdown file."""
    with open(filepath, "r") as file:
        markdown_text = file.read()
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(markdown_text))
    return num_tokens


def num_tokens_from_txt_file(filepath: str, encoding_name: str) -> int:
    """Returns the number of tokens from a given text file."""
    with open(filepath, "r") as file:
        text = file.read()
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

# ingest_all_polycade_data()

# test_single_site_ingestion("https://polycade.com/collections/arcade-machines")

# raw_site_text(
#     "https://polycade.com/collections/arcade-machines/products/polycade-sente-white-with-stripes"
# )

# print(
#     num_tokens_from_md_file(
#         filepath="/Users/jordanbouret/Library/Mobile Documents/iCloud~md~obsidian/Documents/JordansVault/Polycade ChatBot Info.md",
#         encoding_name="cl100k_base",
#     )
#     + num_tokens_from_txt_file(
#         filepath="development/everything_ingested.txt", encoding_name="cl100k_base"
#     )
# )


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

# INGESTION:

# TODO: FURTHER INVESTIGATE MODEL SPEC DIFFERENCES. Like what is this about?: https://polycade.com/pages/polycade-specifications

# TODO: MAYBE implement MMR to reduce repetition.

# TODO: INGEST ALL OF THE FORUMS for better troubleshooting support. You're gonna need Tyler's help with aquiring all of the forum data.

# TODO: Ingest a list of all Polycade locations. Get this from Tyler since the one on the website may be outdated.

# FRONTEND:

# TODO: Use a Polycade wallpaper for the background of your Streamlit website. They can be found here: https://polycade.com/pages/wallpapers
