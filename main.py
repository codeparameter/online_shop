#!/usr/bin/env python
"""Django-style management script for Flask application"""
import os
from flask.cli import FlaskGroup
from project import create_app, db

app = create_app()
cli = FlaskGroup(create_app=create_app)

@cli.command("init-db")
def init_db():
    """Initialize the database."""
    print(os.getenv("DATABASE_URL"))
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

@cli.command("drop-db")
def drop_db():
    """Drop all database tables."""
    with app.app_context():
        db.drop_all()
        print("Database dropped successfully!")

if __name__ == '__main__':
    cli()
