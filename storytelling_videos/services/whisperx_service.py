"""
Service for generating word-level subtitles using WhisperX
"""

from pathlib import Path
from typing import Optional

import whisperx


class WhisperXSubtitleGenerator:
    """Generate word-level SRT subtitles from audio using WhisperX"""

    _model = None
    _align_model = None

    def __init__(self, audio_path: str, model_name: str = "tiny"):
        """
        Initialize WhisperX subtitle generator

        Args:
            audio_path: Path to audio file
            model_name: Model to use (tiny, base, small, medium, large)
        """
        self.audio_path = str(audio_path)
        self.model_name = model_name
        # Try CUDA first, fall back to CPU if unavailable
        self.device = "cpu"  # Use CPU to avoid CUDA/cuDNN compatibility issues
        self.compute_type = "int8"  # Use int8 for CPU compatibility

    def _load_models(self):
        """Load WhisperX model and alignment model"""
        if WhisperXSubtitleGenerator._model is None:
            print(f"Loading WhisperX model: {self.model_name}")
            WhisperXSubtitleGenerator._model = whisperx.load_model(
                self.model_name, self.device, compute_type=self.compute_type
            )
            print("Loading alignment model...")
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
        self._load_models()

        print(f"Transcribing: {self.audio_path}")
        result = WhisperXSubtitleGenerator._model.transcribe(
            self.audio_path, language="en", batch_size=16
        )

        print("Aligning timestamps...")
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

    def generate_word_level_srt(self, output_path: Optional[str] = None) -> str:
        """
        Generate word-level SRT file from audio

        Args:
            output_path: Path to save SRT file. If None, saves next to audio file.

        Returns:
            Path to generated SRT file
        """
        if output_path is None:
            audio_path = Path(self.audio_path)
            output_path = str(audio_path.parent / f"{audio_path.stem}_words.srt")

        # Transcribe with word-level timestamps
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
            else:
                # Fallback: split segment into words
                text: str = segment.get("text", "").strip()  # type: ignore
                start: float = float(segment.get("start", 0))  # type: ignore
                end: float = float(segment.get("end", 0))  # type: ignore

                if text:
                    words = text.split()
                    if len(words) > 0:
                        word_duration = (end - start) / len(words)
                        current_time = start

                        for word in words:
                            word = word.strip()
                            if word:
                                start_time = self.format_timestamp(current_time)
                                end_time = self.format_timestamp(
                                    current_time + word_duration
                                )

                                srt_line = f"{subtitle_index}\n{start_time} --> {end_time}\n{word}\n"
                                srt_content.append(srt_line)
                                subtitle_index += 1
                                current_time += word_duration

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_content))

        print(f"SRT file saved to: {output_path}")
        return output_path


if __name__ == "__main__":
    script_uuid = "cc87e1fc-aa62-4a3e-9fee-ce72df78c6e6"
    parent_dir = Path.cwd()
    audio_path = parent_dir / "saved_audio_kokoro" / script_uuid / "final.wav"
    output_srt = parent_dir / "saved_audio_kokoro" / script_uuid / "final_words.srt"

    generator = WhisperXSubtitleGenerator(str(audio_path), model_name="tiny")
    generator.generate_word_level_srt(str(output_srt))
