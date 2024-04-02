FastAPI CRUD with Caching
This FastAPI application provides CRUD (Create, Read, Update, Delete) operations for managing posts, with caching implemented for read operations.

Requirements
Python 3.9 or later
FastAPI
SQLAlchemy
psycopg2 (for PostgreSQL database)
cachetools

Installation

Clone the repository:
git clone <repository-url>

Install the dependencies:
poetry install pyproject.toml

Set up the database:
Configure your database connection in the database.py file.

Run the migrations to create the necessary tables:

alembic upgrade head


Run the FastAPI server:
main.py

Usage
Endpoints
GET /posts/getPosts: Retrieve all posts.
GET /posts/getPost: Retrieve a specific post by ID.
POST /posts/: Create a new post.
PUT /posts/{id}: Update an existing post.
DELETE /posts/{id}: Delete a post.


Example Usage

To retrieve all posts:
GET /posts/getPosts

To retrieve a specific post by ID:
GET /posts/getPost?id={post_id}

To create a new post:
POST /posts/
Content-Type: application/json
{
    "name": "New Post",
    "text": "This is the content of the new post."
}

To update an existing post:
PUT /posts/{post_id}
Content-Type: application/json
{
    "name": "Updated Post Title",
    "text": "Updated post content."
}

To delete a post:
DELETE /posts/{post_id}

Caching
This application implements caching for read operations (getPosts and getPost). Cached responses are stored in the database to improve performance and reduce the load on the server.

