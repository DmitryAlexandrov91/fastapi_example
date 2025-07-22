from sqlalchemy import Column, String, Text

from app.models.base import BaseDonationCharityProject


class CharityProject(BaseDonationCharityProject):
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
