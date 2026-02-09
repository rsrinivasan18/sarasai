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

🚧 **Week 2** - Database layer integration complete

**Current Features:**
- ✅ RESTful API with FastAPI
- ✅ MVC architecture (Model-View-Controller)
- ✅ Live market data via Alpha Vantage API
- ✅ SQLite database with comprehensive schema
- ✅ Database-backed portfolio management
- ✅ CRUD operations for positions and transactions
- ✅ Stock data endpoints with real-time prices
- ✅ Auto-generated API documentation

## 🏗️ Tech Stack

- **Backend:** Python 3.11, FastAPI
- **Database:** SQLite (production ready for PostgreSQL)
- **Data:** Alpha Vantage API, SQLAlchemy ORM
- **Future:** PostgreSQL, Redis, LangChain

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
- [x] Day 3: Real API integration (Alpha Vantage) ✅
- [x] Week 2: Database layer (SQLite + SQLAlchemy) ✅
- [ ] Week 3: User authentication

---

## 📄 License

MIT License

Copyright (c) 2026 Srinivasan Ramarao

---

*Ancient wisdom. Modern AI. Flowing insights.*  
*Built with 🦢 by Srinivasan Ramarao*