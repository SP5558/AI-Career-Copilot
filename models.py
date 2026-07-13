from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    password = Column(String(255), nullable=False)


    reports = relationship(
        "Report",
        back_populates="user",
        cascade="all, delete"
    )



class Report(Base):

    __tablename__ = "reports"


    id = Column(
        Integer,
        primary_key=True
    )


    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )


    resume_text = Column(
        Text
    )


    result = Column(
        Text
    )


    user = relationship(
        "User",
        back_populates="reports"
    )