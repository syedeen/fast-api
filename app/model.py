from app.database import Base 
from sqlalchemy.sql.expression import null
from sqlalchemy import CheckConstraint , TIMESTAMP , text , String , ForeignKey 
from sqlalchemy.orm import Mapped , mapped_column , relationship
from datetime import datetime


class Actor(Base):
    __tablename__ = "actors"
    actor_id : Mapped[int] =  mapped_column(primary_key=True)
    actor_name : Mapped[str] = mapped_column(nullable=False)
    actor_age :Mapped[int] = mapped_column(nullable=False)
    owner_id :Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    owner :Mapped["User"] = relationship(back_populates="actors")
    created_at :Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"))
    film_actor :Mapped[list["Film_Actor"]] = relationship(
        back_populates="actor",
            cascade="all, delete-orphan"
    )

    films :Mapped[list["Films"]] = relationship(
        secondary="film_actors",
        back_populates="actors",
        viewonly=True
    )




    __table_args__ = (
        CheckConstraint(
            "actor_age  BETWEEN 15 AND 90",
            name = "actor_age_BETWEEN_15_AND_90"
        ),
        CheckConstraint(
            "film_count  >=0",
            name = "film_count_GREATER_>=0"
        )
    )

    def __repr__(self):
        return f"<Actor(id={self.actor_id}, name='{self.actor_name}', age={self.actor_age})>"





class User(Base):
    __tablename__ = "users"
    user_id : Mapped[int] = mapped_column(primary_key=True)
    email : Mapped[str] = mapped_column(String(254),nullable=False , unique=True)
    username : Mapped[str] = mapped_column(String(50),nullable=False , unique=True)
    password : Mapped[str] = mapped_column(nullable=False)
    is_active : Mapped[bool] = mapped_column(default=True)
    failed_login_attempts:Mapped[int] = mapped_column(default=0) 
    locked_until :Mapped[datetime|None] = mapped_column(
        TIMESTAMP(timezone=True),
          nullable=True)
    created_at : Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"))
    

    films: Mapped[list["Films"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    actors: Mapped[list["Actor"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )


    last_login : Mapped[datetime|None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    

    def __repr__(self):
        return f"<User_id={self.user_id})>"





class Films(Base):
    __tablename__  = "films"
    film_id:Mapped[int] = mapped_column(primary_key=True)
    title:Mapped[str] = mapped_column(nullable=False)
    duration_in_mins:Mapped[int] = mapped_column(nullable=False)
    is_g:Mapped[bool] = mapped_column(nullable=False)
    rating:Mapped[float] = mapped_column(nullable=False)
    created_At:Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),server_default=text("now()"))
    owner_id :Mapped[int] = mapped_column(ForeignKey("users.user_id"),nullable=False)
    owner :Mapped["User"] = relationship(back_populates="films") 
    film_actor :Mapped[list["Film_Actor"]] = relationship(
        back_populates="film",
            cascade="all, delete-orphan"
    )
    actors:Mapped[list["Actor"]] = relationship(
        secondary="film_actors",
        back_populates="films",
        viewonly=True
    )

    def __repr__(self):
        return f"<film_id={self.film_id})>"
    

class Film_Actor(Base):
    __tablename__ = "film_actors"
    film_id: Mapped[int] = mapped_column(ForeignKey("films.film_id"),primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actors.actor_id"),primary_key=True)

    film: Mapped["Films"] = relationship(back_populates="film_actor")
    actor: Mapped["Actor"] = relationship(back_populates="film_actor")



class Film_votes(Base):
    __tablename__ = "film_votes"
    film_id: Mapped[int] = mapped_column(ForeignKey("films.film_id"),primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"),primary_key=True)
    vote: Mapped[int] = mapped_column(nullable=False)
    created_at:Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),server_default=text("now()"))

    __table_args__ = (
        CheckConstraint(
        "vote in (-1,1)",
         name= "votes_minus_one_or_one"
    ),
    )




## python -m app.model