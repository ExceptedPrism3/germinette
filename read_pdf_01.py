from pypdf import PdfReader
import sys

try:
    reader = PdfReader("en.subject-18.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)
except Exception as e:
    print(f"Error: {e}")
