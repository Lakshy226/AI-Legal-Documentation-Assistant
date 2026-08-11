import os
import uuid

from flask import (
    Flask,
    jsonify,
    request,
    send_file,
    send_from_directory
)

from flask_cors import CORS
from dotenv import load_dotenv

from services.ai_service import generate_legal_document
from services.legal_service import get_legal_context
from services.pdf_service import create_pdf


# Load the .env file from the backend directory.
load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        ".env"
    )
)


# Create the Flask application.
app = Flask(__name__)


# Locate the frontend directory.
FRONTEND_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend"
    )
)


# Allow frontend requests to communicate with Flask.
CORS(app)


# Directory where generated PDFs will be stored.
GENERATED_DOCS_DIR = os.path.join(
    os.path.dirname(__file__),
    "generated_docs"
)


# Create the generated_docs directory if it does not exist.
os.makedirs(
    GENERATED_DOCS_DIR,
    exist_ok=True
)


# Document types currently supported by the application.
SUPPORTED_TEMPLATES = {
    "Rental Agreement",
    "Non-Disclosure Agreement",
    "Employment Agreement",
    "Service Agreement",
    "Independent Contractor Agreement",
    "Loan Agreement",
    "Bill of Sale",
    "Partnership Agreement",
    "Power of Attorney"
}


# Required fields for document types that currently have
# dedicated frontend forms.
# Required fields for every supported document type.
REQUIRED_FIELDS = {

    # Rental Agreement fields.
    "Rental Agreement": [
        "landlord",
        "tenant",
        "property",
        "startDate",
        "rent",
        "term",
        "jurisdiction"
    ],

    # Non-Disclosure Agreement fields.
    "Non-Disclosure Agreement": [
        "discloser",
        "recipient",
        "purpose",
        "term",
        "jurisdiction"
    ],

    # Employment Agreement fields.
    "Employment Agreement": [
        "employer",
        "employee",
        "role",
        "startDate",
        "salary",
        "jurisdiction"
    ],

    # Service Agreement fields.
    "Service Agreement": [
        "provider",
        "client",
        "services",
        "fee",
        "startDate",
        "jurisdiction"
    ],

    # Independent Contractor Agreement fields.
    "Independent Contractor Agreement": [
        "client",
        "contractor",
        "services",
        "fee",
        "startDate",
        "jurisdiction"
    ],

    # Loan Agreement fields.
    "Loan Agreement": [
        "lender",
        "borrower",
        "amount",
        "interest",
        "startDate",
        "repayment",
        "jurisdiction"
    ],

    # Bill of Sale fields.
    "Bill of Sale": [
        "seller",
        "buyer",
        "item",
        "price",
        "saleDate",
        "jurisdiction"
    ],

    # Partnership Agreement fields.
    "Partnership Agreement": [
        "partnerOne",
        "partnerTwo",
        "business",
        "contribution",
        "startDate",
        "jurisdiction"
    ],

    # Power of Attorney fields.
    "Power of Attorney": [
        "principal",
        "agent",
        "powers",
        "startDate",
        "jurisdiction"
    ]
}


# Serve the frontend when the root URL is opened.
@app.get("/")
def serve_frontend():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# Simple backend health-check endpoint.
@app.get("/api/health")
def health():
    return jsonify({
        "success": True,
        "message": "Legal Assistant backend is running!"
    })


# Validate the document data before sending it to the AI.
def validate_document_data(
    template,
    data
):
    # Get the required fields for the selected template.
    required = REQUIRED_FIELDS.get(
        template,
        []
    )

    # Find fields that are missing or empty.
    missing = [
        field
        for field in required
        if not str(
            data.get(field, "")
        ).strip()
    ]

    return missing


# Generate a new AI-assisted legal document.
@app.post("/api/generate")
def generate_document():

    try:
        # Get the JSON payload sent by the frontend.
        payload = request.get_json(
            silent=True
        ) or {}

        # Get the selected document template.
        template = payload.get(
            "template"
        )

        # Get the selected language.
        language = payload.get(
            "language",
            "en"
        )

        # Get the form data.
        data = payload.get(
            "data",
            {}
        )

        # Make sure a document template was supplied.
        if not template:
            return jsonify({
                "success": False,
                "error": "No document template was provided."
            }), 400

        # Make sure the selected document type is supported.
        if template not in SUPPORTED_TEMPLATES:
            return jsonify({
                "success": False,
                "error": f"Unsupported document template: {template}"
            }), 400

        # Make sure the frontend actually sent an object for data.
        if not isinstance(
            data,
            dict
        ):
            return jsonify({
                "success": False,
                "error": "Document data must be a JSON object."
            }), 400

        # Validate the required fields for templates
        # that have predefined required fields.
        missing_fields = validate_document_data(
            template,
            data
        )

        # Do not stop generation for missing information.
        # The AI service is responsible for reporting missing
        # information in its structured response.
        #
        # This validation is intentionally kept available
        # for future frontend warnings.

        # Get relevant legal context for this document.
        legal_context = get_legal_context(
            template,
            data,
            data.get(
                "jurisdiction",
                "India"
            ),
            language
        )

        # Generate the legal document using the AI service.
        result = generate_legal_document(
            template,
            data,
            legal_context,
            language
        )

        # Create a unique ID for the generated document.
        document_id = str(
            uuid.uuid4()
        )

        # Build the PDF output path.
        pdf_path = os.path.join(
            GENERATED_DOCS_DIR,
            f"{document_id}.pdf"
        )

        # Generate the initial PDF.
        create_pdf(
            result["title"],
            result["content"],
            pdf_path
        )

        # Return the generated document to the frontend.
        return jsonify({
            "success": True,

            "document_id": document_id,

            "title": result.get(
                "title",
                template
            ),

            "content": result.get(
                "content",
                ""
            ),

            "summary": result.get(
                "summary",
                ""
            ),

            "missingInformation": result.get(
                "missingInformation",
                []
            ),

            "warnings": result.get(
                "warnings",
                []
            ),

            "missingFields": missing_fields,

            "pdf_url": (
                f"/api/documents/"
                f"{document_id}/pdf"
            )
        })

    except Exception as error:

        # Print the actual backend error in the Flask terminal.
        print(
            "\n========== GENERATION ERROR =========="
        )

        print(
            repr(error)
        )

        print(
            "=======================================\n"
        )

        # Always return JSON so the frontend can safely
        # handle backend errors.
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# Regenerate a PDF using the CURRENT edited document.
@app.post("/api/documents/<document_id>/pdf")
def regenerate_pdf(
    document_id
):

    # Read the JSON body sent by the frontend.
    body = request.get_json(
        silent=True
    )

    # Reject requests that do not contain valid JSON.
    if not body:
        return jsonify({
            "success": False,
            "error": "Request body must contain JSON."
        }), 400

    # Extract the current document title.
    title = str(
        body.get(
            "title",
            "Legal Document"
        )
    ).strip()

    # Extract the current edited document content.
    content = str(
        body.get(
            "content",
            ""
        )
    ).strip()

    # Make sure the document contains content.
    if not content:
        return jsonify({
            "success": False,
            "error": "Document content is empty."
        }), 400

    # Prevent path traversal attacks through document_id.
    if (
        "/" in document_id
        or "\\" in document_id
        or ".." in document_id
    ):
        return jsonify({
            "success": False,
            "error": "Invalid document ID."
        }), 400

    # Build the PDF path.
    pdf_path = os.path.join(
        GENERATED_DOCS_DIR,
        f"{document_id}.pdf"
    )

    try:

        # Generate the PDF using the user's edited content.
        create_pdf(
            title=title,
            content=content,
            output_path=pdf_path
        )

        # Return the PDF download endpoint.
        return jsonify({
            "success": True,
            "pdf_url": (
                f"/api/documents/"
                f"{document_id}/pdf"
            )
        })

    except Exception as error:

        # Print the technical error in the backend terminal.
        print(
            "\n========== PDF GENERATION ERROR =========="
        )

        print(
            repr(error)
        )

        print(
            "===========================================\n"
        )

        # Return a controlled JSON error.
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# Download an existing generated PDF.
@app.get("/api/documents/<document_id>/pdf")
def download_pdf(
    document_id
):

    # Prevent path traversal attacks.
    if (
        "/" in document_id
        or "\\" in document_id
        or ".." in document_id
    ):
        return jsonify({
            "success": False,
            "error": "Invalid document ID."
        }), 400

    # Build the PDF path.
    pdf_path = os.path.join(
        GENERATED_DOCS_DIR,
        f"{document_id}.pdf"
    )

    # Check whether the PDF exists.
    if not os.path.isfile(
        pdf_path
    ):
        return jsonify({
            "success": False,
            "error": "Document not found."
        }), 404

    # Send the PDF to the browser.
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{document_id}.pdf"
    )


# Start Flask when app.py is executed directly.
if __name__ == "__main__":

    # Start the local development server.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
