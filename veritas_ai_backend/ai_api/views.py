# Create your views here.
"""
Views for the AI API application.
"""

import logging
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai

from veritas_ai_backend.settings import VERITAS_AI_MODEL

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
                "model": "tunedModels/veritasai1-asmlxpf43sd9" (optional),
                "temperature": 1.0 (optional),
                "top_p": 0.95 (optional),
                "top_k": 64 (optional),
                "max_output_tokens": 8192 (optional)
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
            # "model", settings.DEFAULT_GEMINI_MODEL
            "model",
            settings.VERITAS_AI_MODEL,
        )

        # Optional parameters for generation config
        generation_config = {
            "temperature": serializer.validated_data.get("temperature", 1.0),
            "top_p": serializer.validated_data.get("top_p", 0.95),
            "top_k": serializer.validated_data.get("top_k", 64),
            "max_output_tokens": serializer.validated_data.get(
                "max_output_tokens", 8192
            ),
            "response_mime_type": "text/plain",
        }

        # Check if API key is configured
        api_key = settings.GOOGLE_AI_API_KEY
        if not api_key:
            return Response(
                {"error": "Google AI API key is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Configure the client with API key
            genai.configure(api_key=api_key)

            # Create the model
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
            )

            # Create a chat session and send message
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)

            # Prepare output data
            output_data = {"response": response.text, "model": model_name}

            # Add token counts if available in the response
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

        except ImportError:
            logger.error(
                "Failed to import google.generativeai library. Make sure it's installed."
            )
            return Response(
                {"error": "Required library 'google.generativeai' is not installed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error calling Google AI API: {str(e)}")
            return Response(
                {"error": f"Error calling Google AI API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
