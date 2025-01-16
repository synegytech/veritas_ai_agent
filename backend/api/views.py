from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ModelInput, ModelOutput
from .serializers import ModelInputSerializer, ModelOutputSerializer


class ModelInputViewSet(viewsets.ModelViewSet):
    queryset = ModelInput.objects.all()
    serializer_class = ModelInputSerializer

    def get_queryset(self):
        return ModelInput.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        input_instance = self.get_object()

        # Here you would integrate with your ML model
        # This is a placeholder for model processing
        model_output = self.process_model(input_instance.input_data)

        output_data = {"input_data": input_instance.id, "output_data": model_output}

        output_serializer = ModelOutputSerializer(data=output_data)
        if output_serializer.is_valid():
            output_serializer.save()
            return Response(output_serializer.data)
        return Response(output_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def process_model(self, input_data):
        # Placeholder for model processing
        # Replace this with your actual model logic
        return {"processed_result": "Model output here"}


class ModelOutputViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModelOutput.objects.all()
    serializer_class = ModelOutputSerializer

    def get_queryset(self):
        return ModelOutput.objects.filter(input_data__user=self.request.user)
