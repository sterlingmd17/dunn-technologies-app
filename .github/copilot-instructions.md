# Dunn Technologies AI Agent Instructions

## Project Overview
This is a **Django 6.0.2 corporate marketing website** for Dunn Technologies (IT services in Greater Vancouver/Portland). The site is a simple brochure with contact lead generation.

## Architecture

### Key Components
- **`dunntechnologies/`** - Django project configuration (settings, WSGI, URL router)
- **`website/`** - Main Django app containing pages, forms, and views
- **Database** - SQLite (`db.sqlite3`), currently minimal schema (only Django auth/admin)
- **Frontend** - Bootstrap 5.3.3 (CDN) + custom CSS in `website/templates/website/` and `website/static/`

### Page Structure
- **Views** (`website/views.py`) - Function-based views for: home, services, service_area, about, contact
- **URLs** (`website/urls.py`) - Routes pages with Django `name=` attributes for template linking
- **Templates** (`website/templates/website/`) - Base template extends with block content pattern
- **Forms** (`website/forms.py`) - ContactForm with Bootstrap CSS classes (`form-control`)

### Email Integration  
**Contact form submission flow** (see `contact` view):
1. Form validation using `ContactForm` 
2. Send email via Django SMTP (`settings.DEFAULT_FROM_EMAIL`)
3. SMTP configured in settings: `smtp.yourprovider.com` on port 587
4. Email recipient currently hardcoded as `your_email@dunntech.com` - consider making this configurable

## Critical Patterns & Conventions

### Template System
- **Inheritance**: All pages extend `base.html` using Django block tags (`{% block content %}`, `{% block title %}`)
- **Navbar**: Uses Bootstrap navbar component with `ms-auto` for right-alignment; links use `{% url 'name' %}` syntax
- **Messages Framework**: Contact page displays success messages via `django.contrib.messages`
- **Static Files**: Load with `{% load static %}` at template top; CSS loads from CDN and `/website/static/website/css/site.css`

### Form Patterns
- Forms use Django's form class with `widget` customization
- Standard Bootstrap class applied: `form-control`, `form-select` (implied for future use)
- Email backend configured; failure mode uses `fail_silently=False` (will raise exception if email fails)

### URL Naming Convention
Routes use human-readable names: `home`, `services`, `service_area`, `about`, `contact`
Use these **exact** names when generating template links or reverse() calls.

## Developer Workflows

### Running the Development Server
```bash
# Activate virtual environment
dunn-technologies-app-venv\Scripts\activate  # Windows
# or: source dunn-technologies-app-venv/bin/activate  # Linux/Mac

# Run migrations (if models change)
python manage.py migrate

# Start dev server (runs on http://127.0.0.1:8000/)
python manage.py runserver
```

### Database Migrations
- Models are currently minimal; any new models added require:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### Admin Access
- Django admin panel at `/admin/` - use default auth system
- No custom admin classes configured yet

## Common Modifications

### Adding a New Page
1. Create a view function in `website/views.py` returning `render(request, "website/pagename.html")`
2. Add URL pattern to `website/urls.py` with a name: `path("pagename/", views.pagename, name="pagename")`
3. Create template file `website/templates/website/pagename.html` extending base.html
4. Link from navbar in `base.html` using `{% url 'pagename' %}`

### Modifying Contact Form  
- Edit `ContactForm` class in `website/forms.py`
- Update corresponding template `website/templates/website/contact.html` to match fields
- **Note**: Email recipient is currently hardcoded in views.py - extract to settings for configurability

## Known Issues & Technical Debt
- **Duplicate function**: `contact` view defined twice in `website/views.py` - keep second definition (more complete), remove first
- **Empty models**: `website/models.py` is unused; add if expanding features (blog, testimonials, case studies, etc.)
- **Test coverage**: `website/tests.py` empty - no tests written
- **Hardcoded values**: Email recipient should be configurable via settings or environment variable
- **DEBUG mode**: Currently `DEBUG=True` - must be `False` in production

## Environment Variables (Production)
When deploying, set via `.env` or environment:
- `SECRET_KEY` - Replace Django default (currently exposed in settings)
- `DEBUG` - Set to `False`
- `ALLOWED_HOSTS` - Configure for production domain
- `EMAIL_HOST_PASSWORD` - Set app-specific password for email sender
- Database connection if switching from SQLite

## Static Files & Frontend
- Bootstrap 5.3.3 loaded from CDN (no npm/bundler setup)
- Custom CSS in `website/static/website/css/site.css`
- Run `python manage.py collectstatic` before production deployment

## Git Workflow
- `.gitignore` configured for standard Python/Django project
- Virtual environment excluded from version control
- Database (`db.sqlite3`) should be excluded or synchronized carefully for team dev
