from app.database import Base 
from sqlalchemy.sql.expression import null
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped , mapped_column


class Actor(Base):
    __tablename__ = "actors"
    actor_id : Mapped[int] =  mapped_column(primary_key=True)
    actor_name : Mapped[str] = mapped_column(nullable=False)
    film_count :Mapped[int] = mapped_column(nullable=False , default=0)
    actor_age :Mapped[int] = mapped_column(nullable=False)

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


## python -m app.model