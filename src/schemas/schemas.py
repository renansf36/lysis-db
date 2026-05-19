from datetime import date
from typing import Any

from pydantic import BaseModel, Field, model_validator


class _DateRangeFilterBase(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date")
        return self


class OriginDateFilter(_DateRangeFilterBase):
    pass


class YearRangeFilter(BaseModel):
    start_year: int = Field(ge=1900, le=2100)
    end_year: int = Field(ge=1901, le=2101)

    @model_validator(mode="after")
    def validate_year_range(self):
        if self.end_year <= self.start_year:
            raise ValueError("end_year must be greater than start_year")
        return self


class YearFilter(BaseModel):
    year: int = Field(ge=1900, le=2100)


class DateRangeFilter(_DateRangeFilterBase):
    pass


class PaginatedProcessInclusionReport(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[dict[str, Any]]
