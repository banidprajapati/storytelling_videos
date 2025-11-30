"""
Pipeline service for orchestrating the complete video generation workflow
"""

from pathlib import Path
from typing import Optional

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.services.preprocess_text_service import add_pauses
from storytelling_videos.services.video_gen_service import VideoGeneration
from storytelling_videos.services.voice_kokoro_service import KokoroVoice
from storytelling_videos.services.whisperx_service import WhisperXSubtitleGenerator

logger = get_logger(__name__)


class VideoPipeline:
    """Orchestrates the complete video generation pipeline"""

    def __init__(self, script_uuid: str, script_content: str):
        """
        Initialize the video pipeline

        Args:
            script_uuid: Unique identifier for the script
            script_content: The text content of the script
        """
        self.script_uuid = script_uuid
        self.script_content = script_content
        self.parent_dir = Path.cwd()

    def generate_tts_and_srt(
        self, voice: str = "am_liam", model_name: str = "tiny", speed: float = 1
    ) -> dict:
        """
        Generate TTS audio and word-level subtitles

        Args:
            voice: Voice to use for TTS (default: am_liam)
            model_name: Whisper model for subtitles (default: tiny)
            speed: Speech speed (default: 1.0)

        Returns:
            Dictionary with paths to audio and SRT files
        """
        try:
            logger.info(f"[Pipeline] Step 1/3: Generating TTS for {self.script_uuid}")

            # Process and generate TTS
            script_processed = add_pauses(self.script_content)
            kokoro = KokoroVoice(
                script_uuid=self.script_uuid,
                text=script_processed,
                voice=voice,
                lang_code="a",
                speed=speed,
            )
            generator = kokoro.synthesize()
            audio_path = kokoro.save_audio(generator=generator)

            # Generate subtitles
            logger.info("[Pipeline] Step 2/3: Generating SRT subtitles")

            subtitle_generator = WhisperXSubtitleGenerator(
                script_uuid=self.script_uuid, model_name=model_name
            )
            srt_path = subtitle_generator.generate_word_level_srt()

            logger.info(f"[Pipeline] SRT subtitles saved: {srt_path}")

            return {
                "script_uuid": self.script_uuid,
                "audio_path": str(audio_path),
                "srt_path": str(srt_path),
                "status": "success",
            }

        except Exception as e:
            logger.error(f"[Pipeline] Error in TTS/SRT generation: {str(e)}")
            raise

    def generate_video(self, stock_video_path: Optional[str]) -> dict:
        """
        Generate final video with embedded subtitles

        Args:
            stock_video_path: Optional path to specific stock video

        Returns:
            Dictionary with path to generated video
        """
        try:
            logger.info("[Pipeline] Step 3/3: Generating video")

            video_gen = VideoGeneration(script_uuid=self.script_uuid)
            video_gen.generate(stock_video_path=stock_video_path)

            logger.info(f"[Pipeline] Video generated: {video_gen.output_path}")

            return {
                "video_path": str(video_gen.output_path),
                "status": "success",
            }

        except Exception as e:
            logger.error(f"[Pipeline] Error in video generation: {str(e)}")
            raise

    def run_complete_pipeline(
        self,
        voice: str = "am_liam",
        model_name: str = "tiny",
        speed: float = 1,
        stock_video_path: Optional[str] = None,
    ) -> dict:
        """
        Run the complete pipeline from TTS to final video

        Args:
            voice: Voice to use for TTS
            model_name: Whisper model for subtitles
            speed: Speech speed
            stock_video_path: Optional specific stock video

        Returns:
            Dictionary with all generated file paths and status
        """
        try:
            logger.info(f"[Pipeline] Starting complete pipeline for {self.script_uuid}")

            # Step 1 & 2: Generate TTS and SRT
            tts_srt_result = self.generate_tts_and_srt(
                voice=voice, model_name=model_name, speed=speed
            )

            # Step 3: Generate video
            video_result = self.generate_video(stock_video_path=stock_video_path)

            logger.info(
                f"[Pipeline] Complete pipeline finished successfully for {self.script_uuid}"
            )

            return {
                "status": "success",
                "script_uuid": self.script_uuid,
                "audio_path": tts_srt_result["audio_path"],
                "srt_path": tts_srt_result["srt_path"],
                "video_path": video_result["video_path"],
                "message": "Complete pipeline executed successfully",
            }

        except Exception as e:
            logger.error(f"[Pipeline] Complete pipeline failed: {str(e)}")
            raise
