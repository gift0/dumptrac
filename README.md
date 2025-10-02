# dumpTrac

Smart Waste Management Platform - dumpTrac

## Overview

dumpTrac is a web-based platform for reporting, tracking, and managing waste bins in urban environments. It enables citizens to report full bins, agencies to monitor bin status, and provides a dashboard for real-time updates and location mapping.

## Features
- Report full waste bins with location and geocoordinates
- Agency dashboard with map and recent reports
- Real-time bin status updates
- Responsive frontend UI
- FastAPI backend with SQLAlchemy ORM
- PostgreSQL database support

## Project Structure
```
frontend/
  index.html
  dashboard.html
  style.css
  app.js
  assests/
    dumptrac_favicon.png
    dumpTrac_home.mp4
    dumptrac_waste.png
    dumpTrac.png
backend/
  main.py
  requirements.txt
  app/
    database.py
    models.py
    routes.py
    schemas.py
migrations/
  ...
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js (optional, for frontend tooling)
- PostgreSQL

### Backend Setup
1. Navigate to the `backend` folder.
2. Create and activate a Python virtual environment:
   ```sh
   python -m venv env
   env\Scripts\activate  # Windows
   source env/bin/activate  # macOS/Linux
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up your database connection in `.env` or `DATABASE_URL`.
5. Run migrations (if any):
   ```sh
   alembic upgrade head
   ```
6. Start the backend server:
   ```sh
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Open `index.html` and `dashboard.html` in your browser.
2. Ensure the backend API is running for full functionality.

## API Endpoints
- `POST /api/bins` — Create or update a bin
- `GET /api/bins` — List bins
- `GET /api/bins/{bin_id}` — Get bin details
- `POST /api/reports` — Report a full bin
- `GET /api/reports` — List reports
- `PUT /api/reports/{report_id}/clear` — Mark report as cleared

## Technologies Used
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Leaflet.js (map)
- HTML/CSS/JavaScript

## License
MIT

## Author
Gift Maduabuchi
