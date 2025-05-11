from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Body
import google.genai as genai
from google.genai import types

# Local imports
from config import settings, logger
from models import PromptRequest, GenerateResponse, ErrorDetail
from ai_helpers import build_veritas_chat_contents

# Initialize SDK client
if not settings.google_ai_api_key:
    logger.critical("Google AI API key is not set in settings.")
client = genai.Client(api_key=settings.google_ai_api_key)

# Initialize FastAPI app
app = FastAPI(
    title="Veritas AI Chatbot API (google-genai)",
    description="API to interact with a Gemini model using Veritas University context.",
    version="1.0.1",
)

# Path to the Veritas data file
VERITAS_DATA_PATH = Path(settings.absolute_veritas_data_path)

@app.post(
    "/generate/",
    response_model=GenerateResponse,
    summary="Generate Text using Veritas Context (google-genai)",
    description="Processes a prompt using Google's Gemini model via the google-genai SDK.",
    responses={
        400: {"model": ErrorDetail, "description": "Bad Request (invalid input or blocked)"},
        404: {"model": ErrorDetail, "description": "Data file not found"},
        500: {"model": ErrorDetail, "description": "Internal Server Error"},
        503: {"model": ErrorDetail, "description": "Service Unavailable"},
    },
)
async def generate_text(request_data: PromptRequest = Body(...)):
    # Ensure data file present
    if not VERITAS_DATA_PATH.exists():
        logger.error(f"Veritas data file not found at {VERITAS_DATA_PATH}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Required data file not found on the server.",
        )

    # Validate prompt
    prompt = (request_data.prompt or "").strip()
    if not prompt:
        logger.warning("Empty prompt received.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt is required in the request body.",
        )

    model_name = request_data.model or settings.veritas_ai_model
    logger.info(f"Processing prompt for model: {model_name}")

    try:
        # Build context contents list
        contents = build_veritas_chat_contents(
            client=client, file_path=VERITAS_DATA_PATH, prompt=prompt
        )
        # expects List[types.Content]

        # Prepend instruction as user message instead of system message
        instruction_content = types.Content(
            parts=[
                types.Part.from_text(
                    text=(
                        "You are an AI chatbot for Veritas University Abuja. "
                        "Answer respectfully and accurately based on the provided document. "
                        "If the answer isn't in the document, state that you don't have that information."
                    )
                )
            ],
            role="user",
        )

        # Add model response acknowledging the instruction
        acknowledgment_content = types.Content(
            parts=[
                types.Part.from_text(
                    text="I understand. I'll act as a Veritas University Abuja chatbot, answering questions respectfully and accurately based on the provided information."
                )
            ],
            role="model",
        )

        # Ensure contents is a list before concatenating
        contents_list = contents if contents is not None else []
        messages = [instruction_content, acknowledgment_content] + contents_list + [
            types.Content(parts=[types.Part.from_text(text=prompt)], role="user")
        ]

        # Stream generation
        stream = client.models.generate_content_stream(
            model=model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                temperature=request_data.temperature or 0.9,
                top_p=request_data.top_p or 0.95,
                top_k=request_data.top_k or 64,
                max_output_tokens=request_data.max_output_tokens or 8192,
                response_mime_type="text/plain",
            ),
        )

        # Collect response text
        response_text = ""
        for chunk in stream:
            if hasattr(chunk, "prompt_feedback") and chunk.prompt_feedback:
                if hasattr(chunk.prompt_feedback, "block_reason"):
                    reason = chunk.prompt_feedback.block_reason
                    logger.warning(f"Prompt blocked during generation: {reason}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Request blocked by API: {reason}",
                    )
            response_text += getattr(chunk, "text", "")

        logger.info(f"Successfully generated response from model {model_name}.")
        return GenerateResponse(response=response_text.strip(), model=model_name)

    except HTTPException:
        raise
    except ImportError as e:
        logger.critical(f"GenAI SDK import error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server configuration error: {e}",
        )
    except Exception as e:
        if hasattr(e, "__class__") and e.__class__.__name__ == "GoogleAPICallError":
            logger.exception(f"Google API Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error communicating with the AI service: {e}",
            )
        else:
            logger.exception(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal server error occurred.",
            )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
