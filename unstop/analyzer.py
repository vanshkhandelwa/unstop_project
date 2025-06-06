import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def analyze_section(section_name, section_data):
    prompt = f"""
You are a highly skilled resume analysis assistant helping students and professionals improve their resumes.

You are reviewing the section: **{section_name}**.

Instructions:
- If the section is about **experience**, **projects**, **education**, **achievements**, etc.:
  - Identify bullet points or descriptions that are vague, lack numbers/impact, or can be clearer.
  - **Suggest improved alternatives focusing on enhancing impact, clarity, and quantification, even for strong points.**
  - Tag the issues: ["lack of clarity", "missing quantification", "irrelevant content", "poor formatting"].

- If the section is **skills**:
  - Do NOT rephrase skills into sentences.
  - Instead, review each skill and:
    - Tag weak/vague/overused skills (e.g., "Teamwork", "Communication") if present.
    - Suggest **specific, technical, or relevant additional skills** that the candidate might add based on resume context.
    - Output new skills only in `"suggestion"` without altering existing ones.

Return a **JSON array** like this:

[
  {{
    "original": "Original item" (if applicable),
    "suggestion": "Improved or new item",
    "issues": ["clarity", "quantification", ...]
  }},
  ...
]

If there are no issues or nothing to add, return an empty list `[]`.

Resume section content:
{section_data}
"""
    response = model.generate_content(prompt)
    return response.text

    response = model.generate_content(prompt)
    return response.text

def analyze_resume():
    try:
        # Read the JSON output from parser.py
        with open("resume_output.json", "r") as f:
            resume_data = json.load(f)
        print("\nAnalyzing Resume Sections...")
        print("=" * 50)

        # Dynamically analyze all sections found in resume_data
        feedback = {}
        for section_name, section_data in resume_data.items():
            print(f"\nProcessing section: {section_name}")

            # If section data is a dictionary, analyze its subsections
            if isinstance(section_data, dict):
                print(f"Analyzing subsections within {section_name}...")
                subsection_feedback = {}
                for sub_section_name, sub_section_data in section_data.items():
                    print(f"  Analyzing subsection: {sub_section_name}")
                    # Skip empty subsections
                    if not sub_section_data:
                        print(f"  Skipping empty subsection: {sub_section_name}")
                        continue

                    # Convert subsection data to string format for analysis based on type
                    sub_section_str = ""
                    if isinstance(sub_section_data, list):
                        # If list of dictionaries: Format each dict into a string
                        if sub_section_data and isinstance(sub_section_data[0], dict):
                            formatted_items = []
                            for i, item_dict in enumerate(sub_section_data):
                                item_str = f"Item {i+1}:\n"
                                for key, value in item_dict.items():
                                    item_str += f"  {key.replace('_', ' ').title()}: {value}\n"
                                formatted_items.append(item_str)
                            sub_section_str = "\n---\n".join(formatted_items)
                        # If list of strings: Join strings
                        else:
                            sub_section_str = "\n".join(sub_section_data)
                    else:
                         # For other types, just convert to string
                         sub_section_str = str(sub_section_data)

                    # Analyze the subsection
                    analysis = analyze_section(f"{section_name} - {sub_section_name}", sub_section_str)
                    print(f"  Analysis response for {sub_section_name}:")
                    print(analysis)

                    # Extract and parse JSON for the subsection
                    cleaned_analysis = analysis.strip()
                    json_start = cleaned_analysis.find('```json')
                    json_end = cleaned_analysis.rfind('```')

                    if json_start != -1 and json_end != -1 and json_end > json_start:
                        cleaned_analysis = cleaned_analysis[json_start + len('```json'):json_end].strip()
                    elif cleaned_analysis.startswith('```') and cleaned_analysis.endswith('```'):
                        cleaned_analysis = cleaned_analysis[len('```'):-3].strip()

                    try:
                        subsection_feedback[sub_section_name] = json.loads(cleaned_analysis)
                    except Exception as e:
                        subsection_feedback[sub_section_name] = {"error": f"Invalid response format after cleaning for subsection {sub_section_name}: {str(e)}", "raw_analysis": analysis, "cleaned_attempt": cleaned_analysis}

                feedback[section_name] = subsection_feedback # Store subsection feedback under the main section key

            # If section data is a list or other format, analyze the whole section as before
            elif isinstance(section_data, list) or not section_data:
                # Skip empty sections (already handled at the start of the loop, but double-check)
                if not section_data:
                     print(f"Skipping empty section: {section_name}")
                     continue

                print(f"Analyzing section: {section_name}")
                # Convert section data to string format for analysis based on type
                section_str = ""
                # If list of dictionaries (like education, experience, projects):
                if section_data and isinstance(section_data[0], dict):
                    formatted_items = []
                    for i, item_dict in enumerate(section_data):
                        item_str = f"Item {i+1}:\n"
                        for key, value in item_dict.items():
                            # Handle lists within the dictionary (like 'description' in experience/projects)
                            if isinstance(value, list):
                                item_str += f"  {key.replace('_', ' ').title()}:\n"
                                for j, list_item in enumerate(value):
                                    item_str += f"    - {list_item}\n"
                            else:
                                item_str += f"  {key.replace('_', ' ').title()}: {value}\n"
                        formatted_items.append(item_str)
                    section_str = "\n---\n".join(formatted_items)
                # If list of strings (like relevant_coursework, self_learning, technical_achievements, leadership_activities):
                elif isinstance(section_data, list):
                     section_str = "\n".join(section_data)
                # If other format (shouldn't typically happen for these sections, but as a fallback)
                else:
                     section_str = str(section_data)

                analysis = analyze_section(section_name, section_str)
                print(f"Analysis response for {section_name}:")
                print(analysis)

                # Extract and parse JSON for the section
                cleaned_analysis = analysis.strip()
                json_start = cleaned_analysis.find('```json')
                json_end = cleaned_analysis.rfind('```')

                if json_start != -1 and json_end != -1 and json_end > json_start:
                    cleaned_analysis = cleaned_analysis[json_start + len('```json'):json_end].strip()
                elif cleaned_analysis.startswith('```') and cleaned_analysis.endswith('```'):
                    cleaned_analysis = cleaned_analysis[len('```'):-3].strip()

                try:
                    feedback[section_name] = json.loads(cleaned_analysis)
                except Exception as e:
                    feedback[section_name] = {"error": f"Invalid response format after cleaning for section {section_name}: {str(e)}", "raw_analysis": analysis, "cleaned_attempt": cleaned_analysis}
            else:
                # Handle cases where section data is neither a dict nor a list (e.g., a single string or number, though less common in resume sections)
                print(f"Analyzing simple section: {section_name}")
                section_str = str(section_data) # Treat as string

                analysis = analyze_section(section_name, section_str)
                print(f"Analysis response for {section_name}:")
                print(analysis)

                # Extract and parse JSON for the section (assuming model still returns JSON list format for simple sections)
                cleaned_analysis = analysis.strip()
                json_start = cleaned_analysis.find('```json')
                json_end = cleaned_analysis.rfind('```')

                if json_start != -1 and json_end != -1 and json_end > json_start:
                    cleaned_analysis = cleaned_analysis[json_start + len('```json'):json_end].strip()
                elif cleaned_analysis.startswith('```') and cleaned_analysis.endswith('```'):
                    cleaned_analysis = cleaned_analysis[len('```'):-3].strip()

                try:
                     # Even for simple sections, the model is prompted to return a list
                    feedback[section_name] = json.loads(cleaned_analysis)
                except Exception as e:
                    feedback[section_name] = {"error": f"Invalid response format after cleaning for simple section {section_name}: {str(e)}", "raw_analysis": analysis, "cleaned_attempt": cleaned_analysis}


        # Save feedback to analysis_output.json
        with open("analysis_output.json", "w") as f:
            json.dump(feedback, f, indent=2)
        print("\nFeedback saved to analysis_output.json")
    except FileNotFoundError:
        print("Error: resume_output.json not found. Please run parser.py first.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in resume_output.json")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    analyze_resume()
