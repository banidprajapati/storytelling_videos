"""
Service for generating word-level subtitles using OpenAI Whisper
"""

from pathlib import Path
from typing import Optional


class WhisperSubtitleGenerator:
    """Generate word-level SRT subtitles from audio using Whisper"""

    def __init__(self, audio_path: str):
        """
        Initialize Whisper subtitle generator

        Args:
            audio_path: Path to audio file
        """
        try:
            import whisper
        except ImportError:
            raise ImportError(
                "whisper is not installed. Install with: pip install openai-whisper"
            )

        self.whisper = whisper
        self.audio_path = str(audio_path)
        self.model = None

    def transcribe(self, model_name: str = "tiny"):
        """
        Transcribe audio and get word-level timestamps

        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)

        Returns:
            Transcription result with word-level timestamps
        """
        print(f"Loading Whisper model: {model_name}")
        self.model = self.whisper.load_model(model_name)

        print(f"Transcribing audio: {self.audio_path}")
        result: dict = self.model.transcribe(
            self.audio_path, language="en", verbose=False
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

    def generate_word_level_srt(
        self, output_path: Optional[str] = None, model_name: str = "tiny"
    ) -> str:
        """
        Generate word-level SRT file from audio

        Args:
            output_path: Path to save SRT file. If None, saves next to audio file.
            model_name: Whisper model to use

        Returns:
            Path to generated SRT file
        """
        if output_path is None:
            audio_path = Path(self.audio_path)
            output_path = str(audio_path.parent / f"{audio_path.stem}_words.srt")

        # Transcribe with word-level timestamps
        result = self.transcribe(model_name)

        # Extract word-level timing from segments
        srt_content = []
        subtitle_index = 1

        for segment in result.get("segments", []):  # type: ignore
            # Check if segment has word-level details
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
                # Fallback: If word-level timing not available, create one subtitle per segment
                word: str = segment.get("text", "").strip()  # type: ignore
                start: float = float(segment.get("start", 0))  # type: ignore
                end: float = float(segment.get("end", 0))  # type: ignore

                if word:
                    start_time = self.format_timestamp(start)
                    end_time = self.format_timestamp(end)

                    srt_line = (
                        f"{subtitle_index}\n{start_time} --> {end_time}\n{word}\n"
                    )
                    srt_content.append(srt_line)
                    subtitle_index += 1

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_content))

        print(f"Word-level SRT file generated: {output_path}")
        return output_path


if __name__ == "__main__":
    # Test script
    script_uuid = "be7036b5-075e-4d9a-96f0-7a52d6dca906"
    parent_dir = Path.cwd()
    audio_path = parent_dir / "saved_audio_kokoro" / script_uuid / "final.wav"
    output_srt = parent_dir / "saved_audio_kokoro" / script_uuid / "final_words.srt"

    generator = WhisperSubtitleGenerator(str(audio_path))
    srt_path = generator.generate_word_level_srt(str(output_srt), model_name="tiny")
    print(f"Generated SRT at: {srt_path}")
