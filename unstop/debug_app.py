import json
from markupsafe import escape # Assuming markupsafe is the correct module for escape

# Copying the show_results function from app.py
def show_results():
    try:
        # Read resume and analysis output
        with open("resume_output.json") as f:
            parsed_data = json.load(f)
        with open("analysis_output.json") as f:
            feedback = json.load(f)
    except FileNotFoundError as e:
        print("❌ Error: " + str(e) + ". Please run parser.py and analyzer.py first.")
        return "❌ Error: " + str(e) + ". Please run parser.py and analyzer.py first.", ""
    except json.JSONDecodeError as e:
        print("❌ Error: Invalid JSON format in output files. Please check parser.py and analyzer.py.")
        return "❌ Error: Invalid JSON format in output files. Please check parser.py and analyzer.py.", ""
    except Exception as e:
        print("❌ Error: " + str(e))
        return "❌ Error: " + str(e), ""

    # Format feedback with color highlights
    feedback_str = ""
    try:
        for section, feedback_items in feedback.items():
            feedback_str += f"<h3>{section.capitalize()} Feedback</h3>"
            if isinstance(feedback_items, list):
                for fb in feedback_items:
                    original = escape(fb.get('original', ''))
                    suggestion = escape(fb.get('suggestion', ''))
                    issues = ', '.join(fb.get('issues', []))
                    feedback_str += f"""
                    <div style=\"margin-bottom: 1em;\">
                        <p>❌ <b>Original:</b> <span style=\"background-color:#ffcccc; padding: 2px 4px;\">{original}</span></p>
                        <p>✅ <b>Suggestion:</b> <span style=\"background-color:#ccffcc; padding: 2px 4px;\">{suggestion}</span></p>
                        <p>🏷️ <b>Issues:</b> <span style=\"color:#b22222;\">{issues}</span></p>
                    </div>
                    """
            elif isinstance(feedback_items, dict) and "error" in feedback_items:
                feedback_str += f"<p style='color:red;'>⚠️ Error: {feedback_items['error']}</p>"
            else:
                feedback_str += f"<p>Unexpected feedback format for section {section}: {feedback_items}</p>"
    except Exception as e:
        print(f"❌ Error during feedback formatting: {str(e)}")
        return f"❌ Error during feedback formatting: {str(e)}", ""

    return "✅ Resume parsed and analyzed successfully!", feedback_str

# Run the function and print the output
if __name__ == "__main__":
    status, feedback = show_results()
    print("Status:", status)
    print("Feedback:", feedback) 