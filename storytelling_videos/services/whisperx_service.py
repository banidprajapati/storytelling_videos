"""
Service for generating word-level subtitles using WhisperX
"""

from pathlib import Path

import whisperx

from storytelling_videos.core.loggings import get_logger

logger = get_logger(__name__)


class WhisperXSubtitleGenerator:
    """Generate word-level SRT subtitles from audio using WhisperX"""

    _model = None
    _align_model = None

    def __init__(self, script_uuid: str, model_name: str = "tiny"):
        """
        Initialize WhisperX subtitle generator

        Args:
            audio_path: Path to audio file
            model_name: Model to use (tiny, base, small, medium, large)
        """
        parent_dir = Path.cwd()
        audio_path = (
            parent_dir / "saved_audio_kokoro" / script_uuid / "full_script_audio.wav"
        )
        output_srt_path = (
            parent_dir / "saved_audio_kokoro" / script_uuid / "full_sub_words.srt"
        )
        self.audio_path = str(audio_path)
        self.model_name = model_name
        self.output_srt_path = output_srt_path
        # Try CUDA first, fall back to CPU if unavailable
        self.device = "cpu"
        self.compute_type = "int8"
        self._load_models()

    def _load_models(self):
        """Load WhisperX model and alignment model"""
        if WhisperXSubtitleGenerator._model is None:
            logger.info(f"Loading WhisperX model: {self.model_name}")
            WhisperXSubtitleGenerator._model = whisperx.load_model(
                self.model_name, self.device, compute_type=self.compute_type
            )

            logger.info("Loading alignment model...")
            align_model, metadata = whisperx.load_align_model(
                language_code="en", device=self.device
            )

            WhisperXSubtitleGenerator._align_model = (align_model, metadata)

    def transcribe(self) -> dict:
        """
        Transcribe audio and get word-level timestamps using WhisperX

        Returns:
            Transcription result with word-level timestamps
        """

        result = WhisperXSubtitleGenerator._model.transcribe(
            self.audio_path, language="en", batch_size=16
        )

        align_model, metadata = WhisperXSubtitleGenerator._align_model
        result = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            self.audio_path,
            self.device,
            return_char_alignments=False,
        )

        return result

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Format timestamp in SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def generate_word_level_srt(self) -> Path:
        """
        Generate word-level SRT file from audio

        Returns:
            Path to generated SRT file
        """
        output_file = Path(self.output_srt_path)

        # Skip if SRT already exists
        if output_file.exists():
            logger.info(f"SRT file already exists: {self.output_srt_path}")
            return output_file

        logger.info("Transcribing audio with WhisperX...")
        result = self.transcribe()

        # Extract word-level timing from segments
        srt_content = []
        subtitle_index = 1

        for segment in result.get("segments", []):  # type: ignore
            # WhisperX provides word-level details in the "words" field
            if "words" in segment:  # type: ignore
                words_list = segment.get("words", [])  # type: ignore
                for word_info in words_list:
                    word: str = word_info.get("word", "").strip()  # type: ignore
                    start: float = float(word_info.get("start", 0))  # type: ignore
                    end: float = float(word_info.get("end", 0))  # type: ignore

                    if word:  # Skip empty words
                        start_time = self.format_timestamp(start)
                        end_time = self.format_timestamp(end)

                        srt_line = (
                            f"{subtitle_index}\n{start_time} --> {end_time}\n{word}\n"
                        )
                        srt_content.append(srt_line)
                        subtitle_index += 1

        # Write to file
        output_file = Path(self.output_srt_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_content))

        print(f"SRT file saved to: {self.output_srt_path}")
        return self.output_srt_path
