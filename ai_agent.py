import google.generativeai as genai
import os

# Configure your API key (ensure you have this set in your terminal or hardcoded for the demo)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def find_best_matches(directory_data, interest, previous_matches=""):
    """Asks Gemini to pick the top 3 professors, aggressively excluding previous matches, and enforcing realistic honesty."""
    
    exclusion_rule = ""
    if previous_matches:
        exclusion_rule = f"""
        =========================================
        CRITICAL NEGATIVE CONSTRAINT:
        The user has already seen the following recommendations:
        {previous_matches}
        
        YOU ARE STRICTLY FORBIDDEN from recommending anyone mentioned in the text above. 
        You must pick the NEXT best 3 professors from the directory.
        =========================================
        """

    prompt = f"""
    You are an academic advisor. A student is looking for undergraduate research.
    Their specific research interest is: {interest}

    Here is the directory of available engineering faculty:
    {directory_data}
    
    {exclusion_rule}
    
    Based ONLY on the titles and departments provided in the directory, identify the top 3 closest matching professors for this student. 
    
    CRITICAL REALISM RULE: You must be highly realistic and honest. If the "best" available professors in this list are still a poor fit for the student's specific interest, you MUST explicitly state that. 
    
    For each of the 3 professors:
    - Format with a clear heading.
    - Explain why they were chosen as the closest option.
    - Explicitly state the "Reality Check": Is this actually a strong match, or is it a stretch? Highlight any major gaps between the student's interest and the professor's department.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Matching Error: {e}"

def generate_dossier(prof_data, major, interest):
    """Creates a deep-dive strategy guide for the student based on scraped lab data."""
    prompt = f"""
    You are an expert academic advisor. Create a dossier for the following student:
    Student Major: {major}
    Student Interest: {interest}

    Professor Details:
    Name: {prof_data['name']}
    Title: {prof_data['title']}
    Email: {prof_data.get('email', 'N/A')}

    Recent Lab/Research Data Scraped from their website:
    {prof_data.get('research_text', 'No extra research text found. Use your internal knowledge base to summarize their work.')}

    Write a strategic dossier. Include:
    1. Core Research Summary: What does this professor actually do?
    2. Connection to Student: How does the student's major/interest fit into this lab?
    3. The "Hook": Give the student 2 specific questions or topics to mention in an email that proves they read the professor's research.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Dossier Error: {e}"

def draft_outreach_email(prof_data, major, interest, dossier_text):
    """Takes the generated dossier and writes a highly optimized cold email."""
    prompt = f"""
    You are an expert career advisor. Based on the following student profile and professor dossier, write a professional, concise, and compelling cold email asking for an undergraduate research opportunity.

    Student Major: {major}
    Student Interest: {interest}
    Professor Name: {prof_data['name']}

    Professor Dossier/Context:
    {dossier_text}

    Rules for the email:
    1. Provide a strong, clear Subject Line at the top.
    2. Keep the body under 150 words.
    3. Seamlessly weave in one of the specific "hooks" from the dossier to prove the student actually understands their lab's work.
    4. Keep the tone academic, eager, and professional. Do not flatter excessively.
    5. End with a low-friction call to action (e.g., asking for a brief 10-minute chat).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Failed to draft email: {e}"