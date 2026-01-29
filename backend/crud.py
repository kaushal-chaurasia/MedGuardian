from sqlalchemy.orm import Session
from models import Drug

def get_multiple_drugs(db: Session, names: list):
    return db.query(Drug).filter(
        Drug.name.in_(names)).all()
