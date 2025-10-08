import pandas as pd
import re

# ===============================
# STEP 1 — LOAD DATA
# ===============================
indian_df = pd.read_csv("A_Z_medicines_dataset_of_India.csv")
side_df = pd.read_csv("Drug Side Effects.csv")
inter_df = pd.read_csv("Drug-Drug Interaction.csv")

# ===============================
# STEP 2 — CLEAN COLUMN NAMES
# ===============================
def clean_columns(df):
    df.columns = df.columns.str.lower().str.strip()
    return df

indian_df = clean_columns(indian_df)
side_df = clean_columns(side_df)
inter_df = clean_columns(inter_df)

print("📋 Indian dataset columns:", list(indian_df.columns))
print("📋 Side Effects dataset columns:", list(side_df.columns))
print("📋 Interaction dataset columns:", list(inter_df.columns))

# ===============================
# STEP 3 — FIX INTERACTION DATASET
# ===============================
def auto_rename_interaction_cols(df):
    rename_map = {}
    for col in df.columns:
        if "drug 1" in col or "drug_a" in col:
            rename_map[col] = "drug1"
        elif "drug 2" in col or "drug_b" in col:
            rename_map[col] = "drug2"
        elif "interaction" in col:
            rename_map[col] = "interaction_description"
    df.rename(columns=rename_map, inplace=True)
    return df

inter_df = auto_rename_interaction_cols(inter_df)
print("✅ Renamed interaction columns:", ", ".join(inter_df.columns))

# Drop NaNs
inter_df = inter_df.dropna(subset=["drug1", "drug2"], how="any")

# ===============================
# STEP 4 — FIX SIDE EFFECTS DATASET
# ===============================
def auto_rename_side_effect_cols(df):
    rename_map = {}
    for col in df.columns:
        if "drug_name" in col:
            rename_map[col] = "drug_name"
        elif "name" == col:  # fallback
            rename_map[col] = "drug_name"
        elif "side_effects" in col or "adverse" in col:
            rename_map[col] = "side_effect"
    df.rename(columns=rename_map, inplace=True)
    return df

side_df = auto_rename_side_effect_cols(side_df)
print("✅ Renamed side effect columns:", ", ".join(side_df.columns))

# Validation
if "drug_name" not in side_df.columns or "side_effect" not in side_df.columns:
    raise KeyError("❌ 'drug_name' or 'side_effect' column missing in side effects dataset!")

# Drop empty rows
side_df = side_df.dropna(subset=["drug_name", "side_effect"])

# ===============================
# STEP 5 — STANDARDIZE TEXT
# ===============================
def normalize(text):
    if pd.isna(text):
        return ""
    return re.sub(r"[^a-zA-Z0-9\s+]", "", str(text)).lower().strip()

for col in ["name", "short_composition1", "short_composition2"]:
    if col in indian_df.columns:
        indian_df[col] = indian_df[col].apply(normalize)

side_df["drug_name"] = side_df["drug_name"].apply(normalize)
side_df["side_effect"] = side_df["side_effect"].apply(normalize)
inter_df["drug1"] = inter_df["drug1"].apply(normalize)
inter_df["drug2"] = inter_df["drug2"].apply(normalize)

# ===============================
# STEP 6 — EXTRACT COMPONENTS
# ===============================
def extract_components(comp):
    if pd.isna(comp) or comp == "":
        return []
    return [
        re.sub(r"\d+(mg|ml|mcg)|tablet|capsule|syrup", "", c).strip()
        for c in comp.split("+")
        if c.strip()
    ]

indian_df["components1"] = indian_df["short_composition1"].apply(extract_components)
indian_df["components2"] = indian_df["short_composition2"].apply(extract_components)

indian_df["all_components"] = indian_df.apply(
    lambda x: list(set(x["components1"] + x["components2"])), axis=1
)

# ===============================
# STEP 7 — BUILD INTERACTION MAPPING
# ===============================
interaction_pairs = set(
    tuple(sorted([row["drug1"], row["drug2"]])) for _, row in inter_df.iterrows()
)

def check_interaction(components):
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            pair = tuple(sorted([components[i], components[j]]))
            if pair in interaction_pairs:
                return f"{pair[0]} interacts with {pair[1]}"
    return "No known interaction"

indian_df["interaction_warning"] = indian_df["all_components"].apply(check_interaction)

# ===============================
# STEP 8 — ADD SIDE EFFECTS
# ===============================
side_effect_map = side_df.groupby("drug_name")["side_effect"].apply(list).to_dict()

def get_side_effects(components):
    effects = []
    for comp in components:
        if comp in side_effect_map:
            effects.extend(side_effect_map[comp])
    return list(set(effects)) if effects else ["No major side effects known"]

indian_df["side_effects"] = indian_df["all_components"].apply(get_side_effects)

# ===============================
# STEP 9 — SAVE FINAL CLEANED DATA
# ===============================
final_df = indian_df[
    ["name", "manufacturer_name", "all_components", "interaction_warning", "side_effects"]
]

final_df.to_csv("cleaned_master_dataset.csv", index=False)

print("\n✅ Data preprocessing complete!")
print(f"Total entries processed: {len(final_df)}")
print("📁 Output saved as 'cleaned_master_dataset.csv'")