# Çimsa Smart Assistant 🤖💻

This project is a **desktop chatbot application** developed to provide **quick solutions for common IT support issues** at Çimsa.  
It combines **rule-based logic** with a lightweight **NLU (Natural Language Understanding)** approach.  
The application also features a modern **CustomTkinter interface**, offering a user-friendly chat experience. 🎯

---
🚀 Features
- **Quick answers to common IT issues:**
  - VPN connection problems
  - Outlook password reset
  - SAP login issues
  - Printer / OneDrive / Teams problems
- **Ticket Creation Process**:
  - Step-by-step collection of **Title → Detail → Priority (urgent/normal)**
  - Optional **screenshot attachment**
- **NLU Support**:
  - Can handle typos (e.g., `vpn bağlnmıyo`)
  - Provides clickable suggestions when unclear
- **Corporate Information Module**:
  - Çimsa mission & vision
  - Website
  - Company history
  - CEO information
  - Sabancı Holding background
- **Modern UI Design**:
  - CustomTkinter-based, dark theme support
  - User & bot message bubbles
  - Quick access buttons in sidebar (VPN, Outlook, SAP, etc.)


---
🛠️ Technologies Used
- **Python 3.11**
- **CustomTkinter** → modern GUI
- **Pillow (PIL)** → logo & image handling
- **fuzzywuzzy + python-Levenshtein** → fuzzy text matching
- **Regex (re)** → rule-based intent routing
- **JSON** → intent & response database

---
📂 Project Structure
Cimsa_Chatbot/
│
├── gui_app.py # GUI (CustomTkinter)
├── chatbot_logic.py # Chatbot logic (intents + NLU + rules)
├── faq.json # Intent-response dataset
├── requirements.txt # Required libraries
├── logo.png # App logo
└── talep_log.txt # Ticket logs (optional)

---
⚡ Installation
    Clone the repository:
   ```bash
   git clone https://github.com/username/cimsa-chatbot.git
   cd cimsa-chatbot


   Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate  

   Install requirements:
   pip install -r requirements.txt

   Run the application:
   python gui_app.py

---
🔮 Future Improvements: 
 Web-based version (Flask / FastAPI + React UI)
 Integration with Microsoft Teams / Slack
 Advanced NLU (spaCy / scikit-learn / HuggingFace)



---
⚠️ Limitations
This chatbot was developed within a limited internship period.  
Due to time constraints, it may not always provide 100% correct answers.  
The main goal is to demonstrate the integration of rule-based logic, NLU, and a modern GUI in a practical IT support scenario.

---
👤 Author: Kağan Kılıç
🎓 Computer Engineering, Eskişehir Technical University

🔗 LinkedIn: linkedin.com/in/kagankilic

💻 GitHub: github.com/klckagan

📜 License

This project was developed for educational and internship purposes.
