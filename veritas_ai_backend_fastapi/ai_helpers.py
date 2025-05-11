# ai_helpers.py
import logging
from google.genai import (  # Use google.genai import style
    types,
    client as genai_client,
)
from pathlib import Path

logger = logging.getLogger(__name__)  # Use logger from main scope

VERITAS_MODEL_PREAMBLE_TEXT = """Okay, I've reviewed the text you provided. Here's a summary of the key information about Veritas University, Abuja, along with answers to potential questions a user might have, presented in a respectful and informative way:

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


def build_veritas_chat_contents(
    client: genai_client.Client, file_path: Path, prompt: str
) -> list[types.Content] | None:
    """
    Builds the 'contents' list for the Gemini API call using google.genai style,
    potentially uploading the Veritas data file.

    Args:
        client: The initialized Google AI client (obtained via google.genai).
        file_path: The Path object pointing to the Veritas data file.
        prompt: The user's input prompt.

    Returns:
        A list of google.genai.types.Content objects for the API call.
        Returns a simplified list if file upload fails but can proceed.
    """
    contents = []
    try:
        if not file_path.exists():
            logger.error(
                f"Veritas data file confirmed missing at {file_path} during content build."
            )
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            return contents

        logger.info(f"Attempting to upload Veritas data file from {file_path}")
        # Use client.files.upload and pass the *string path* as 'file'
        # This matches the original Django code's usage pattern more closely
        # Note: Ensure the API key is configured *before* this helper is called,
        # as the client needs it implicitly or explicitly.
        veritas_file = client.files.upload(file=str(file_path))  # Pass string path
        logger.info(
            f"Successfully uploaded file: {veritas_file.name}, URI: {veritas_file.uri}"
        )

        # Build contents with the uploaded file and preamble
        contents = [
            types.Content(
                role="user",
                parts=[
                    # Use Part.from_uri or Part.from_file_data depending on API version
                    # Add null checks for uri and mime_type to ensure they're strings
                    types.Part.from_uri(
                        file_uri=veritas_file.uri or "",  # Ensure not None
                        mime_type=veritas_file.mime_type or "application/octet-stream",
                    ),
                    types.Part.from_text(text="This is some of the school's data"),
                ],
            ),
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=VERITAS_MODEL_PREAMBLE_TEXT)],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        return contents

    except AttributeError as ae:
        # Catch potential issues if 'client.files' doesn't exist or uri attribute is named differently
        logger.error(
            f"Attribute error during file handling/content build (check API compatibility): {str(ae)}"
        )
        logger.warning("Falling back to using only the user prompt.")
        contents = [
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        ]
        return contents
    except Exception as e:
        logger.error(
            f"Error uploading Veritas data file or building contents: {str(e)}"
        )
        logger.warning("Falling back to using only the user prompt for generation.")
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        return contents
