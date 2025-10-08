import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load your cleaned CSV
df = pd.read_csv("cleaned_master_dataset.csv")

# Step 2: Create a SQLite database connection
engine = create_engine("sqlite:///knowledge_base.db")

# Step 3: Store the DataFrame as a SQL table
df.to_sql("knowledge_data", engine, if_exists="replace", index=False)

print("✅ Database created successfully: knowledge_base.db")
