from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActionItem(BaseModel):
    task: str = Field(..., description="The task to be completed.")
    owner: str | None = Field(None, description="The owner of the task.")
    due_date: date | None = Field(None, description="The due date for the task completion.")

class GeneratedNoteContent(BaseModel):
    summary: str = Field(..., description="A concise summary of the transcript.")
    decisions: list[str] = Field(default_factory=list, description="A list of decisions made during the meeting.")
    action_items: list[ActionItem] = Field(default_factory=list, description="A list of action items with details.")
    key_points: list[str] = Field(default_factory=list, description="A list of key points discussed in the meeting.")
    follow_up_questions: list[str] = Field(default_factory=list, description="A list of follow-up questions for further discussion.")

class GeneratedNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="The unique identifier of the generated note.")
    transcript_id: UUID = Field(..., description="The unique identifier of the associated transcript.")
    summary: str = Field(..., description="A concise summary of the transcript.")
    decisions: list[str] = Field(default_factory=list, description="A list of decisions made during the meeting.")
    action_items: list[ActionItem] = Field(default_factory=list, description="A list of action items with details.")
    key_points: list[str] = Field(default_factory=list, description="A list of key points discussed in the meeting.")
    follow_up_questions: list[str] = Field(default_factory=list, description="A list of follow-up questions for further discussion.")
    model_name: str = Field(..., description="The name of the model used to generate the note.")
    prompt_version: str = Field(..., description="The version of the prompt used for generating the note.")
    created_at: datetime = Field(..., description="The timestamp when the generated note was created.")