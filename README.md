# 🧠 DRDO-AI-Document-Verifier
This AI-driven system automates recruitment document processing by leveraging Google Cloud Vision and Gemini for advanced OCR and multilingual document understanding. It efficiently extracts and validates critical documents such as certificates and scorecards, ensuring accurate verification against user inputs.
Built on a robust Django/Python backend, the platform features a secure, user-friendly dashboard for seamless management and monitoring. By eliminating manual errors and accelerating the verification workflow, this solution significantly enhances operational efficiency for organizations like RAC–DRDO.

## 🔎 Core Capabilities

🔐 **Secure User Access** — Streamlined signup and login system for applicants ensuring data privacy  
📝 **Comprehensive Form Intake** — Capture detailed personal, educational, and professional information  
📁 **Robust Document Upload** — Supports PDFs including identity proofs, certificates, and scorecards  
🧠 **AI-Driven Data Extraction** — Utilizes Google Cloud OCR and NLP to intelligently extract both structured and freeform content  
✔️ **Automated Data Validation** — Cross-checks extracted document data with submitted form entries for consistency  
📈 **Insightful Discrepancy Analysis** — Detects and visually highlights mismatches with accuracy metrics  
📊 **Interactive Dashboard** — Real-time monitoring of document processing status and verification outcomes  

## ⚙️ Tech Stack

**🖥️ Backend:** Django, Python  
**🌐 Frontend:** HTML, CSS, Bootstrap, Django Templates  
**🗄️ Database:** SQLite  
**📄 Document Parsing:** Tesseract OCR, PyMuPDF, PDFMiner, LayoutLM *(optional)*  
**📊 Visualization:** Matplotlib, Plotly  
**🔐 Authentication:** Django Authentication System  

## 🚀 Getting Started

### 📦 Prerequisites
- Python 3.8 or higher  
- pip (Python package manager)  
- Virtualenv (recommended for isolated environments)

### 🛠️ Installation & Setup

#### Clone the repository
git clone https://github.com/your-username/idp-system.git
cd idp-system

#### Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate

#### Install required packages
pip install -r requirements.txt

#### Apply migrations
python manage.py migrate

#### Run the server
python manage.py runserver
