# Zumud

<div align="center">

![Zumud Logo](/frontend/public/logos/zumud/combined.svg)
![Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg?style=for-the-badge)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.0.0+-000000.svg?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)

</div>

**Zumud** is a proprietary platform that helps job seekers automatically generate customized resumes and cover letters tailored to specific job descriptions using AI.

## 🌟 Features

- 🧠 **AI-Powered Resume Improvement**: Upload your existing resume and get AI-powered suggestions for improvement
- 📝 **Custom Resume Generation**: Generate tailored resumes based on job descriptions
- 📄 **Cover Letter Creation**: Automatically generate personalized cover letters
- ❓ **Application Question Answering**: Get AI-generated responses to common job application questions
- 📊 **Dashboard**: Manage your resume, applications, and profile settings in one place
- 🔒 **User Authentication**: Secure login and signup system with JWT authentication
- 📧 **Email Integration**: Send generated documents directly via email
- ☁️ **Cloud Storage**: Automatic backup of your documents to Google Drive

## 🌟 Key Features

- **Resume Tailoring**: Automatically customize your resume for each job application using advanced AI.
- **Cover Letter Generation**: Create personalized cover letters tailored to specific job descriptions.
- **Resume PDF Extraction**: Upload your existing resume in PDF format and the system will intelligently extract the text.
- **AI-Powered Resume Formatting**: Raw text from uploaded PDFs is transformed by AI into perfectly structured, clean formatting optimized for further processing.
- **Section Recognition**: AI automatically identifies and categorizes resume sections for better analysis.
- **Application Tracking**: Manage all your job applications in one place.
- **Interview Question Preparation**: Get customized answers for common interview questions based on your resume and the job description.
- **Professional PDF Output**: Download beautifully formatted PDFs for your resume and cover letter.
- **LaTeX Export**: Access the LaTeX source code of your documents for further customization.

## 📋 Table of Contents

- [Demo](#-demo)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [Community](#-community)
- [License](#-license)

## 🚀 Demo

*Add screenshots or a GIF of the application in action here*

## 🏗 Architecture

Zumud consists of two main components:

1. **Backend**: A FastAPI application that handles:
   - AI integration and document generation
   - User authentication and data management
   - Email and cloud storage integration
   - PDF generation and processing

2. **Frontend**: A Next.js application that provides:
   - Modern, responsive user interface
   - Real-time document preview
   - Interactive dashboard
   - Secure authentication flow

## 💻 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9 or later
- Node.js 18.0.0 or later
- Git
- Virtual environment tool (`venv`, `virtualenv`, etc.)

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/Form-pilot/Zumud.git
cd Zumud
```

2. **Set up the backend**

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

3. **Set up the frontend**

```bash
cd frontend
npm install
```

## 🔑 Environment Variables

Create a `.env` file in the root directory with the following required variables:

```
# Required
OPEN_AI_KEY=your_openai_api_key
GMAIL_APP_PASSWORD=your_gmail_app_password
ADD_GDRIVE_ZAP_URL=your_zapier_webhook_url

# Optional - only required for production environments
SECRET_KEY=your_secret_key_for_jwt  # Auto-generated if not set
ALGORITHM=HS256  # Default value
ACCESS_TOKEN_EXPIRE_MINUTES=720  # Default value
```

> ⚠️ **Note**: 
> - Never commit your `.env` file to version control.
> - For production environments, it's recommended to set a permanent SECRET_KEY to prevent users from being logged out when the server restarts.

## 🏃‍♂️ Running the Application

### Backend

```bash
# Start the FastAPI backend
uvicorn backend.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

### Frontend

```bash
# Start the Next.js frontend
cd frontend
npm run dev
```

The web application will be available at [http://localhost:3000](http://localhost:3000)

## 📚 API Documentation

Once your backend is running, you can access:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🤝 Contributing

We welcome contributions to Zumud! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please check out our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 👥 Community

Join our community to get help, share ideas, and collaborate:

- **Main Group**: [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/+GN3-DufToPU4OTA0)
- **Development Chat**: [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/+a8Cz2QqZWRdkMzI0)

## 📄 License

This project is proprietary software with all rights reserved. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.

---

<div align="center">
  <sub>Built with ❤️ by the Zumud Team</sub>
</div>
