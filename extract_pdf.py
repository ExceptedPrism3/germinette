import pypdf
import sys

try:
    reader = pypdf.PdfReader("/Users/pixo/Documents/Coding/Python/germinettte/Intra Projects Python Module 02 Edit.pdf")
    print(f"Number of pages: {len(reader.pages)}")
    for i, page in enumerate(reader.pages):
        print(f"\n--- Page {i+1} ---")
        print(page.extract_text())
except Exception as e:
    print(f"Error: {e}")
