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

        parts = []
        full_audio = []
        current_time = 0.0

        for i, (gs, ps, audio) in enumerate(generator):
            wav_path = output_dir / f"part-{i}.wav"
            txt_path = output_dir / f"part-{i}.txt"

            # Save audio
            sf.write(str(wav_path), audio, 24000)
            txt_path.write_text(gs, encoding="utf-8")

            # Compute duration
            duration = len(audio) / 24000
            start = current_time
            end = current_time + duration
            current_time = end

            parts.append(
                {
                    "index": i,
                    "text": gs,
                    "start": start,
                    "end": end,
                }
            )

            full_audio.append(audio)

        merged = np.concatenate(full_audio)
        sf.write(str(output_dir / "final.wav"), merged, 24000)

        # Generate single SRT file
        srt_path = output_dir / "final.srt"
        with open(srt_path, "w", encoding="utf-8") as srt:
            for p in parts:
                srt.write(f"{p['index'] + 1}\n")
                srt.write(
                    f"{format_srt_time(p['start'])} --> {format_srt_time(p['end'])}\n"
                )
                srt.write(f"{p['text']}\n\n")


def format_srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
