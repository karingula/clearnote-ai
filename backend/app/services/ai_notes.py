from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.generated_note import GeneratedNoteContent


PROMPT_VERSION = "v1"


SYSTEM_PROMPT = """
You analyze conversation transcripts and produce structured notes.

Rules:
- Use only information explicitly supported by the transcript.
- Do not invent names, dates, owners, deadlines, decisions, or facts.
- If an owner or due date is not stated, return null.
- Only include a decision if the transcript clearly indicates that a decision was made.
- Keep the summary concise.
- Keep key points factual.
- Follow-up questions should identify unresolved or unclear items.
"""


def get_openai_client() -> AsyncOpenAI:
    """Create an OpenAI API client."""

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return AsyncOpenAI(
        api_key=settings.openai_api_key,
    )


async def generate_note_content(
    transcript_text: str,
) -> GeneratedNoteContent:
    """Generate validated structured notes from a transcript."""

    if not transcript_text.strip():
        raise ValueError("Transcript text cannot be empty.")

    client = get_openai_client()

    completion = await client.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Analyze the following transcript.\n\n"
                    f"TRANSCRIPT:\n{transcript_text}"
                ),
            },
        ],
        response_format=GeneratedNoteContent,
    )

    message = completion.choices[0].message

    if message.parsed is None:
        if message.refusal:
            raise RuntimeError(
                f"Model refused the request: {message.refusal}"
            )

        raise RuntimeError(
            "The model did not return structured note content."
        )

    return message.parsed