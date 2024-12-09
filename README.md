# TailorMade AI

**Automate the creation of tailored resumes and cover letters.**

TailorMade AI is an open-source project designed to help job seekers generate customized resumes and cover letters based on a given job description and their existing resume. Whether you’re targeting your dream job or applying to multiple positions, TailorMade AI simplifies the process with ease and precision.

## Features
- Generate tailored resumes and cover letters based on specific job descriptions.
- User-friendly FastAPI backend for seamless interaction.
- Simple setup and deployment for local use.

## Getting Started

Follow the steps below to set up and run the project locally.

### Prerequisites

Ensure you have the following installed:
- Git
- Python 3.7 or later

### Installation

1. Clone the repository to your local machine:
   ```bash
   git clone git@github.com:Form-pilot/TailorMade.git

2. Navigate to the project folder:
   ```bash
   cd TailorMade

3. Create a virtual environment:
   ```bash
   python3 -m venv .venv

4. Activate the virtual environment:
   - On macOS/Linux:
      ```bash
      source .venv/bin/activate
   - On Windows:
      ```bash
      .venv\Scripts\activate

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

6. Set up your environment variables:
   - Create a .env file in the project root.
   - Refer to envs.py for the required variables.
   - Important: Never push this file to your remote repository as it contains sensitive data.

7. Run the project:
   ```bash
   uvicorn main:app --reload

8. Access the API documentation:

   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to explore and test the API.

## Usage

Use the API endpoints to:
   - Upload your current resume.
   - Input the job description.
   - Generate tailored resumes and cover letters in seconds.

## Support & Contributions

We welcome contributions and feedback to improve TailorMade AI.

### Join our Community

- For support and updates, join our Telegram group: <div align="center">[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
)](https://t.me/+GN3-DufToPU4OTA0)</div>
- For development discussions and collaboration, join our dev chat: <div align="center">[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
)](https://t.me/+a8Cz2QqZWRdkMzI0)</div>

### How to Contribute

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
4. Push to the branch:
   ```bash
   git push origin feature-name
5. Open a pull request.

### Happy Job Hunting!

Let TailorMade AI empower your job applications with precision-crafted resumes and cover letters.