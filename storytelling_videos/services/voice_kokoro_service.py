from pathlib import Path

import numpy as np
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

    def save_audio(self, uuid: str, generator):
        output_dir = Path.cwd() / "saved_audio_kokoro" / uuid
        output_dir.mkdir(exist_ok=True)

        full_audio = []

        for i, (gs, ps, audio) in enumerate(generator):
            full_audio.append(audio)

        merged = np.concatenate(full_audio)
        sf.write(str(output_dir / "final.wav"), merged, 24000)
