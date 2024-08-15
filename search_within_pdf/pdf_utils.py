import fitz  # PyMuPDF

def find_text_in_pdf(pdf_path, search_text):
    """
    Searches for a specific text within a PDF and records the locations where it is found.
    """
    document = fitz.open(pdf_path)
    locations = []
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text_instances = page.search_for(search_text)
        if text_instances:
            locations.append({'page': page_num + 1})
    return locations
