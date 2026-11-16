# 🌿 EdibleIQ – Smart Food Inventory & Waste Management System

**Think Smart. Waste Less.**

EdibleIQ is a smart food inventory and waste management application built using Python and Streamlit. It helps users manage their food inventory, track expiry dates, monitor food waste, and make better use of available ingredients.

## ✨ Features

- **User Authentication:** Individual user signup and login.
- **Personalized Inventory:** Separate food inventory for each user.
- **Food Management:** Add, edit, and delete food items.
- **Expiry Tracking:** Monitor expiry dates and identify items that need attention.
- **Food Activity Tracking:** Track food that is used or wasted.
- **Waste Analytics:** Visualize food usage and waste through interactive charts.
- **AI Recipe Generator:** Generate recipe suggestions using available ingredients with Gemini API.
- **Data Persistence:** Store user accounts and individual inventory data using JSON files.

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Google Gemini API
- JSON
- Python-dotenv
- Hashlib

## 📁 Project Structure

```text
EdibleIQ/
│
├── app.py
├── auth.py
├── storage.py
├── logic.py
├── ai_suggestions.py
├── requirements.txt
├── .env
└── .gitignore
```

## ⚙️ Installation & Setup

1. Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

2. Navigate to the project folder:

```bash
cd EdibleIQ
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

5. Run the application:

```bash
streamlit run app.py
```

## 🔐 Data & Security

- User accounts are stored in a local JSON file.
- Each user's food inventory and activity data are stored separately.
- Passwords are hashed before storage.
- API credentials are kept in environment variables and excluded from Git using `.gitignore`.

**Note:** This project uses local JSON storage and is intended as a learning/portfolio application, not a production-ready multi-user deployment.

## 🎯 Project Goal

The goal of EdibleIQ is to encourage smarter food management, reduce avoidable food waste, and help users make better decisions about their food inventory.

---

**Built with 💚 using Python and Streamlit.**
