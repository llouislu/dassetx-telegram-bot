from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from dassetx_telegram_bot.database.model.base import Base


class Subscriptions(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = (UniqueConstraint('rule_id', 'subscriber_id'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    subscriber_id = Column(Integer, nullable=False)
