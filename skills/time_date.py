from datetime import datetime

from skills.common import simple_text

TIME_PHRASES = (
    "what time is it", "what time it is", "whats the time", "what is the time",
    "whats the current time", "what is the current time", "current time",
    "tell me the time",
)
DATE_PHRASES = (
    "whats the date", "what is the date", "whats todays date", "what is todays date",
    "todays date", "date today", "what day is it", "what day is today",
)


def ends_with_any(text: str, phrases: tuple) -> bool:
    return any(text.endswith(phrase) for phrase in phrases)


def try_handle_time_date(user_input: str) -> str | None:
    text = simple_text(user_input)
    now = datetime.now()

    if ends_with_any(text, TIME_PHRASES):
        return f"It's {now.strftime('%I:%M %p').lstrip('0')}."

    if ends_with_any(text, DATE_PHRASES):
        return f"Today is {now:%A}, {now.day} {now:%B %Y}."

    return None