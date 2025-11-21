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


# Example usage
if __name__ == "__main__":
    sample = """Ever wonder how AI like ChatGPT reads your wildest questions and spits out genius answers? It's all thanks to the Transformer architecture... a total game-changer in AI.\n\nPicture the old way computers handled language: like a kid reading a book, word by word, left to right. Slow, forgetful, missing the big picture. Transformers? They devour the entire sentence at once. Magic sauce? Attention.\n\nSelf-attention is like your brain in a noisy party. It scans every word, figures out which ones matter most right now. \"Bank\" could mean money... or a river. Attention weighs the context—boom, it knows!\n\nThey amp it up with multi-head attention: imagine seven detectives, each spotting different clues simultaneously. Faster, smarter connections.\n\nNo built-in order? Positional encoding sprinkles in word positions, like invisible GPS tags.\n\nStack encoders to understand input... decoders to craft replies. Layers upon layers, training on billions of words.\n\nTransformers birthed GPT, translation wizards, image generators. They're why AI feels alive. Mind blown? Yeah... the future's paying attention."""
    print(preprocess_text(sample))
