from sqlalchemy.orm import Session
from typing import TypeVar, Type, List

T = TypeVar("T")

class BaseRepository:
    def __init__(self, session: Session, entity_class: Type[T]) -> None:
        self.session = session
        self.entity_class = entity_class

    def save_entity(self, entity: T) -> T:
        self.session.merge(entity)
        self.session.commit()
        return entity    
    
    def save(self, entities: List[T]) -> bool:
        for entity in entities:
            self.session.add(entity)
            self.session.commit()
        return True

    def get_entity(self, id: int) -> T:
        return self.session.query(self.entity_class).get(id)
    
    def get(self) -> List[T]:
        return self.session.query(self.entity_class).all()
        
    def update(self, entity: T) -> T:
        self.session.merge(entity)
        self.session.commit()
        return entity    
    
    def search_by_property(self, **kwargs) -> List[T]:
        """
        Search entities by properties.
        """
        query = self.session.query(self.entity_class)
        for key, value in kwargs.items():
            query = query.filter(getattr(self.entity_class, key) == value)
        return query.all()