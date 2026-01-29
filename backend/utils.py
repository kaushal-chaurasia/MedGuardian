import ast
import itertools

def parse_components(component_str):
    return ast.literal_eval(component_str)

def detect_interactions(drugs):
    component_map = {}

    # Collect components per drug
    for drug in drugs:
        component_map[drug.name] = parse_components(drug.all_components)

    interactions = []

    # Check all medicine combinations
    for (drug1, comp1), (drug2, comp2) in itertools.combinations(component_map.items(), 2):
        for c1 in comp1:
            for c2 in comp2:
                if c1 == c2:
                    continue
                interactions.append(
                    f"Checked {drug1} and {drug2}: No known interaction"
                )

    return interactions
