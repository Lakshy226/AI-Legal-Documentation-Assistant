import json
import os
from datetime import date
# FIX: Import load_dotenv so the backend can read the .env file.
from dotenv import load_dotenv
from groq import Groq


load_dotenv()  # FIX: Load GROQ_API_KEY and other variables from backend/.env.


# Read the Groq API key from the environment.
API_KEY = os.getenv("GROQ_API_KEY")


# Force the model that supports Groq Strict Structured Outputs.
# FIX: Explicitly use the GPT-OSS 20B model for structured JSON output.
MODEL = "openai/gpt-oss-20b"


# Create the Groq client only when an API key exists.
client = Groq(api_key=API_KEY) if API_KEY else None


# Generate a structured legal document using Groq.
def generate_legal_document(
    template,
    data,
    legal_context,
    language="en"
):

    # Stop immediately if the API key is missing.
    if client is None:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    # Convert all frontend form fields into readable text.
    user_information = "\n".join(
        f"{key}: {value}"
        for key, value in data.items()
    )

    # Get today's date from the backend instead of asking the model to invent it.
    current_date = date.today().isoformat()

    # Create the system instruction for the legal-document assistant.
    system_prompt = """
You are an AI-assisted legal documentation assistant for India.

Your job is to prepare a FIRST DRAFT of legal documents.

STRICT RULES:

1. Never invent facts.
2. Never invent names, dates, amounts, addresses, clauses or user information.
3. Never invent statutes, sections, regulations or case law.
4. If information is missing, add it to missingInformation.
5. Do NOT insert fake placeholders into the document.
6. Do not silently assume important legal terms.
7. Clearly distinguish user-provided facts from legal guidance.
8. Use the supplied legal context where relevant.
9. Use clear language while retaining appropriate legal structure.
10. This is an AI-generated draft, not legal advice.
11. The user should review the document with a qualified legal professional.
12. The final document should be internally consistent.

DOCUMENT STRUCTURE:

The document MUST be highly structured and must NOT be one continuous paragraph.

Use clearly numbered major sections such as:

1. PARTIES
2. PROPERTY
3. TERM OF TENANCY
4. RENT AND PAYMENT
5. SECURITY DEPOSIT
6. USE OF PROPERTY
7. MAINTENANCE AND REPAIRS
8. TERMINATION
9. GOVERNING LAW AND JURISDICTION
10. SIGNATURES

Use subsection numbering where appropriate:

1.1
1.2
2.1
2.2
3.1
3.2

Important information such as names, dates, amounts, addresses and terms must be presented as clearly separated fields or clauses.

Do not combine unrelated legal provisions into the same paragraph.

Keep every major section and subsection separate.

The SIGNATURES section must contain separate signature information for each party.

Do not use Markdown tables.

Do not use Markdown headings such as # or ##.

Use plain numbered headings because the PDF generator will format them automatically.

The response format is enforced by the API.

Focus only on generating the requested legal document content.
"""

    # Create the user-specific generation request.
    user_prompt = f"""
Create a complete first draft of this legal document.

DOCUMENT TYPE:
{template}

CURRENT DATE:
{current_date}

LANGUAGE:
{language}

USER-PROVIDED INFORMATION:
{user_information}

LEGAL CONTEXT:
{legal_context}

Generate the document using the actual user-provided information.

Use the following section structure where applicable:

1. PARTIES

2. PROPERTY

3. TERM OF TENANCY

4. RENT AND PAYMENT

5. SECURITY DEPOSIT

6. USE OF PROPERTY

7. MAINTENANCE AND REPAIRS

8. TERMINATION

9. GOVERNING LAW AND JURISDICTION

10. SIGNATURES

Use subsections such as 1.1, 1.2, 2.1 and 2.2 where appropriate.

Use the actual values supplied by the user.

Never use fake placeholder values.

If information is missing:

- Keep the affected clause neutral.
- Add the missing item to missingInformation.
- Do not invent a value.

Keep the document professional and suitable for PDF rendering.
"""

    # Send the document-generation request to Groq.
    response = client.chat.completions.create(
        # FIX: Explicitly use the model that supports strict structured outputs.
        model=MODEL,

        # Send the system instructions and user information.
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        # FIX: Keep GPT-OSS reasoning simple for this document-generation task.
        reasoning_effort="low",

        # FIX: Use Strict Structured Outputs so Groq enforces the JSON structure.
        response_format={
            "type": "json_schema",

            # FIX: Define the exact JSON response structure.
            "json_schema": {
                "name": "legal_document",

                # FIX: Enable strict schema validation.
                "strict": True,

                # FIX: Define the legal-document response object.
                "schema": {
                    "type": "object",

                    "properties": {

                        # FIX: Generated document title.
                        "title": {
                            "type": "string"
                        },

                        # FIX: Generated legal document content.
                        "content": {
                            "type": "string"
                        },

                        # FIX: Generated document summary.
                        "summary": {
                            "type": "string"
                        },

                        # FIX: List of information missing from the user's input.
                        "missingInformation": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },

                        # FIX: List of warnings that should be shown to the user.
                        "warnings": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },

                    # FIX: Strict mode requires all schema properties to be required.
                    "required": [
                        "title",
                        "content",
                        "summary",
                        "missingInformation",
                        "warnings"
                    ],

                    # FIX: Strict mode requires additional properties to be disabled.
                    "additionalProperties": False
                }
            }
        }
    )

    # Extract the JSON string returned by Groq.
    raw_output = response.choices[0].message.content

    # Make sure the model actually returned something.
    if not raw_output:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    # Convert the JSON string into a Python dictionary.
    try:
        result = json.loads(raw_output)

    # Provide a useful error if Groq returned invalid JSON.
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Groq returned invalid JSON: {error}"
        )

    # Make sure the expected fields exist even if the model omitted one.
    result.setdefault(
        "title",
        template
    )

    result.setdefault(
        "content",
        ""
    )

    result.setdefault(
        "summary",
        ""
    )

    result.setdefault(
        "missingInformation",
        []
    )

    result.setdefault(
        "warnings",
        []
    )

    # Make sure missingInformation is always a list.
    if not isinstance(
        result["missingInformation"],
        list
    ):
        result["missingInformation"] = []

    # Make sure warnings is always a list.
    if not isinstance(
        result["warnings"],
        list
    ):
        result["warnings"] = []

    # Make sure content is a string.
    if not isinstance(
        result["content"],
        str
    ):
        result["content"] = str(
            result["content"]
        )

    # Make sure title is a string.
    if not isinstance(
        result["title"],
        str
    ):
        result["title"] = template

    # Make sure summary is a string.
    if not isinstance(
        result["summary"],
        str
    ):
        result["summary"] = str(
            result["summary"]
        )

    # Return the normalized result to Flask.
    return result
