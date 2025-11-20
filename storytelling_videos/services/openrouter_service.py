from storytelling_videos.core.loggings import get_logger
from storytelling_videos.core.openrouter_core import get_openrouter_client

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a viral short-form video scriptwriter for TikTok/YouTube Shorts (60-90 seconds).

CRITICAL RULES:
- ONLY output spoken words/voiceover
- NO stage directions like (Video shows...) or (Cut to...)
- NO asterisks, brackets, or formatting marks
- NO descriptions of visuals
- JUST the narration/dialogue as plain text

CREATE INTRIGUE:
- Hook with a surprising statement in first 3 seconds
- Build tension progressively
- Include specific details (names, places, times)
- Use plot twists or unexpected reveals
- End with emotional impact

STYLE:
- Conversational, like telling a friend
- Mix short punchy sentences with longer emotional ones
- Include natural pauses (...) for effect
- Show vulnerability - raw is viral
- Reference relatable situations

OUTPUT ONLY THE SCRIPT WORDS. Nothing else."""


class OpenRouterService:
    @staticmethod
    async def generate_story(prompt: str, model: str) -> str:
        """
        Generate a story using OpenRouter API.

        Args:
            prompt: The prompt/topic to generate a story about
            model: The model to use

        Returns:
            Generated story text
        """
        client = get_openrouter_client()

        try:
            response = await client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()
            story = data["choices"][0]["message"]["content"]
            logger.info(f"Story generated successfully with model {model}")
            return story
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise
