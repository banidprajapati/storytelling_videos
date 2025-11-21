from pathlib import Path

import soundfile as sf
import torch  # noqa: F401
from kokoro import KPipeline


class KokoroVoice:
    _pipeline = None  # Class variable for lazy initialization

    def __init__(
        self,
        text: str,
        voice: str = "am_liam",
        lang_code: str = "a",
        speed: float = 1,
    ):
        self.text = text
        self.voice = voice
        self.lang_code = lang_code
        self.speed = speed

    def get_pipeline(self, lang_code=None):
        # lazy initialize a single shared pipeline for the class
        if self._pipeline is None:
            self._pipeline = KPipeline(lang_code=self.lang_code)
        return self._pipeline

    def synthesize(self):
        pipeline = self.get_pipeline(self.lang_code)
        return pipeline(
            self.text, voice=self.voice, speed=self.speed, split_pattern=r"\n+"
        )


# example input text (ensure 'text' is defined before creating Kokoro)
text = """Ever wonder how AI like ChatGPT reads your wildest questions and spits out genius answers? It's all thanks to the Transformer architecture... a total game-changer in AI.

Picture the old way computers handled language: like a kid reading a book, word by word, left to right. Slow, forgetful, missing the big picture. Transformers? They devour the entire sentence at once. Magic sauce? Attention.

Self-attention is like your brain in a noisy party. It scans every word, figures out which ones matter most right now. "Bank" could mean money... or a river. Attention weighs the context—boom, it knows!

They amp it up with multi-head attention: imagine seven detectives, each spotting different clues simultaneously. Faster, smarter connections.

No built-in order? Positional encoding sprinkles in word positions, like invisible GPS tags.

Stack encoders to understand input... decoders to craft replies. Layers upon layers, training on billions of words.

Transformers birthed GPT, translation wizards, image generators. They're why AI feels alive. Mind blown? Yeah... the future's paying attention."""
output_dir = Path.cwd() / "saved_audio_kokoro"
output_dir.mkdir(exist_ok=True)

kokoro = KokoroVoice(text=text, voice="am_liam", lang_code="a", speed=1)
generator = kokoro.synthesize()

for i, (gs, ps, audio) in enumerate(generator):
    sf.write(str(output_dir / f"{i}.wav"), audio, 24000)
