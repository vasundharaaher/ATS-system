from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Flask app
app = Flask(__name__)

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    jd = request.form.get('jd')
    uploaded_file = request.files.get('resume')
    
    if not jd or not uploaded_file:
        return jsonify({"error": "Job description and resume are required!"}), 400
    
    # Extract text from the PDF
    resume_text = input_pdf_text(uploaded_file)
    
    # Format the input for the AI model
    prompt = input_prompt.format(text=resume_text, jd=jd)
    
    # Get the response from Gemini
    response = get_gemini_response(prompt)
    
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)
