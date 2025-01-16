from rest_framework import serializers
from .models import ModelInput, ModelOutput


class ModelInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelInput
        fields = ["id", "input_data", "created_at"]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ModelOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelOutput
        fields = ["id", "input_data", "output_data", "created_at"]
        read_only_fields = ["created_at"]
