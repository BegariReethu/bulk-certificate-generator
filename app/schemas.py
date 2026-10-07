from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RecipientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("name must not be empty")
        return value


class GenerationRequest(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    certificate_title: str = Field(default="Certificate of Completion", min_length=2, max_length=200)
    recipients: list[RecipientCreate] = Field(min_length=1, max_length=1000)

    @field_validator("event_name", "certificate_title")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("value must not be empty")
        return value


class RecipientResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_name: str
    email: str
    status: str
    error_message: str | None = None
    download_url: str | None = None


class JobCreateResponse(BaseModel):
    job_id: int
    status: str
    total: int


class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    total: int
    successful: int
    failed: int
    progress: float
    certificates: list[RecipientResult]
