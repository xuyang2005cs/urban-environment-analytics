"""City configuration models."""

from pydantic import BaseModel, ConfigDict, Field


class City(BaseModel):
    """A geocoded city used by the collection pipeline."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str
    query_name: str
    country: str
    country_code: str = Field(min_length=2, max_length=2)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str

