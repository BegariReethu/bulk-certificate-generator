from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_name: Mapped[str] = mapped_column(String(200), nullable=False)
    certificate_title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PROCESSING")
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    successful: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recipients: Mapped[list["Recipient"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("generation_jobs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    job: Mapped[GenerationJob] = relationship(back_populates="recipients")
