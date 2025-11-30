from pathlib import Path

import soundfile as sf
import torch  # noqa: F401
from kokoro import KPipeline

from storytelling_videos.core.loggings import get_logger

logger = get_logger(__name__)


class KokoroVoice:
    _pipeline = None  # Class variable for lazy initialization
    _device = None

    def __init__(
        self,
        script_uuid: str,
        text: str,
        voice: str = "am_liam",
        lang_code: str = "a",
        speed: float = 1,
    ):
        self.text = text
        self.voice = voice
        self.lang_code = lang_code
        self.speed = speed
        self.output_dir = Path.cwd() / "saved_audio_kokoro" / script_uuid
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.output_path = self.output_dir / "full_script_audio.wav"
        self.device = self._get_device()

    @staticmethod
    def _get_device():
        """Determine best device (cuda or cpu)"""
        if KokoroVoice._device is None:
            if torch.cuda.is_available():
                logger.info("CUDA available - using GPU for TTS")
                KokoroVoice._device = "cuda"
            else:
                logger.warning("CUDA not available - using CPU for TTS")
                KokoroVoice._device = "cpu"
        return KokoroVoice._device

    def get_pipeline(self):
        # lazy initialize a single shared pipeline for the class
        if KokoroVoice._pipeline is None:
            KokoroVoice._pipeline = KPipeline(
                lang_code=self.lang_code, device=self.device
            )
        return KokoroVoice._pipeline

    def synthesize(self):
        if self.output_path.exists():
            logger.info("Audio file already exists.")
            return None

        pipeline = self.get_pipeline()
        return pipeline(
            self.text, voice=self.voice, speed=self.speed, split_pattern=r"\n+"
        )

    def save_audio(self, generator):
        if generator is None:
            logger.info("Skipping save_audio - file already exists")
            return self.output_path

        with sf.SoundFile(
            self.output_path, mode="w", samplerate=24000, channels=1
        ) as f:
            for _, _, audio in generator:
                f.write(audio)

        return self.output_path
