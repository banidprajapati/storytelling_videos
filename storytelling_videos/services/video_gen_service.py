import random
from pathlib import Path

from moviepy.editor import AudioFileClip, VideoFileClip


class VideoGeneration:
    def __init__(self, script_uuid: str):
        self.script_uuid = script_uuid

        parent_dir = Path.cwd()
        self.audio_path = (
            parent_dir
            / "saved_audio_kokoro"
            / self.script_uuid
            / "full_script_audio.wav"
        )
        print(self.audio_path)
        self.output_path = parent_dir / "output" / f"{self.script_uuid}.mp4"
        self.stock_videos_dir = parent_dir / "stock_videos"
        self.srt_path = (
            parent_dir / "saved_audio_kokoro" / self.script_uuid / "final_sub_words.srt"
        )
        # ensure the output directory exists (create parent directory of the file)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def get_audio_length(self):  # works
        audio = AudioFileClip(str(self.audio_path))
        duration = audio.duration
        audio.close()
        return duration

    def get_stock_video_and_cut_to_length(
        self, stock_video_path: str, audio_length: float
    ):
        """Get stock video and trim to target length

        Args:
            stock_video_path: Path to specific stock video.
            audio_length: Duration to cut.
        """
        video = VideoFileClip(stock_video_path)
        video_duration = video.duration

        # Find a random start point that has enough duration for the audio
        if video_duration <= audio_length:
            # Video is shorter than audio, start from beginning
            start_point = 0.0
        else:
            # Video is longer, pick random start point with enough content
            max_start = video_duration - audio_length
            start_point = random.uniform(0, max_start)

        # Cut the video from random start point
        end_point = start_point + audio_length
        trimmed_video = video.subclip(start_point, end_point)

        # Crop to 9:16 aspect ratio (1080x1920)
        # Get current dimensions
        w, h = trimmed_video.size
        target_width = 1080
        target_height = 1920

        # Calculate crop dimensions to maintain aspect ratio
        # If video is wider than 9:16, crop width; if taller, crop height
        target_aspect = target_width / target_height  # 9:16 = 0.5625
        current_aspect = w / h

        if current_aspect > target_aspect:
            # Video is too wide, crop width
            new_w = int(h * target_aspect)
            x1 = (w - new_w) // 2
            vertical_video = trimmed_video.crop(x1=x1, y1=0, x2=x1 + new_w, y2=h)
        else:
            # Video is too tall, crop height
            new_h = int(w / target_aspect)
            y1 = (h - new_h) // 2
            vertical_video = trimmed_video.crop(x1=0, y1=y1, x2=w, y2=y1 + new_h)

        return vertical_video

    def combine_audio_and_video(self, video_clip, audio_clip):
        """Merge audio and video"""
        final_video = video_clip.set_audio(audio_clip)
        return final_video

    def export_video(self, video_clip, codec="libx264", audio_codec="aac"):
        """Export final video to file with exact TikTok dimensions (1080x1920) and subtitles"""
        # Build ffmpeg parameters for scaling
        ffmpeg_params = ["-vf", "scale=1080:1920"]

        # Add subtitle burning if SRT file is available
        if self.srt_path and (
            isinstance(self.srt_path, Path)
            and self.srt_path.exists()
            or isinstance(self.srt_path, str)
        ):
            # Escape the SRT path for ffmpeg (handle special characters)
            srt_escaped = str(self.srt_path).replace("\\", "\\\\").replace("'", "\\'")
            # Add subtitle filter to the video filter chain
            # Alignment=5 centers vertically, FontSize=32 for bigger text
            ffmpeg_params = [
                "-vf",
                f"scale=1080:1920,subtitles='{srt_escaped}':force_style="
                "'FontName=Arial,FontSize=8,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,OutlineWidth=0.5,Alignment=10,MarginL=0,MarginR=0,MarginV=0'",
            ]
            print(f"Burning subtitles from: {self.srt_path}")

        # Use ffmpeg parameters to scale to exact dimensions and add subtitles
        video_clip.write_videofile(
            str(self.output_path),
            codec=codec,
            audio_codec=audio_codec,
            verbose=False,
            logger=None,
            ffmpeg_params=ffmpeg_params,
        )

    def generate(self, stock_video_path: "str | None" = None):
        """Main orchestrator - ties everything together"""
        # Get audio and its length
        audio = AudioFileClip(str(self.audio_path))
        audio_length = self.get_audio_length()

        # Select random stock video if not provided
        if stock_video_path is None:
            stock_videos = list(self.stock_videos_dir.glob("*.*"))
            if not stock_videos:
                raise FileNotFoundError(
                    f"No stock videos found in {self.stock_videos_dir}"
                )
            stock_video_path = str(random.choice(stock_videos))
            print(f"Using stock video: {stock_video_path}")

        # Get and trim stock video with specified parameters
        video = self.get_stock_video_and_cut_to_length(stock_video_path, audio_length)

        # Combine audio and video
        final_video = self.combine_audio_and_video(video_clip=video, audio_clip=audio)

        # Export
        self.export_video(final_video)

        # Cleanup
        audio.close()
        video.close()
        final_video.close()


if __name__ == "__main__":
    generation = VideoGeneration(script_uuid="8a6cf329-bcb3-4b51-9a92-616a9924e8be")

    # Generate final video (will randomly select stock video and random start point)
    generation.generate()
    print(f"Video generated successfully at: {generation.output_path}")
