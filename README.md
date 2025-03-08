# English Learning Platform API

A FastAPI-based backend service for an English learning platform featuring vocabulary management, AI-powered chatbot assistance, and error detection.

## Features

- **Authentication System**
  - User registration and login
  - JWT-based authentication
  - Token refresh mechanism

- **Vocabulary Management**
  - Create and manage vocabulary lists
  - Add/edit/delete vocabulary items
  - Support for images, definitions, and examples
  - Progress tracking

- **AI-Powered Features**
  - Intelligent chatbot for English learning assistance
  - Grammar and error detection
  - Mixed language (English-Vietnamese) sentence analysis
  - Smart response suggestions

- **Content Management**
  - Practice questions and exercises
  - Multiple question types support
  - Audio and image content support

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **AI Integration**: 
  - Google Generative AI
  - OpenAI
  - LangChain

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with:
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/v1/register` - User registration
- `POST /api/v1/login` - User login

### Vocabulary
- `GET /api/v1/vocabulary-list` - Get vocabulary lists
- `POST /api/v1/vocabulary` - Create vocabulary list
- `PATCH /api/v1/vocabulary` - Update vocabulary list
- `DELETE /api/v1/vocabulary/{list_id}` - Delete vocabulary list
- `POST /api/v1/vocabulary-item` - Add vocabulary item
- `PATCH /api/v1/vocabulary-item` - Update vocabulary item
- `DELETE /api/v1/vocabulary-item/{item_id}` - Delete vocabulary item

### AI Features
- `POST /api/v1/messages` - Chat with AI assistant
- `POST /api/v1/suggestions` - Get response suggestions

### Practice Content
- `GET /api/v1/practice/{practice_type}` - Get practice questions

## Project Structure

```
app/
├── ai/                 # AI-related modules
├── api/               # API endpoints
│   └── v1/           
├── db/                # Database configuration
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── services/          # Business logic
└── main.py           # Application entry point
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
