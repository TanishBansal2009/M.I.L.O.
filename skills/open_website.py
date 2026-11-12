import webbrowser
from urllib.parse import urlparse
from google.genai import types
from skills.common import clean_text, strip_polite_prefixes, strip_polite_suffixes
from skills.sites import KNOWN_SITES

OPEN_TRIGGERS = ("open ", "go to ", "take me to ", "launch ")

FILLER_WORDS = ("the", "website", "site", "page", "web", "please")

NOT_A_SITE_WORDS = ("a", "an", "my", "this", "that", "it",
                    "how", "what", "why", "who", "when", "where")


def extract_site_request(user_input: str) -> str | None:
    text = strip_polite_prefixes(clean_text(user_input))

    for trigger in OPEN_TRIGGERS:
        if text.startswith(trigger):
            target = strip_polite_suffixes(text.removeprefix(trigger).strip())

            words = [w for w in target.split() if w not in FILLER_WORDS]
            return " ".join(words)

    return None


def looks_like_website(name: str) -> bool:
    words = name.split()

    if len(words) == 0 or len(words) > 3:
        return False

    for word in words:
        if word in NOT_A_SITE_WORDS:
            return False

    return True


def get_url_for_site(client, model: str, site_description: str) -> str | None:
    try:
        response = client.models.generate_content(
            model=model,
            contents=(
                f"The user wants to open: '{site_description}'. "
                "If this is a real, well-known website, respond with ONLY its "
                "official https:// URL. If it is not a website, or you are "
                "not sure, respond with ONLY the word NONE. "
                "No extra words, no markdown, no backticks."
            ),
            config=types.GenerateContentConfig(
                temperature=0, 
            ),
        )
        raw = (response.text or "").strip()
    except Exception:
        return None

    url = raw.strip("`'\" \n")

    if url.upper() == "NONE":
        return None

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None

    parts = parsed.netloc.split(".")
    if len(parts) < 2 or "" in parts or len(parts[-1]) < 2:
        return None

    return url


def try_handle_open_site(user_input: str, client, model: str, ask_yes_no) -> str | None:
    site_description = extract_site_request(user_input)
    if site_description is None:
        return None

    # Step 1: check our own list first (fast, no API, and names in our list are trusted)
    url = KNOWN_SITES.get(site_description)
    found_by_api = False

    if url is None:
        # Step 2: not in our list, so does it even look like a website?
        # If not, treat it as chat
        if not looks_like_website(site_description):
            return None

        # Step 3: only now ask the API
        url = get_url_for_site(client, model, site_description)
        found_by_api = True

    # Step 4: API said it's not a website, so let normal chat handle it
    if url is None:
        return None

    # Step 5: the API can be wrong, so check with the user before opening
    if found_by_api:
        if not ask_yes_no(f"I think '{site_description}' is {url} - should I open it?"):
            return "Okay, I won't open it."

    if not webbrowser.open(url):
        return f"I couldn't open a browser here, but the link is {url}"

    return f"Opening {site_description} for you."