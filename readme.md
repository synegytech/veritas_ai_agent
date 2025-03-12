# Veritas AI Backend

A Django backend that interfaces with Google AI Studio APIs for generative AI models like Gemini Pro.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd veritas_ai_backend
```

### 2. Create and Activate a Virtual Environment

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Required Libraries

```bash
pip install django djangorestframework google-generativeai
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory and add your Google AI API key:

```
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

Then, set up the environment variables:

```bash
# For Windows
set GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# For macOS/Linux
export GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The server will start at http://127.0.0.1:8000/

## API Endpoints

### Generate AI Text

- **URL**: `/api/generate/`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Body

```json
{
  "prompt": "Your text prompt here",
  "model": "gemini-2.0-flash", // Optional, defaults to settings.DEFAULT_GEMINI_MODEL
  "temperature": 0.7, // Optional
  "top_p": 0.9, // Optional
  "max_output_tokens": 1024 // Optional
}
```

#### Successful Response (200 OK)

```json
{
  "response": "The AI-generated text response",
  "model": "gemini-2.0-flash",
  "prompt_tokens": 10, // Optional
  "completion_tokens": 50, // Optional
  "total_tokens": 60 // Optional
}
```

#### Error Response (4xx/5xx)

```json
{
  "error": "Error message",
  "details": {} // Optional details about the error
}
```

## Testing the API

### Using curl

```bash
curl -X POST \
  http://127.0.0.1:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain how AI works"}'
```

### Using Python Requests

```python
import requests

url = "http://127.0.0.1:8000/api/generate/"
payload = {"prompt": "Explain how AI works"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### Using Postman

1. Create a new POST request to `http://127.0.0.1:8000/api/generate/`
2. Set the Content-Type header to `application/json`
3. In the Body tab, select "raw" and "JSON" format
4. Enter the JSON payload: `{"prompt": "Explain how AI works"}`
5. Send the request
