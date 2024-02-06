from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, Session, relationship
from fastapi import Depends

DATABASE_URL = "sqlite:///./test.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

class BookDB(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    publication_year = Column(Integer)

class ReviewDB(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    rating = Column(Integer)
    book_id = Column(Integer, ForeignKey("books.id"))
    book = relationship("BookDB", back_populates="reviews")

Base.metadata.create_all(bind=engine)

class BookDB(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    publication_year = Column(Integer)
    reviews = relationship("ReviewDB", back_populates="book")

class ReviewDB(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    rating = Column(Integer)
    book_id = Column(Integer, ForeignKey("books.id"))
    book = relationship("BookDB", back_populates="reviews")

def get_db():
    db = Session(autocommit=False, bind=engine)
    try:
        yield db
    finally:
        db.close()

def add_book_db(book: Book, db: Session = Depends(get_db)):
    db_book = BookDB(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def submit_review_db(book_id: int, review: Review, db: Session = Depends(get_db)):
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_review = ReviewDB(**review.dict(), book_id=book_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review
