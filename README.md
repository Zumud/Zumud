# TailorMade AI

<div align="center">

![TailorMade Logo](https://img.shields.io/badge/TailorMade-AI-blue?style=for-the-badge)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)

</div>

**TailorMade AI** is an open-source platform that helps job seekers automatically generate customized resumes and cover letters tailored to specific job descriptions using AI.

## 🌟 Features

- 🧠 **AI-Powered Customization**: Tailors your resume and cover letter to match job descriptions
- 📝 **Document Generation**: Creates professional-looking PDFs with various templates
- 🔄 **Application Question Answering**: Helps craft responses to common application questions
- 🛠️ **Resume Editor**: Built-in tools for quick edits and updates
- 🔒 **User Account System**: Save your resume and settings for future use

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

TailorMade consists of two main components:

1. **Backend**: A FastAPI application that handles data processing, AI integration, and document generation
2. **Frontend**: A Streamlit interface for user interaction

## 💻 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9 or later
- Git
- Virtual environment tool (`venv`, `virtualenv`, etc.)

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/Form-pilot/TailorMade.git
cd TailorMade
```

2. **Create and activate a virtual environment**

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the root directory with the following required variable:

```
OPEN_AI_KEY=your_openai_api_key
```

The following variables are optional and will use sensible defaults if not specified:

```
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
# Start the Streamlit frontend
streamlit run frontend/app.py
```

The web application will be available at [http://localhost:8501](http://localhost:8501)

## 📚 API Documentation

Once your backend is running, you can access:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🤝 Contributing

We welcome contributions to TailorMade AI! To contribute:

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

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by the TailorMade AI Team</sub>
</div>
