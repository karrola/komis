# KOMIS - web application for a car lot

Project was created in collaboration with @pirate1rat

## Technologies

Python, Django, SQLite, HTML5 + DjangoTemplates, Bootstrap 5

## Features

- browsing offers (with filters)
- adding offers to favourites
- adding sales offers with automatic ML-based price estimation (based on a trained machine learning regression model)
- admin panel supported by django-admin

## Setup instructions

1. Clone repository
2. (advised) Create virtual environment
3. Install requirements
   ```
   pip install -r requirements.txt
   ```
4. Create .env using .env.example
5. Apply database migrations
   ```
   py manage.py migrate       # Windows
   python3 manage.py migrate  # Linux / macOS
   ```
6. To use the Django admin panel, create a superuser:
   ```
   py manage.py createsuperuser       # Windows
   python3 manage.py createsuperuser  # Linux / macOS
   ```
7. Import sample offers
   ```
   py manage.py import_offers prepared_car_sales.csv       # Windows
   python3 manage.py import_offers prepared_car_sales.csv   # Linux / macOS
   ```
8. Run the development server

   ```
   py manage.py runserver       # Windows
   python3 manage.py runserver  # Linux / macOS
   ```

   The application will be available at http://127.0.0.1:8000/

   The admin panel is available at http://127.0.0.1:8000/admin/
