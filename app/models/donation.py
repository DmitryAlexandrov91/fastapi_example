from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseDonationCharityProject


class Donation(BaseDonationCharityProject):
    user_id = Column(
        Integer,
        ForeignKey('user.id')
    )
    comment = Column(Text)
