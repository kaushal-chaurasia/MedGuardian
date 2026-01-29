from pydantic import BaseModel
from typing import List

class MedicineInput(BaseModel):
    medicines: List[str]
