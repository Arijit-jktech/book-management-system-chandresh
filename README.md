# Book Management System

A modern, production-ready RESTful API for managing books and reviews with AI-powered summarization capabilities.

## Features

- **Book Management** - Complete CRUD operations for books
- **Review System** - Users can rate and review books with aggregated ratings
- **AI Summarization** - Automatic book summary generation using Groq's LLM API
- **Authentication** - Secure JWT-based user authentication
- **Recommendations** - Smart book recommendations based on ratings
- **Async Architecture** - Built with FastAPI and async SQLAlchemy for high performance
- **Docker Ready** - Containerized deployment with Docker Compose

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy (Async)
- **Authentication**: JWT with passlib
- **AI**: Groq API (Llama 3.3)
- **Testing**: Pytest

## Quick Start

### Prerequisites

- Python 3.9+
- pip
- (Optional) Docker & Docker Compose

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book_management_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Groq API key:
   ```env
   LLM_API_KEY=your_groq_api_key_here
   ```
   
   Get a free API key at [Groq Console](https://console.groq.com/)

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

### Docker Setup

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API key
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Books
- `GET /api/v1/books/` - List all books
- `POST /api/v1/books/` - Create new book (auth required)
- `GET /api/v1/books/{id}` - Get book by ID
- `PUT /api/v1/books/{id}` - Update book (auth required)
- `DELETE /api/v1/books/{id}` - Delete book (auth required)

### Reviews
- `GET /api/v1/reviews/` - List all reviews
- `POST /api/v1/reviews/` - Create review (auth required)
- `GET /api/v1/reviews/{id}` - Get review by ID
- `PUT /api/v1/reviews/{id}` - Update review (auth required)
- `DELETE /api/v1/reviews/{id}` - Delete review (auth required)

### AI Features
- `POST /api/v1/generate-summary` - Generate summary from text (auth required)
- `POST /api/v1/books/{id}/generate-summary` - Generate and save book summary (auth required)
- `GET /api/v1/books/{id}/summary` - Get book with summary and average rating
- `GET /api/v1/recommendations` - Get recommended books

## Usage Example

1. **Sign up**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password123"}'
   ```

2. **Login**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -d "username=user@example.com&password=password123"
   ```

3. **Create a book** (use token from login)
   ```bash
   curl -X POST "http://localhost:8000/api/v1/books/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"1984","author":"George Orwell","genre":"Dystopian","year_published":1949}'
   ```

4. **Generate AI summary**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/books/1/generate-summary" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
book_management_system/
├── app/
│   ├── api/
│   │   ├── deps.py           # Dependencies
│   │   └── v1/
│   │       └── endpoints/    # API endpoints
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── security.py       # Auth utilities
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   └── main.py               # Application entry
├── tests/                    # Test suite
├── .env.example              # Environment template
├── requirements.txt          # Dependencies
├── Dockerfile                # Docker image
└── docker-compose.yml        # Docker services
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./book_db.sqlite` |
| `SECRET_KEY` | JWT secret key | - |
| `LLM_API_KEY` | Groq API key | - |
| `LLM_BASE_URL` | Groq API base URL | `https://api.groq.com/openai/v1` |
| `LLM_MODEL` | AI model name | `llama-3.3-70b-versatile` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration time | `30` |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
