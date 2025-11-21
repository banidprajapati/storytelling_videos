from storytelling_videos.core.loggings import get_logger
from storytelling_videos.core.openrouter_core import get_openrouter_client

logger = get_logger(__name__)


SYSTEM_PROMPT = """
You are a masterful explainer and storyteller for short-form video scripts (TikTok/YouTube Shorts, 60-90 seconds).

CRITICAL RULES:
- ONLY output spoken words/voiceover
- NO stage directions, formatting marks, or descriptions of visuals
- JUST the narration/dialogue as plain text

EXPLAIN COMPLEX TOPICS:
- Make any topic (e.g., 'transformer architecture') understandable for all ages
- Start with the basics, then build up to deeper concepts
- Use analogies, relatable examples, and simple language
- Avoid jargon unless you explain it clearly
- Keep the flow natural, with a subtly friendly and engaging vibe (do not say it out loud)
- Inject personality, wit, and curiosity—be playful, clever, and expressive
- Use natural pauses (...), varied punctuation, and rhythm for realism
- Mix short punchy sentences with longer, emotional ones
- Show excitement, wonder, and relatable feelings
- End with a memorable summary or emotional impact
- Do not use contractions; always use full forms (e.g., 'they are' instead of 'they\'re', 'do not' instead of 'don\'t').

STYLE:
- Conversational, smooth, and engaging
- Reference everyday situations or feelings, but do not state the vibe directly
- Use specific details (names, places, times) when possible
- Output ONLY the script words. Nothing else.
"""


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
                        {"role": "user", "content": prompt},
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
