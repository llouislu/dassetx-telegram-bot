from sqlalchemy import Column, Integer, String, ForeignKey, Float

from dassetx_telegram_bot.database.model.base import Base


class Rules(Base):
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    condition = Column(Integer, ForeignKey("conditions.sign"), nullable=False)
    target_price = Column(Float, nullable=False)
