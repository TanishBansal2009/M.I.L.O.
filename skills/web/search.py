import webbrowser
from urllib.parse import quote_plus

from skills.common import clean_text, strip_polite_prefixes, strip_polite_suffixes

SEARCH_TRIGGERS = (
    "search the web for ", "search the internet for ", "search online for ",
    "search for ", "search up ", "search ",
    "look up ", "lookup ", "ask google ", "google ",
)

GENERIC_SUFFIXES = (" on the internet", " on the web", " online")

SEARCH_SITES = {
    "google":      ("Google",      "https://www.google.com/search?q={q}"),
    "youtube":     ("YouTube",     "https://www.youtube.com/results?search_query={q}"),
    "wikipedia":   ("Wikipedia",   "https://en.wikipedia.org/w/index.php?search={q}"),
    "amazon":      ("Amazon",      "https://www.amazon.in/s?k={q}"),
    "flipkart":    ("Flipkart",    "https://www.flipkart.com/search?q={q}"),
    "github":      ("GitHub",      "https://github.com/search?q={q}"),
    "maps":        ("Google Maps", "https://www.google.com/maps/search/?api=1&query={q}"),
    "google maps": ("Google Maps", "https://www.google.com/maps/search/?api=1&query={q}"),
}

NOT_A_QUERY_WORDS = (
    "it", "this", "that", "them", "here", "there", "something", "anything",
    "me", "you", "your", "yourself", "my", "at", "to", "into", "for", "on",
    "is", "are", "was", "were", "has", "have", "does", "do", "did",
    "can", "could", "will", "would", "should",
)

UNFINISHED_ENDINGS = ("for", "on", "about", "of", "and", "to", "in", "the", "a", "an")

MAX_QUERY_WORDS = 15
MAX_QUERY_CHARS = 200


def extract_search_request(user_input: str) -> str | None:
    text = strip_polite_prefixes(clean_text(user_input))

    for trigger in SEARCH_TRIGGERS:
        if text.startswith(trigger):
            query = strip_polite_suffixes(text.removeprefix(trigger).strip())

            for suffix in GENERIC_SUFFIXES:
                if query.endswith(suffix):
                    query = query.removesuffix(suffix).strip()

            for lead in ("for ", "about "):
                if query.startswith(lead):
                    query = query.removeprefix(lead).strip()

            return query

    return None


def split_site_and_query(query: str) -> tuple[str, str]:
    for site in sorted(SEARCH_SITES, key=len, reverse=True):
        if query.startswith(f"{site} for "):
            return site, query.removeprefix(f"{site} for ").strip()
        if query.endswith(f" on {site}"):
            return site, query.removesuffix(f" on {site}").strip()
    return "google", query


def looks_like_search(query: str) -> bool:
    if not query:
        return False

    if len(query) > MAX_QUERY_CHARS or len(query.split()) > MAX_QUERY_WORDS:
        return False

    if not any(ch.isalnum() for ch in query):
        return False

    words = query.split()

    if words[0] in NOT_A_QUERY_WORDS:
        return False

    if words[-1] in UNFINISHED_ENDINGS:
        return False

    return True


def try_handle_search(user_input: str) -> str | None:

    query = extract_search_request(user_input)
    if query is None:
        return None

    site, query = split_site_and_query(query)

    if not looks_like_search(query):
        return None

    site_name, url_template = SEARCH_SITES[site]

    url = url_template.format(q=quote_plus(query))

    if not webbrowser.open(url):
        return f"I couldn't open a browser here, but this is the link: {url}"

    return f"Searching {site_name} for '{query}'."