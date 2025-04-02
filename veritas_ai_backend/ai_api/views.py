# Create your views here.
"""
Views for the AI API application.
"""
# views.py

import logging
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from google import genai
from google.genai import types

# Local imports
from .serializers import PromptSerializer, ResponseSerializer
from .ai_helpers import build_veritas_chat_contents  # <-- Import the helper function

# Configure logging
logger = logging.getLogger(__name__)

# Path to the Veritas data file - update this to the actual path on your server
VERITAS_DATA_FILE_PATH = os.path.join(
    settings.BASE_DIR, "veritas_data", "Veritas_data.pdf"
)


class GenerateTextView(APIView):
    """
    API endpoint that uses Google AI Studio's Gemini models to generate text.
    Uses a pre-loaded Veritas University data file and processes user prompts.
    """

    parser_classes = (JSONParser,)

    def post(self, request):
        """
        Process a prompt with the Veritas data and return AI-generated text.

        Request body:
            {
                "prompt": "Text prompt to send to the AI model",
                "model": "gemini-pro" (optional - use setting default),
                "temperature": 1.0 (optional),
                "top_p": 0.95 (optional),
                "top_k": 64 (optional),
                "max_output_tokens": 8192 (optional)
            }
        """
        # Validate input data
        serializer = PromptSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid input received: {serializer.errors}")
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get prompt from validated data
        prompt = serializer.validated_data.get("prompt", "")
        if not prompt:
            logger.warning("Request received with empty prompt.")
            return Response(
                {"error": "Prompt is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model_name = serializer.validated_data.get(
            "model",
            settings.VERITAS_AI_MODEL,  # Ensure this setting exists
        )
        logger.info(f"Processing prompt for model: {model_name}")

        # Check if API key is configured
        api_key = settings.GOOGLE_AI_API_KEY  # Ensure this setting exists
        if not api_key:
            logger.error("Google AI API key is not configured in settings.")
            return Response(
                {"error": "Google AI API key is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Check if the Veritas data file exists *before* attempting complex logic
        # Note: The helper function also checks, providing redundancy.
        if not os.path.exists(VERITAS_DATA_FILE_PATH):
            logger.error(f"Veritas data file not found at {VERITAS_DATA_FILE_PATH}")
            return Response(
                {"error": "Required data file not found on the server."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Configure the client with API key
            client = genai.Client(api_key=api_key)

            # --- Use the helper function to build contents ---
            contents = build_veritas_chat_contents(
                client=client, file_path=VERITAS_DATA_FILE_PATH, prompt=prompt
            )

            # The helper function now handles fallback, so contents should always be a list.
            # A check for None could be added if the helper might return it on critical failure.
            # if contents is None:
            #     logger.error("Failed to build chat contents critically.")
            #     return Response(
            #         {"error": "Failed to prepare data for AI model."},
            #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #     )

            # Configuration for generation
            # Keep system instruction here as it's part of the generation config, not the history
            system_instruction = [
                types.Part.from_text(
                    text="You are An AI chatbot for Veritas University Abuja. You will answer questions respectfully and give accurate answers based primarily on the provided document and context. If the answer isn't in the document or context, state that you don't have that specific information."
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=serializer.validated_data.get(
                    "temperature", 0.9
                ),  # Adjusted default temp
                top_p=serializer.validated_data.get("top_p", 0.95),
                top_k=serializer.validated_data.get("top_k", 64),
                max_output_tokens=serializer.validated_data.get(
                    "max_output_tokens", 8192
                ),
                response_mime_type="text/plain",
                # system_instruction=system_instruction # Use if model supports it correctly
            )

            logger.info(
                f"Sending request to Gemini model '{model_name}' with {len(contents)} content parts."
            )
            # Generate content - Pass system instruction if applicable/desired
            # Note: System Instruction placement depends on the exact model and API version.
            # Sometimes it's part of GenerateContentConfig, sometimes prepended to 'contents'.
            # Check the genai library documentation for your specific model.
            # For now, assuming it's in the config:
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=generate_content_config,
                # If system_instruction should be part of contents:
                # contents=[types.Content(parts=system_instruction, role='system')] + contents
            )

            response_text = ""
            for chunk in response_stream:
                # Add basic error handling for chunks if needed (e.g., chunk.prompt_feedback)
                try:
                    response_text += chunk.text
                except ValueError:
                    logger.warning(
                        f"Received chunk without text, possibly finish reason: {chunk.candidates[0].finish_reason}"
                    )
                except Exception as chunk_err:
                    logger.error(f"Error processing chunk: {chunk_err}")

            # Prepare output data
            output_data = {"response": response_text.strip(), "model": model_name}
            logger.info(f"Successfully generated response from model {model_name}.")

            # Serialize and return the response
            response_serializer = ResponseSerializer(output_data)
            return Response(response_serializer.data)

        except ImportError as e:
            logger.critical(f"Failed to import required libraries: {str(e)}")
            return Response(
                {
                    "error": f"Server configuration error: Required libraries are not installed: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except types.generation_types.BlockedPromptException as e:
            logger.warning(f"Prompt blocked by API: {e}")
            return Response(
                {"error": "Request blocked due to safety concerns.", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred calling Google AI API: {str(e)}"
            )  # Use exception for traceback
            return Response(
                {"error": f"Error communicating with the AI service."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,  # Use 503 for external service issues
            )
