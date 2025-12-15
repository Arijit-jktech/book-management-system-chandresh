import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_book_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/v1/books/",
        json={"title": "Test Book", "author": "Test Author"}
    )
    assert response.status_code == 401

# We need a helper to get auth headers, but for now let's test public endpoints if any
# The assignment says "Implement basic authentication for the API", implying most things are protected.
# My implementation protected create/update/delete, but read is public in my code?
# Let's check books.py
# create_book: protected
# read_books: public
# read_book: public
# update_book: protected
# delete_book: protected

@pytest.mark.anyio
async def test_read_books_empty(client: AsyncClient):
    response = await client.get("/api/v1/books/")
    assert response.status_code == 200
    assert response.json() == []
