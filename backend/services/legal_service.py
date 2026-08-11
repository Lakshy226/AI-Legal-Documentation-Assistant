import json
import os


# Locate the project root.
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)


# Locate the legal source database.
LEGAL_SOURCE_FILE = os.path.join(
    PROJECT_ROOT,
    "legal_data",
    "sources.json"
)


def get_legal_context(
    template,
    data=None,
    jurisdiction="India",
    language="en"
):
    """
    Retrieve potentially relevant legal authorities for any
    supported document type.

    The function does NOT decide that a law definitely applies.
    It supplies candidate authorities to the AI for analysis.
    """

    # Ensure form data is always a dictionary.
    data = data or {}

    # Normalize jurisdiction.
    jurisdiction = str(
        jurisdiction or "India"
    ).strip()

    # Make sure the legal database exists.
    if not os.path.isfile(
        LEGAL_SOURCE_FILE
    ):
        return {
            "document_type": template,
            "jurisdiction": jurisdiction,
            "language": language,
            "user_facts": data,
            "sources": [],
            "notice": (
                "Legal source database was not found."
            )
        }

    # Load the legal source database.
    try:

        with open(
            LEGAL_SOURCE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            database = json.load(
                file
            )

    except (
        OSError,
        json.JSONDecodeError
    ) as error:

        return {
            "document_type": template,
            "jurisdiction": jurisdiction,
            "language": language,
            "user_facts": data,
            "sources": [],
            "notice": (
                f"Legal database error: {error}"
            )
        }

    # Retrieve authorities for the selected document.
    sources = database.get(
        template,
        []
    )

    # Add retrieval metadata to every source.
    retrieved_sources = []

    for source in sources:

        source_copy = dict(
            source
        )

        # Mark the source as retrieved.
        source_copy["retrieved"] = True

        # Record the jurisdiction being analyzed.
        source_copy["analysis_jurisdiction"] = jurisdiction

        retrieved_sources.append(
            source_copy
        )

    # Return the complete context to the AI.
    return {
        "document_type": template,
        "jurisdiction": jurisdiction,
        "language": language,
        "user_facts": data,
        "sources": retrieved_sources
    }
