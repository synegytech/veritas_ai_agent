# models.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class PromptRequest(BaseModel):
    """
    Pydantic model for the prompt input request body.
    Corresponds to PromptSerializer.
    """

    prompt: str = Field(..., description="The text prompt to send to the AI model")
    model: Optional[str] = Field(
        None, description="The Gemini model to use (defaults to config)"
    )
    temperature: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Controls randomness in output (0.0 to 1.0)"
    )
    top_p: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Nucleus sampling parameter (0.0 to 1.0)"
    )
    top_k: Optional[int] = Field(
        None,
        ge=1,
        description="Top-k sampling parameter",  # Added top_k from view logic
    )
    max_output_tokens: Optional[int] = Field(
        None, ge=1, description="Maximum number of tokens to generate"
    )

    # Allow extra fields if needed, though usually better to be explicit
    model_config = ConfigDict(extra="ignore")


class GenerateResponse(BaseModel):
    """
    Pydantic model for the AI response output.
    Corresponds to ResponseSerializer.
    """

    response: str = Field(
        ..., description="The generated text response from the AI model"
    )
    model: str = Field(..., description="The model used to generate the response")
    # Usage metadata is often not directly available from the streaming response chunks
    # prompt_tokens: Optional[int] = Field(None, description="Number of tokens in the prompt")
    # completion_tokens: Optional[int] = Field(None, description="Number of tokens in the completion")
    # total_tokens: Optional[int] = Field(None, description="Total number of tokens used")

    model_config = ConfigDict(extra="ignore")


class ErrorDetail(BaseModel):
    """Pydantic model for error details."""

    detail: str
    error_code: Optional[str] = None  # Optional error code if needed


class BlockedPromptDetail(BaseModel):
    """Pydantic model for blocked prompt errors."""

    detail: str
    reason: str
