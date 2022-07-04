from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()

class Source(Base):
    __tablename__ = "source"

    source_id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String)
    user_id = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    group_id = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    room_id = Column(String, nullable=True)
    room_name = Column(String, nullable=True)
    source_enabled = Column(Integer,nullable=True)

    def __str__(self) -> str:
        return f"{self.source_id}"
