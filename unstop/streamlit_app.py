import streamlit as st
import json
from markupsafe import escape
import os

st.set_page_config(layout="wide")
st.title("🧠 Resume Analyzer Results Viewer (Streamlit)")
st.markdown("This displays the results from `parser.py` and `analyzer.py`. **Please run those scripts first.**")

def load_and_display_results():
    try:
        if not os.path.exists("resume_output.json"):
            st.error("❌ Error: resume_output.json not found. Please run parser.py first.")
            return
        if not os.path.exists("analysis_output.json"):
            st.error("❌ Error: analysis_output.json not found. Please run analyzer.py first.")
            return

        with open("resume_output.json", "r", encoding='utf-8') as f:
            parsed_data = json.load(f)
        with open("analysis_output.json", "r", encoding='utf-8') as f:
            feedback = json.load(f)

    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in output files.")
        return
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return

    # Display feedback section by section
    for section_name, feedback_data in feedback.items():
        st.subheader(f"{section_name.capitalize()} Feedback")

        if isinstance(feedback_data, dict):
            if not feedback_data:
                st.info(f"No feedback found for the {section_name.capitalize()} section.")
            else:
                for sub_section_name, subsection_feedback_items in feedback_data.items():
                    st.markdown(f"**{sub_section_name.replace('_', ' ').title()}**")

                    if isinstance(subsection_feedback_items, list):
                        if not subsection_feedback_items:
                            st.info(f"No suggestions found for {sub_section_name.replace('_', ' ').title()}.")
                        else:
                            for fb in subsection_feedback_items:
                                suggestion = escape(fb.get('suggestion', ''))
                                issues = ', '.join(fb.get('issues', []))
                                is_skills_section = section_name.lower() == "skills"

                                if fb.get('original') is not None:
                                    original = escape(fb.get('original', ''))
                                    st.markdown(f"""
                                    <div style="margin-bottom: 1em; padding: 1em; border: 1px solid #eee; border-radius: 5px;">
                                        <p>❌ <b>Original:</b> <span style="background-color:#ffcccc; padding: 2px 4px; border-radius: 3px;">{original}</span></p>
                                        {(f'<p>✅ <b>Suggestion:</b> <span style="background-color:#ccffcc; padding: 2px 4px; border-radius: 3px;">{suggestion}</span></p>' if suggestion else '')}
                                        {(f'<p>🏷️ <b>Issues:</b> <span style="color:#b22222;">{issues}</span></p>' if issues else '')}
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    label = "Suggested Skill Addition" if is_skills_section else "Potential Addition"
                                    st.markdown(f"""
                                    <div style="margin-bottom: 1em; padding: 1em; border: 1px solid #d3edff; border-radius: 5px;">
                                        <p>✨ <b>{label}:</b> <span style="background-color:#e6f7ff; padding: 2px 4px; border-radius: 3px;">{suggestion}</span></p>
                                    </div>
                                    """, unsafe_allow_html=True)

                    elif isinstance(subsection_feedback_items, dict) and "error" in subsection_feedback_items:
                        st.error(f"⚠️ Analyzer Error: {subsection_feedback_items['error']}")
                        if "raw_analysis" in subsection_feedback_items:
                            st.markdown(f"<pre>{escape(subsection_feedback_items['raw_analysis'])}</pre>", unsafe_allow_html=True)
                    else:
                        st.warning(f"Unexpected format in subsection: {sub_section_name}")

        elif isinstance(feedback_data, list):
            if not feedback_data:
                st.info(f"No suggestions found for {section_name.capitalize()}.")
            else:
                for fb in feedback_data:
                    suggestion = escape(fb.get('suggestion', ''))
                    issues = ', '.join(fb.get('issues', []))
                    is_skills_section = section_name.lower() == "skills"

                    if fb.get('original') is not None:
                        original = escape(fb.get('original', ''))
                        st.markdown(f"""
                        <div style="margin-bottom: 1em; padding: 1em; border: 1px solid #eee; border-radius: 5px;">
                            <p>❌ <b>Original:</b> <span style="background-color:#ffcccc; padding: 2px 4px; border-radius: 3px;">{original}</span></p>
                            {(f'<p>✅ <b>Suggestion:</b> <span style="background-color:#ccffcc; padding: 2px 4px; border-radius: 3px;">{suggestion}</span></p>' if suggestion else '')}
                            {(f'<p>🏷️ <b>Issues:</b> <span style="color:#b22222;">{issues}</span></p>' if issues else '')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        label = "Suggested Skill Addition" if is_skills_section else "Potential Addition"
                        st.markdown(f"""
                        <div style="margin-bottom: 1em; padding: 1em; border: 1px solid #d3edff; border-radius: 5px;">
                            <p>✨ <b>{label}:</b> <span style="background-color:#e6f7ff; padding: 2px 4px; border-radius: 3px;">{suggestion}</span></p>
                        </div>
                        """, unsafe_allow_html=True)

        elif isinstance(feedback_data, dict) and "error" in feedback_data:
            st.error(f"⚠️ Analyzer Error for {section_name.capitalize()}: {feedback_data['error']}")
            if "raw_analysis" in feedback_data:
                st.markdown(f"<pre>{escape(feedback_data['raw_analysis'])}</pre>", unsafe_allow_html=True)

        else:
            st.warning(f"⚠️ Unexpected format for section: {section_name}")

# Run
load_and_display_results()
