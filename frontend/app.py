import streamlit as st
import requests
from typing import Dict, Any
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # This is to add the root directory to sys.path. We need to remove this in future
from backend.models.ai_models import AIModel
from backend.models.templates import ResumeTemplate

BACK_END_URL = "http://localhost:8000"

class ResumeApp:
    def __init__(self, bak_end_url: str = BACK_END_URL):
        self.back_end_url = bak_end_url
    
    def call_api(self, endpoint: str, data: Dict[str, Any], query_params: Dict[str, Any] = None) -> Dict:
        headers = {}
        if 'access_token' in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        # Prepare the URL with query parameters if provided
        url = f"{self.back_end_url}/func/{endpoint}"
        
        # Make the request with both query parameters and JSON body
        response = requests.post(url, params=query_params, json=data, headers=headers)
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
        return response.json()

    
    def login(self, username: str, password: str) -> Dict:
        try:
            response = requests.post(
                f"{self.back_end_url}/auth/login",
                data={"username": username, "password": password} 
            )
            if response.status_code == 200:
                # Store user data in session state
                st.session_state.user_data = {
                "username": response.json().get("username"),  # Get username from response
                "id": response.json().get("user_id")          # Get user_id from response
                }
                st.session_state.access_token = response.json().get("access_token")
                return response.json()
            else:
                st.error(f"Login failed: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return None

    def signup(self, username: str, password: str, email: str, initial_resume: str) :
        try:
            response = requests.post(
                f"{self.back_end_url}/auth/signup",
                json={
                    "username": username,
                    "password": password,
                    "email": email,
                    "initial_resume": initial_resume if not initial_resume else "Empty"
                }
            )
            if response.status_code == 201:  # Changed to match backend status code
                return response.json()
            else:
                st.error(f"Signup failed: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            st.error(f"Signup error: {str(e)}")
            return None
    
    def update_resume(self, resume_content: str) :
        try:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            
            response = requests.put(
                f"{self.back_end_url}/auth/update_resume",
                json={"resume_content": resume_content},
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Update resume failed: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            st.error(f"Update resume error: {str(e)}")
            return None

    def get_resume(self) :
        try:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.get(f"{self.back_end_url}/auth/get_resume", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Get resume failed: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            st.error(f"Get resume error: {str(e)}")
            return None

def display_pdf(pdf_file_path):
    # Opening and reading the PDF file
    with open(pdf_file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    
    # Displaying the PDF
    st.markdown(pdf_display, unsafe_allow_html=True)

def show_auth_page(app: ResumeApp):
    st.title("Welcome to Resume Tailorer")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user_data = app.login(username, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                
    
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            initial_resume = st.text_area("Your Initial Resume", height=200)
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                result = app.signup(new_username, new_password, email, initial_resume)
                if result:
                    st.success("Account created successfully! Please login.")
                

    
def show_main_app(app:ResumeApp):
    st.title(f"Welcome back, {st.session_state.user_data['username']}!")

    # Sidebar for Configuration and Resume Management
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        st.header("Configuration")
        ai_model = st.selectbox("Select AI Model", [model.value for model in AIModel], index=0)
        resume_template = st.selectbox("Select Resume Template", [template.value for template in ResumeTemplate], index=2)
        
        # Resume Management
        st.header("Your Resume")
        resume_data = app.get_resume()
        current_resume = resume_data.get("resume_content", "") if resume_data else ""
        new_resume = st.text_area("Edit Resume", value=current_resume, height=300)

        if st.button("Update Resume"):
            if new_resume.strip():
                result = app.update_resume(new_resume)
                if result:
                    st.success("Resume updated successfully!")
                else:
                    st.error("Failed to update resume")

    # Middle Section: Job Description
    st.header("Job Description")
    job_description = st.text_area("Enter Job Description", height=200)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Generate Resume", "Generate Cover Letter", "Answer application questions", "CV Editor"])
    
    # Create profile data without job description
    profile_data = {
        "profile": {"resume": {"text": current_resume}, "username": st.session_state.user_data['username']},
        "tailoring_options": {
            "ai_model": ai_model,
            "resume_template": resume_template
        }
    }

    with tab1:
        if st.button("Check Eligibility"):
            if not job_description or job_description.strip() == "":
                st.error("Please enter a job description.")
            else:
                result = app.call_api("determine_eligibility", profile_data, query_params={"job_description": job_description})
                st.write("Eligibility:", result.get("eligibility", "N/A"))
                st.write("Reason:", result.get("reason", "No reason provided"))
        
        if st.button("Check Suitability"):
            if not job_description or job_description.strip() == "":
                st.error("Please enter a job description.")
            else:
                result = app.call_api("determine_suitability", profile_data, query_params={"job_description": job_description})
                st.write("Suitability:", result.get("suitability", "N/A"))
                st.write("Reason:", result.get("reason", "No reason provided"))
        
        if st.button("Generate Resume"):
            if not job_description or job_description.strip() == "":
                st.error("Please enter a job description.")
            else:
                result = app.call_api("generate-latex-resume-save", profile_data, query_params={"job_description": job_description})
                if "latex_code" in result and "pdf_file_path" in result:
                    # session_state shows that whether latex code is present or not, as in the cv_editor part, we want to edit the latex code
                    st.session_state['latex_code'] = result['latex_code']
                    pdf_file_path = result['pdf_file_path']
                    if os.path.exists(pdf_file_path):
                        st.success(f"PDF saved: {pdf_file_path}")
                        display_pdf(pdf_file_path)
                    else:
                        st.error("PDF file does not exist. Please try again.")
                else:
                    st.error("Unexpected response format from the API. Please try again.")

    with tab2:
        if st.button("Generate Cover Letter"):
            if not job_description or job_description.strip() == "":
                st.error("Please enter a job description.")
            else:
                cover_letter_text = app.call_api("generate-tailored-plain-coverletter", profile_data, query_params={"job_description": job_description})
                st.text_area("Generated Cover Letter", value=cover_letter_text, height=400)
                # Generate the PDF
                st.success(f"PDF generated successfully!")
    
    with tab3:
        question_description = st.text_area("Enter Question", height=200)
        if st.button("Generate answer"):
            if not question_description or question_description.strip() == "":
                st.error("Please enter a question.")
            elif not job_description or job_description.strip() == "":
                st.error("Please enter a job description.")
            else:
                # Add the question to the profile data
                question_data = profile_data.copy()
                question_data["question"] = {"description": question_description}
                result = app.call_api("answer-application-questions", question_data, query_params={"job_description": job_description})
                st.text_area("Generated Answer", value=result, height=400)
    
    with tab4:
        # There should be a latex code to display, as the purpose of this section is to edit the latex code
        if 'latex_code' not in st.session_state:
            st.session_state['latex_code'] = ""
            
        st.header("LaTeX Editor")
        edited_latex = st.text_area("Edit LaTeX Code", value=st.session_state['latex_code'], height=400)
        if st.button("Save Final PDF"):
            save_data = {
                "latex": {
                    "latex_code":edited_latex
                },
                "tailoring_options": {
                    "ai_model":ai_model,
                    "resume_template": resume_template
                }
            }
            result = app.call_api("save-latex-resume", save_data)
            if result.get('path'):
                st.success(f"PDF saved at: {result['path']}")
            else:
                st.error("An error occured. Please try again.")

def main():
    st.set_page_config(page_title="Resume Tailorer", layout="wide")
    app = ResumeApp()

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    

    # Show either auth page or main app based on login status
    if not st.session_state.logged_in:
        show_auth_page(app)
    else:
        show_main_app(app)


if __name__ == "__main__":
    main()