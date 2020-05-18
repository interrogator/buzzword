"""
Random utilities this app needs
"""


def markdown_to_buzz_input(markdown):
    """
    User can use markdown when correcting OCR
    We need to parse out headers and bulletpoints into <meta> features
    """
    return markdown


def filepath_for_pdf(pdf):
    return f"PATH TO {pdf}"


def get_raw_text_for_ocr(pdf_file):
    return f"OCR RESULT for {pdf_file}"
