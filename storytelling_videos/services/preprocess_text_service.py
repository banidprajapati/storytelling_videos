import re


# Remove URLs
def remove_links(text):
    return re.sub(r"https?://\S+|www\.\S+", "", text)


# Remove emojis and non-ASCII characters
def remove_emojis(text):
    return re.sub(r"[\U00010000-\U0010ffff]", "", text)


# Remove asterisks and other unwanted special characters
def remove_special_chars(text):
    return re.sub(r"[\*]", "", text)


# Main preprocessing function
def preprocess_text(text):
    text = remove_links(text)
    text = remove_emojis(text)
    text = remove_special_chars(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def add_pauses(text):
    # Replace single periods not preceded or followed by another period with ellipsis
    return re.sub(r"(?<!\.)\.(?!\.)", "...", text)
