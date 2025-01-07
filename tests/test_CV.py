import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
from enum import Enum
from backend.main import app, generate_tailored_plain_resume
from backend.models import AIModel
from backend.models.templates import ResumeTemplate, Template_Details

# Initialize test client
client = TestClient(app)

# Test data fixtures
@pytest.fixture
def sample_resume():
    return """
    John Doe
    Software Engineer
    
    Experience:
    - Senior Developer at Tech Corp (2020-2023)
    - Junior Developer at Start-up Inc (2018-2020)
    
    Education:
    - BS in Computer Science, University of Technology (2018)
    """

@pytest.fixture
def sample_job_description():
    return """
    Looking for a Senior Software Engineer with:
    - 5+ years of Python experience
    - Strong background in web development
    - Experience with cloud technologies
    """

@pytest.fixture
def mock_tailored_resume():
    return {
        "tailored_resume": """
        John Doe
        Senior Software Engineer
        
        Professional Experience:
        Tech Corp (2020-2023)
        - Led Python development team on cloud-based projects
        - Implemented web applications using modern frameworks
        
        Start-up Inc (2018-2020)
        - Developed and maintained Python applications
        - Worked on web development projects
        
        Education:
        BS in Computer Science, University of Technology (2018)
        """
    }

# Unit tests for create_tailored_plain_resume function
class TestCreateTailoredPlainResume:
    def test_successful_resume_creation(self, sample_resume, sample_job_description, mock_tailored_resume):
        with patch('openai_wrapper.client.beta.chat.completions.parse') as mock_openai:
            # Configure mock
            mock_response = Mock()
            mock_response.choices = [
                Mock(message=Mock(content=json.dumps(mock_tailored_resume)))
            ]
            mock_openai.return_value = mock_response
            
            # Call function
            result = generate_tailored_plain_resume(
                resume=sample_resume,
                job_description=sample_job_description,
                model=AIModel.gpt_4o_mini,
                template=ResumeTemplate.Blue_Modern_Resume
            )
            
            # Verify results
            # Test whether the output resume is string or not
            assert isinstance(result, str)
            # Test whether the output resume contains tailored information
            assert "Senior Software Engineer" in result
            assert "Tech Corp" in result

            mock_openai.assert_called_once()
            call_args = mock_openai.call_args[1]
            # Test whether the used model is the default one
            assert call_args['model'] == AIModel.gpt_4o_mini
            # Test the roles in the messages of ChatGPT
            assert len(call_args['messages']) == 2
            assert call_args['messages'][0]['role'] == "system"
            assert call_args['messages'][1]['role'] == "user"

    @pytest.mark.parametrize("template", list(ResumeTemplate))
    def test_different_template_pages(self, sample_resume, sample_job_description, mock_tailored_resume, template):
        with patch('openai_wrapper.client.beta.chat.completions.parse') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [
                Mock(message=Mock(content=json.dumps(mock_tailored_resume)))
            ]
            mock_openai.return_value = mock_response
            
            
            result = generate_tailored_plain_resume(
                resume=sample_resume,
                job_description=sample_job_description,
                model=AIModel.gpt_4o_mini,
                template=template
                )
                
            call_content = mock_openai.call_args[1]['messages'][1]['content']
            # Test the number of pages for each template 
            assert str(Template_Details[template]['num_pages']) in call_content

    @pytest.mark.parametrize("model", [AIModel.gpt_4o_mini, AIModel.gpt_4o])
    def test_different_models(self, sample_resume, sample_job_description, mock_tailored_resume, model):
        with patch('openai_wrapper.client.beta.chat.completions.parse') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [
                Mock(message=Mock(content=json.dumps(mock_tailored_resume)))
            ]
            mock_openai.return_value = mock_response
            
            result = generate_tailored_plain_resume(
                resume=sample_resume,
                job_description=sample_job_description,
                model=model
            )
            # Test does the app work with different GPT models
            assert mock_openai.call_args[1]['model'] == model
    
    
    def test_api_error_handling(self, sample_resume, sample_job_description):
        with patch('openai_wrapper.client.beta.chat.completions.parse') as mock_openai:
            mock_openai.side_effect = Exception("API Error")
            
            with pytest.raises(Exception) as exc_info:
                result = generate_tailored_plain_resume(
                    resume=sample_resume,
                    job_description=sample_job_description
                )
            # Test whether the app handle API error
            assert "API Error" in str(exc_info.value)

# Integration tests for the GET endpoint
class TestTailoredResumeEndpoint:
    def test_successful_request(self, sample_resume, sample_job_description, mock_tailored_resume):
        with patch('openai_wrapper.create_tailored_plain_resume') as mock_create_resume:
            mock_create_resume.return_value = mock_tailored_resume['tailored_resume']
            
            response = client.get(
                "/generate-tailored-plain-resume",
                params={
                    "resume": sample_resume,
                    "job_description": sample_job_description,
                    "model": AIModel.gpt_4o_mini.value,
                    "template": ResumeTemplate.MTeck_resume.value
                }
            )
            # Test whether request works correctly
            assert response.status_code == 200
            assert "Senior Software Engineer" in response.json()
    
    def test_missing_parameters(self):
        response = client.get("/generate-tailored-plain-resume")
        # Test whether request gives error when it is not given parameters
        assert response.status_code == 422
    
    def test_invalid_model(self, sample_resume, sample_job_description):
        response = client.get(
            "/generate-tailored-plain-resume",
            params={
                "resume": sample_resume,
                "job_description": sample_job_description,
                "model": "invalid_model",
                "template": ResumeTemplate.Blue_Modern_Resume.value
            }
        )
        # Test whether request gives error when it is given invalid model
        assert response.status_code == 422
    
    def test_invalid_template(self, sample_resume, sample_job_description):
        response = client.get(
            "/generate-tailored-plain-resume",
            params={
                "resume": sample_resume,
                "job_description": sample_job_description,
                "model": AIModel.gpt_4o_mini.value,
                "template": "invalid_template"
            }
        )
        # Test whether request gives error when it is given invalid template
        assert response.status_code == 422


                