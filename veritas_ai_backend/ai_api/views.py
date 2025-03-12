# Create your views here.
"""
Views for the AI API application.
"""

import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PromptSerializer, ResponseSerializer

# Configure logging
logger = logging.getLogger(__name__)


class GenerateTextView(APIView):
    """
    API endpoint that uses Google AI Studio's Gemini models to generate text.
    """

    def post(self, request):
        """
        Process a prompt and return AI-generated text.

        Request body:
            {
                "prompt": "Text prompt to send to the AI model",
                "model": "gemini-2.0-flash" (optional),
                "temperature": 0.7 (optional),
                "top_p": 0.9 (optional),
                "max_output_tokens": 1024 (optional)
            }
        """
        # Validate input data
        serializer = PromptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get prompt from validated data
        prompt = serializer.validated_data.get("prompt")
        model_name = serializer.validated_data.get(
            "model", settings.DEFAULT_GEMINI_MODEL
        )

        # Optional parameters
        generation_config = {}
        for param in ["temperature", "top_p", "max_output_tokens"]:
            if param in serializer.validated_data:
                generation_config[param] = serializer.validated_data[param]

        # Check if API key is configured
        if not settings.GOOGLE_AI_API_KEY:
            return Response(
                {"error": "Google AI API key is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Import Google's genai library
            from google import genai

            # Initialize the client with API key
            # genai.configure(api_key=settings.GOOGLE_AI_API_KEY)

            # Create a client
            client = genai.Client(api_key=settings.GOOGLE_AI_API_KEY)

            # Generate content
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                # generation_config=generation_config if generation_config else None,
            )

            # Parse the response and prepare output
            if hasattr(response, "text"):
                output_data = {"response": response.text, "model": model_name}

                # Add token counts if available
                if hasattr(response, "usage"):
                    usage = response.usage
                    if hasattr(usage, "prompt_tokens"):
                        output_data["prompt_tokens"] = usage.prompt_tokens
                    if hasattr(usage, "completion_tokens"):
                        output_data["completion_tokens"] = usage.completion_tokens
                    if hasattr(usage, "total_tokens"):
                        output_data["total_tokens"] = usage.total_tokens

                # Serialize and return the response
                response_serializer = ResponseSerializer(output_data)
                return Response(response_serializer.data)
            else:
                return Response(
                    {"error": "Failed to get text from AI model response."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except ImportError:
            logger.error("Failed to import genai library. Make sure it's installed.")
            return Response(
                {"error": "Required library 'genai' is not installed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error calling Google AI API: {str(e)}")
            return Response(
                {"error": f"Error calling Google AI API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
