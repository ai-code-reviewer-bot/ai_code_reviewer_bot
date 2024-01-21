from abc import ABC
from typing import List

from pydantic import BaseModel


class Review(BaseModel):
    line_number: int
    comment: str


class Reviewer(BaseModel, ABC):
    def review_file_changes(self, file_changes: str) -> List[Review]:
        pass
