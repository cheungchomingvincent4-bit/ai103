import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()
search_client = SearchClient(os.getenv("SEARCH_ENDPOINT"), os.getenv("INDEX_NAME"), AzureKeyCredential(os.getenv("QUERY_KEY")))


def show(title, results, fields):
    print(f"\n== {title}: {results.get_count()} documents")
    for document in results:
        print("  " + " | ".join(str(document[field]) for field in fields))


# 1. Every document in the index
results = search_client.search(search_text="*", include_total_count=True, select=["title"])
show("Everything", results, ["title"])

# 2. Only some fields: the locations were added by an AI skill
results = search_client.search(search_text="*", include_total_count=True, select=["title", "locations"])
show("Titles and locations", results, ["title", "locations"])

# 3. Documents that mention New York, with their key phrases
results = search_client.search(search_text="New York", include_total_count=True, select=["title", "keyPhrases"])
show("New York", results, ["title", "keyPhrases"])

# 4. The same search, filtered to files smaller than 380,000 bytes
results = search_client.search(search_text="New York", include_total_count=True,
                               select=["title", "metadata_storage_size"],
                               filter="metadata_storage_size lt 380000")
show("New York, small files only", results, ["title", "metadata_storage_size"])

# 5. Which places do the brochures mention most?
results = search_client.search(search_text="*", facets=["locations,count:5"], top=0)
print("\n== Top locations")
for facet in results.get_facets()["locations"]:
    print(f"  {facet['value']}: {facet['count']} documents")

# 6. Semantic ranking: answer a question, with captions
results = search_client.search(
    search_text="Where can I see a famous bridge?",
    query_type="semantic",
    semantic_configuration_name="margies-index-semantic-configuration",
    query_caption="extractive",
    select=["title"],
    top=3
)
print("\n== Semantic search")
for document in results:
    print(f"  {document['title']} (reranker score {document['@search.reranker_score']:.2f})")
    for caption in document["@search.captions"] or []:
        print("     " + caption.text)
