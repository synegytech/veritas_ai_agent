"""
Serializers for the AI API application.
"""

from rest_framework import serializers


class PromptSerializer(serializers.Serializer):
    """
    Serializer for the prompt input.
    """

    prompt = serializers.CharField(
        required=True, help_text="The text prompt to send to the AI model"
    )

    # Optional parameters
    model = serializers.CharField(
        required=False,
        help_text="The Gemini model to use (defaults to settings.DEFAULT_GEMINI_MODEL)",
    )
    temperature = serializers.FloatField(
        required=False,
        min_value=0.0,
        max_value=1.0,
        help_text="Controls randomness in output (0.0 to 1.0)",
    )
    top_p = serializers.FloatField(
        required=False,
        min_value=0.0,
        max_value=1.0,
        help_text="Nucleus sampling parameter (0.0 to 1.0)",
    )
    max_output_tokens = serializers.IntegerField(
        required=False, min_value=1, help_text="Maximum number of tokens to generate"
    )


class ResponseSerializer(serializers.Serializer):
    """
    Serializer for the AI response output.
    """

    response = serializers.CharField(
        help_text="The generated text response from the AI model"
    )
    model = serializers.CharField(help_text="The model used to generate the response")
    prompt_tokens = serializers.IntegerField(
        help_text="Number of tokens in the prompt", required=False
    )
    completion_tokens = serializers.IntegerField(
        help_text="Number of tokens in the completion", required=False
    )
    total_tokens = serializers.IntegerField(
        help_text="Total number of tokens used", required=False
    )
