import enum

from sqlalchemy import Column, Enum, String

from dassetx_telegram_bot.database.model.base import Base


class ConditionEnum(enum.Enum):
    LESS_THAN = 1
    LESS_EQUAL = 2
    GREATER_THAN = 3
    GREATER_EQUAL = 4


class Conditions(Base):
    __tablename__ = 'conditions'

    sign = Column(Enum(ConditionEnum), primary_key=True)
    name = Column(String)
