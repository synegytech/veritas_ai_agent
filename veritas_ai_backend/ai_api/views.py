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
from rest_framework.parsers import JSONParser
from google import genai
from google.genai import types

from .serializers import PromptSerializer, ResponseSerializer

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
                "model": "gemini-2.0-pro-exp-02-05" (optional),
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
        prompt = serializer.validated_data.get("prompt", "")
        if not prompt:
            return Response(
                {"error": "Prompt is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model_name = serializer.validated_data.get(
            "model",
            settings.VERITAS_AI_MODEL,
        )

        # Check if API key is configured
        api_key = settings.GOOGLE_AI_API_KEY
        if not api_key:
            return Response(
                {"error": "Google AI API key is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Check if the Veritas data file exists
        if not os.path.exists(VERITAS_DATA_FILE_PATH):
            logger.error(f"Veritas data file not found at {VERITAS_DATA_FILE_PATH}")
            return Response(
                {"error": "Required data file not found on the server."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Configure the client with API key
            client = genai.Client(api_key=api_key)

            # Upload the Veritas data file to Google's API
            try:
                logger.info(
                    f"Uploading Veritas data file from {VERITAS_DATA_FILE_PATH}"
                )
                veritas_file = client.files.upload(file=VERITAS_DATA_FILE_PATH)

                # Context builder - similar to the example code the user provided
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=veritas_file.uri,
                                mime_type=veritas_file.mime_type,
                            ),
                            types.Part.from_text(
                                text="This is some of the schools data"
                            ),
                        ],
                    ),
                    types.Content(
                        role="model",
                        parts=[
                            types.Part.from_text(
                                text="""Okay, I've reviewed the text you provided. Here's a summary of the key information about Veritas University, Abuja, along with answers to potential questions a user might have, presented in a respectful and informative way:

**About Veritas University, Abuja (VUA)**

*   **Overview:** Veritas University is a private university located in Bwari Area Council, Abuja, Nigeria.  It was founded by the Catholic Bishops Conference of Nigeria in 2002 and emphasizes a holistic education combining academics, moral values, and Christian principles.  It's often referred to as the Catholic University of Nigeria.
*   **Mission:** To provide an integral and holistic education, blending academic and professional training with moral, spiritual, and cultural development, rooted in Catholic teachings.  The university is committed to research, truth-seeking, and producing graduates who contribute positively to society.
*   **Vision:** To be a dynamic community fostering academic excellence and contributing to the advancement of Nigeria, ranking among the best universities globally.
*   **Core Values:** Hard work, integrity, discipline, creativity, and dedication to Catholic principles.
*   **Philosophy:** All knowledge originates from God and is for the service of humanity. The university promotes the highest standards of teaching, research, and community service.
*   **History:**
    *   Founded in March 2002 by the Catholic Bishops Conference of Nigeria.
    *   Received provisional operation license in 2007.
    *   Started admitting students in October 2008 at a temporary campus in Obehie, Abia State.
    *   Moved to its permanent campus in Bwari, Abuja, in 2014.

**Key Information and Potential Questions & Answers:**

*   **Q: When is the resumption date for the 2024/2025 academic session?**

    *   **A:**  There has been a change in the resumption dates.
        *   **100-level students:** Monday, October 7th, 2024.
        *   **Returning students (200-500 level):** Saturday, October 12th, 2024.
        *   The university apologizes for any inconvenience caused by this change.

*   **Q: What documents do fresh (new) students need to bring for resumption?**

    *   **A:** Fresh students (UTME, Direct Entry, and Transfer) need four (4) photocopies of each of the following:
        1.  UTME result slip
        2.  O' Level Result(s) (WAEC/NECO/NABTEB, etc.)
        3.  Veritas University admission letter
        4.  Birth certificate/evidence of age
        5.  Attestation letter
        6.  Sponsorship letter
        7.  Medical fitness report
        8.  Evidence of State of origin
        9.  Original O' Level certificate (if available)
        10. Evidence of Change of Institution to Veritas University (for those who didn't initially choose Veritas as their first choice)
        11. JAMB Admission Letter
        12. Transcript (for transfer students only)
        13. Evidence of transfer fee (for transfer students only)
    *   **Important Notes for Freshers:**
        *   Students with awaiting results or who didn't choose Veritas as their first choice *must* visit a JAMB CBT center to change their institution and upload their O' Level results *before* resumption.
        *   Transfer students must also visit a CBT center to regularize their admission and submit an indemnity form to the Vice-Chancellor's office.

*   **Q: How can I contact Veritas University regarding admission inquiries?**

    *   **A:** You can contact the following individuals:
        1.  Rev. Fr. Dr. Peter Bakwaph: 08039398830 (Chairman, Admission Committee)
        2.  Mr. Ilya Cephas: 07086858143
        3.  Dr. Adidi Dokpesi: 08138605055
    *   **Crucially:** The university warns against fraudsters. Do *not* interact with any phone numbers not explicitly listed on the official website (www.veritas.edu.ng). They do *not* offer admissions or accept payments through third parties.

*   **Q: What is the official website of Veritas University?**

    *   **A:** The official website is [www.veritas.edu.ng](http://www.veritas.edu.ng/).

*   **Q: What is the motto of Veritas University?**

    *   **A:** The motto is \"Seeking the Truth.\"

*   **Q: Who is the Vice-Chancellor of Veritas University?**

    *   **A:** The Vice-Chancellor is Prof. Hyacinth E. Ichoku.

* **Q: Who is the Registrar of Veritas University?**
    *   **A:** Dr. Mrs. Stella Chizoba Okonkwo

*   **Q: Where is Veritas University located?**

    *   **A:** The university is located in the Bwari Area Council of the Federal Capital Territory, Abuja, Nigeria.

*   **Q: What are some recent achievements of Veritas University?**

    *   **A:**
        *   Ranked among the top 11 universities in Nigeria in the 2023 Times Higher Education (THE) Impact Rankings.
        *   Adopted by the African Development Bank (AfDB) as a Centre of Excellence for Computer Coding.
        *   Offers free digital skills training to young Nigerians in Abuja.
        *   Successfully represented Africa in a global universities debate competition.
        * had it 13th convocation ceremony.

*   **Q: What is the Veritas University Endowment Foundation?**

    *   **A:** It's a philanthropic initiative of the Catholic Bishops Conference of Nigeria to create a self-sustaining, faith-based, and value-centered university. It accepts donations and endowments to support scholarships, infrastructure development, and research.

* **Q:Does Veritas University have a focus on research?**
        * A: Yes veritas university places a strong emphasis on research.

* **Q:What are some of qualities expected from veritas university graduates?**
       * A: Wide and ordered knowledge in an area of academic
discipline ,The ability to reason logically,The ability to communicate clearly in speech and writing with
confidence, Competence in numeric and computer literacy
,Exhibition of such moral values as honesty, humility,
truthfulness, love and high ethics in personal and professional
life, Ready acceptance of obligations and responsibilities; and well
developed interpersonal skills and capacity for team work.

* **Q:What is the email for the school's bursar?**
      *A: bursar@veritas.edu.ng

I believe this comprehensively covers the information provided in the text, addressing likely questions in a clear, organized, and respectful manner. I have prioritized the most important information, especially regarding admissions and the resumption date changes.
"""
                            ),
                        ],
                    ),
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                        ],
                    ),
                ]
            except Exception as e:
                logger.error(f"Error uploading Veritas data file: {str(e)}")

                # Fallback to just using the prompt if file upload fails
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    ),
                ]

            # Configuration for generation
            generate_content_config = types.GenerateContentConfig(
                temperature=serializer.validated_data.get("temperature", 1.0),
                top_p=serializer.validated_data.get("top_p", 0.95),
                top_k=serializer.validated_data.get("top_k", 64),
                max_output_tokens=serializer.validated_data.get(
                    "max_output_tokens", 8192
                ),
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(
                        text="You are An AI chatbot for Veritas University Abuja. You will answer questions respectfully and give accurate answers."
                    ),
                ],
            )

            # Generate content
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text

            # Prepare output data
            output_data = {"response": response_text, "model": model_name}

            # Serialize and return the response
            response_serializer = ResponseSerializer(output_data)
            return Response(response_serializer.data)

        except ImportError as e:
            logger.error(f"Failed to import required libraries: {str(e)}")
            return Response(
                {"error": f"Required libraries are not installed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error calling Google AI API: {str(e)}")
            return Response(
                {"error": f"Error calling Google AI API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
