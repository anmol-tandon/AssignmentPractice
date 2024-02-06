from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class BookDB(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    publication_year = Column(Integer)

class ReviewDB(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    text = Column(String)
    rating = Column(Integer)


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

@app.post("/books/", response_model=Book)
def add_book(book: Book, db: Session = Depends(get_db)):
    db_book = BookDB(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.post("/reviews/", response_model=Review)
def submit_review(review: Review, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_review = ReviewDB(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    # Simulate sending a confirmation email in the background
    background_tasks.add_task(send_confirmation_email, review)
    return db_review

@app.get("/books/", response_model=List[Book])
def get_books(author: str = None, publication_year: int = None, db: Session = Depends(get_db)):
    query = db.query(BookDB)
    if author:
        query = query.filter(BookDB.author == author)
    if publication_year:
        query = query.filter(BookDB.publication_year == publication_year)
    return query.all()

@app.get("/reviews/{book_id}", response_model=List[Review])
def get_reviews(book_id: int, db: Session = Depends(get_db)):
    query = db.query(ReviewDB).filter(ReviewDB.book_id == book_id)
    return query.all()
