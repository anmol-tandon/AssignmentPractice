from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str
    publication_year: int

class Review(BaseModel):
    text: str
    rating: int

books_db = []
reviews_db = []

@app.post("/books/")
def add_book(book: Book):
    books_db.append(book)
    return {"message": "Book added successfully"}

@app.post("/reviews/{book_id}")
def submit_review(book_id: int, review: Review):
    if book_id < 0 or book_id >= len(books_db):
        raise HTTPException(status_code=404, detail="Book not found")
    
    reviews_db.append({"book_id": book_id, **review.dict()})
    return {"message": "Review submitted successfully"}

@app.get("/books/")
def get_books(author: Optional[str] = None, publication_year: Optional[int] = None):
    filtered_books = books_db
    if author:
        filtered_books = [b for b in filtered_books if b.author == author]
    if publication_year:
        filtered_books = [b for b in filtered_books if b.publication_year == publication_year]
    return filtered_books

@app.get("/reviews/{book_id}")
def get_reviews(book_id: int):
    if book_id < 0 or book_id >= len(books_db):
        raise HTTPException(status_code=404, detail="Book not found")
    
    return [review for review in reviews_db if review['book_id'] == book_id]
