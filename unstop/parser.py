import fitz  # PyMuPDF
import docx2txt
import mimetypes
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os
from PIL import Image
from io import BytesIO
import json

# Set your Gemini API Key
genai.configure(api_key="AIzaSyCY9tnrZXjEWJMlU39Y6Znd3eMnFQLBbI8")

# Gemini Vision model
vision_model = genai.GenerativeModel("gemini-2.0-flash")

def parse_docx(file_path):
    return docx2txt.process(file_path)

def parse_pdf_text(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_image_or_scanned_pdf(file_path):
    # For scanned PDFs, take a screenshot of each page and send to Gemini
    images = []
    if file_path.endswith(".pdf"):
        with fitz.open(file_path) as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                image = Image.open(BytesIO(img_bytes))
                images.append(image)
    else:
        image = Image.open(file_path)
        images.append(image)

    text = ""
    for img in images:
        response = vision_model.generate_content(
            [img, "Extract the text content from this resume image for structured analysis."]
        )
        text += response.text + "\n"
    return text.strip()

def get_text_from_resume(file_path):
    mime, _ = mimetypes.guess_type(file_path)
    if mime:
        if "pdf" in mime:
            text = parse_pdf_text(file_path)
            if len(text.strip()) < 100:  # Very low text — possibly scanned
                text = extract_text_from_image_or_scanned_pdf(file_path)
        elif "word" in mime or file_path.endswith(".docx"):
            text = parse_docx(file_path)
        elif mime.startswith("image/"):
            text = extract_text_from_image_or_scanned_pdf(file_path)
        else:
            raise ValueError("Unsupported file type.")
    else:
        raise ValueError("Unable to determine file type.")
    return text.strip()

def structure_resume_text_to_json(resume_text):
    prompt = f"""
You are a resume parser AI. Convert the following resume text into structured JSON with these sections:
education, experience, skills, projects, certifications (if any), achievements (if any), leadership (if any). Be accurate.

Resume Text:
\"\"\"
{resume_text}
\"\"\"
Return only JSON.
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def parse_resume(file_path):
    raw_text = get_text_from_resume(file_path)
    structured_json = structure_resume_text_to_json(raw_text)
    # Clean up the output if it starts/ends with code block markers
    cleaned = structured_json.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[len('```json'):].strip()
    if cleaned.startswith('```'):
        cleaned = cleaned[len('```'):].strip()
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3].strip()
    # Parse and return the JSON as a Python dict
    return json.loads(cleaned)

# === Example usage ===
if __name__ == "__main__":
    file_path = "ss.pdf"
    print("Reading PDF file...")
    raw_text = get_text_from_resume(file_path)
    print("\nExtracted text from PDF:")
    print("-" * 50)
    print(raw_text)
    print("-" * 50)
    print("\nStructuring text into JSON...")
    structured_json = structure_resume_text_to_json(raw_text)
    
    # Save the JSON output to a file
    try:
        # Clean up the output if it starts/ends with code block markers
        cleaned = structured_json.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[len('```json'):].strip()
        if cleaned.startswith('```'):
            cleaned = cleaned[len('```'):].strip()
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3].strip()
        # First, parse the JSON to ensure it's valid
        json_data = json.loads(cleaned)
        # Then save it with proper formatting
        with open("resume_output.json", "w") as f:
            json.dump(json_data, f, indent=2)
        print("\nJSON output saved to resume_output.json")
    except json.JSONDecodeError as e:
        print(f"\nError: Invalid JSON format - {str(e)}")
        print("Raw output:")
        print(structured_json)
    
    print("\nStructured JSON output:")
    print("-" * 50)
    print(structured_json)
    print("-" * 50)
