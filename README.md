# Sarasai (सरसाई)

**Where Wisdom Flows** 🦢

AI-powered investment analysis platform - Phase 1: Stock Analysis

---

## 👨‍💻 Author

**Srinivasan Ramarao**  
📧 Email: rsrinivasan18@gmail.com  
💼 LinkedIn: [Add your LinkedIn]  
🐙 GitHub: [Add your GitHub username]

---

## 🎯 About

Sarasai brings flowing intelligence to modern markets, combining ancient 
Vedic wisdom with cutting-edge AI technology. Named after Saraswati (सरस्वती), 
the goddess of knowledge and wisdom.

## 📊 Status

🚧 **Day 2** - MVC Architecture implemented, professional structure complete

**Current Features:**
- ✅ RESTful API with FastAPI
- ✅ MVC architecture (Model-View-Controller)
- ✅ Mock data from CSV (easy to swap to live data)
- ✅ Stock data endpoints
- ✅ Auto-generated API documentation

## 🏗️ Tech Stack

- **Backend:** Python 3.11, FastAPI
- **Data:** Pandas, CSV (transitioning to PostgreSQL)
- **Future:** LangChain, PostgreSQL, Redis

## 🚀 Quick Start
```bash
# Activate environment
venv\Scripts\activate

# Run server
uvicorn api.main:app --reload

# Visit
http://localhost:8000/docs
```

## 📁 Project Structure
```
sarasai/
├── api/              # API routes (View)
├── core/             # Models & Services (Model + Controller)
├── config/           # Configuration
├── data/             # Data sources
└── tests/            # Tests (coming soon)
```

## 📈 Progress

- [x] Day 1: Project setup, first endpoints ✅
- [x] Day 2: MVC architecture, CSV data integration ✅
- [ ] Day 3: Real API integration (Alpha Vantage)
- [ ] Week 2: PostgreSQL database
- [ ] Week 3: User authentication

---

## 📄 License

MIT License

Copyright (c) 2026 Srinivasan Ramarao

---

*Ancient wisdom. Modern AI. Flowing insights.*  
*Built with 🦢 by Srinivasan Ramarao*