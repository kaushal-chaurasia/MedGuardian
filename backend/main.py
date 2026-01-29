from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import MedicineInput
import crud
from utils import detect_interactions

app = FastAPI(title="MedGuardian API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "MedGuardian backend running"}

@app.get("/drug/{name}")
def get_drug_info(name: str, db: Session = Depends(get_db)):
    drugs = crud.get_drug(db, name)
    return drugs


@app.post("/check-interaction")
def check_interaction(data: MedicineInput, db: Session = Depends(get_db)):
    drugs = crud.get_multiple_drugs(db, data.medicines)

    if len(drugs) < 2:
        return {"error": "At least two medicines required"}

    interaction_report = detect_interactions(drugs)

    return {
        "medicines_checked": data.medicines,
        "interactions": interaction_report
    }
