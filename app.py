# /backend/app.py

import os
from app import create_app
from app.models import db

# Get config from environment or use development by default
config_name = os.environ.get('FLASK_CONFIG', 'default')
app = create_app(config_name)

@app.cli.command("init-db")
def init_db():
    """Initialize the database with tables and initial data."""
    db.create_all()
    print("Initialized the database.")

@app.cli.command("seed-db")
def seed_db():
    """Seed the database with sample data."""
    from app.utils.seeder import seed_database
    seed_database()
    print("Database seeded with sample data.")

if __name__ == '__main__':
    app.run(host='0.0.0.0')