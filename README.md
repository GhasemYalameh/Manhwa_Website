# Manhwa Platform

A comprehensive Django-based web platform for managing and reading manhwa content with advanced features including user authentication, ratings, comments, and ticketing system.

## Features

### Core Functionality
- **Manhwa Management**: Complete CRUD operations for manhwa content with episodes, genres, and studio information
- **User System**: Custom phone-based authentication with watchlist functionality
- **Rating System**: 5-star rating system with detailed statistics
- **Comments & Reactions**: Nested comments (up to 3 levels) with like/dislike reactions
- **View Tracking**: Automatic view counting and tracking
- **Ticketing System**: Support ticket management for user-admin communication
- **Rich Text Editor**: CKEditor 5 integration for content creation

### Technical Features
- RESTful API with JWT authentication
- Multi-language support (Persian/English) with django-rosetta
- Docker containerization with PostgreSQL
- Optimized database queries with prefetch_related and select_related
- Custom pagination and filtering
- Comprehensive test coverage

## Tech Stack

- **Backend**: Django 5.2.3, Django REST Framework 3.16.0
- **Database**: PostgreSQL 14
- **Authentication**: JWT (Simple JWT), Djoser
- **Editor**: CKEditor 5
- **Containerization**: Docker & Docker Compose
- **Other**: django-filter, django-debug-toolbar, Pillow

## Project Structure

```
.
├── accounts/              # User authentication and profiles
├── manhwas/              # Core manhwa functionality
├── config/               # Django project settings
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded content
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
└── requirements.txt      # Python dependencies
```

## Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone git@github.com:GhasemYalameh/Manhwa_Website.git
cd Manhwa_Website
```

2. **Create `.env` file** in the project root:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DB_ENGINE=postgresql
DB_NAME=manhwa_db
DB_USER=postgres
.
.
# And other environment variables in .env.example file.
```

3. **Build and run with Docker Compose**
```bash
docker compose up --build
```

4. **Run migrations** (in a new terminal):
```bash
docker compose exec web python manage.py migrate
```

5. **Create superuser**
```bash
docker compose exec web python manage.py createsuperuser
```

6. **Access the application**
- Web: http://localhost:8000
- Admin: http://localhost:8000/admin
- API: http://localhost:8000/api

### Local Development Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables** (create `.env` file as shown above)

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

## API Documentation

### Authentication Endpoints
```
POST /auth/jwt/create/          # Login (get JWT tokens)
POST /auth/jwt/refresh/         # Refresh access token
POST /auth/users/               # Register new user
```

### Manhwa Endpoints
```
GET    /api/manhwas/                    # List all manhwas
POST   /api/manhwas/                    # Create manhwa (admin)
GET    /api/manhwas/{id}/               # Manhwa detail
POST   /api/manhwas/{id}/set_view/      # Track view
POST   /api/manhwas/{id}/rate/          # Rate manhwa
GET    /api/manhwas/{id}/rate/          # Get user's rating
```

### Comment Endpoints
```
GET    /api/manhwas/{id}/comments/              # List comments
POST   /api/manhwas/{id}/comments/              # Create comment
GET    /api/manhwas/{id}/comments/{cid}/        # Comment detail
GET    /api/manhwas/{id}/comments/{cid}/replies/ # Get replies
POST   /api/manhwas/{id}/comments/{cid}/reaction/ # Like/dislike
PATCH  /api/manhwas/{id}/comments/{cid}/        # Update comment
DELETE /api/manhwas/{id}/comments/{cid}/        # Delete comment
```

### Episode Endpoints
```
GET /api/manhwas/{id}/episodes/         # List episodes
GET /api/manhwas/{id}/episodes/{eid}/   # Episode detail
```

### Ticket Endpoints
```
GET  /api/tickets/          # List user tickets
POST /api/tickets/          # Create ticket
GET  /api/tickets/{id}/     # Ticket messages
POST /api/tickets/{id}/     # Add message to ticket
```

## Authentication

The API uses JWT authentication. Include the token in request headers:

```bash
Authorization: JWT <access_token>
```

Example login:
```bash
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09123456789", "password": "yourpassword"}'
```

## Key Models

### CustomUser
- Phone-based authentication (Iranian format: 09XXXXXXXXX)
- Username, email, first_name, last_name
- ManyToMany relationship with Manhwa (watchlist)

### Manhwa
- Titles (English/Persian), summary, cover image
- Season, day of week, publication date
- ManyToMany: genres
- ForeignKey: studio
- Tracked: views_count, last_upload

### Comment
- Nested structure (max 3 levels)
- Like/dislike reactions
- Automatic level calculation

### Episode
- Auto-incrementing episode numbers
- File upload with organized directory structure
- Download tracking

## Running Tests

```bash
# Using Docker
docker compose exec web python manage.py test

# Local
python manage.py test
```

Tests cover:
- API endpoints
- Authentication
- Comment reactions
- Permissions
- Database queries optimization

## Development Tools

### Debug Toolbar
Access at `/__debug__/` when DEBUG=True

### Django Admin
Customized admin interface with:
- Autocomplete fields
- Inline editing
- Custom filters and actions
- Persian language support

### Rosetta (Translation Management)
Access at `/rosetta/` to manage translations

## Media Files

Files are organized as:
```
media/
└── Manhwa/
    └── {manhwa-title}/
        └── Season-{number}/
            ├── Covers/
            │   └── cover.jpg
            └── Episodes/
                └── episode-files
```

## Performance Optimization

- Prefetch and select_related for query optimization
- Cached properties for expensive operations
- Custom pagination (10 items per page)
- Database indexing on frequently queried fields
- Atomic transactions for data integrity

## Security Features

- CSRF protection
- JWT token authentication
- Phone number validation with regex
- HTML tag sanitization in user input
- Permission-based access control
- Secure password hashing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is currently in active development and is primarily intended as a portfolio demonstration.

For any inquiries regarding usage or collaboration, please feel free to contact me.

## Support

For issues and questions:
- Create a ticket through the platform
- Contact the development team
- Check existing documentation

## Roadmap

- [x] RESTful API with JWT authentication
- [x] Nested comments system
- [x] Docker containerization
- [ ] Redis caching for improved performance
- [ ] Celery for asynchronous task processing
- [ ] Enhanced search functionality
- [ ] Real-time notifications
---

**Note**: This project is in active development. Some features may be subject to change.