from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List

app = FastAPI()

books_db = []
reviews_db = []

# Pydantic models for data validation
class Book(BaseModel):
    title: str
    author: str
    publication_year: int

class Review(BaseModel):
    book_id: int
    text: str
    rating: int
    
@app.post("/books/", response_model=Book)
def add_book(book: Book):
    books_db.append(book)
    return book

@app.post("/reviews/", response_model=Review)
def submit_review(review: Review, background_tasks: BackgroundTasks):
    reviews_db.append(review)
    background_tasks.add_task(send_confirmation_email, review)
    return review

@app.get("/books/", response_model=List[Book])
def get_books(author: str = None, publication_year: int = None):
    filtered_books = books_db
    if author:
        filtered_books = [b for b in filtered_books if b.author == author]
    if publication_year:
        filtered_books = [b for b in filtered_books if b.publication_year == publication_year]
    return filtered_books

@app.get("/reviews/{book_id}", response_model=List[Review])
def get_reviews(book_id: int):
    book_reviews = [r for r in reviews_db if r.book_id == book_id]
    return book_reviews


def send_confirmation_email(review: Review):
    print(f"Email sent: Thank you for submitting a review for book {review.book_id}!")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
