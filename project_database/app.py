import random
import csv
import pandas as pd
import json

def generate_random_equipment(equipment_list, prob_dist=None, max_items=None):
    if prob_dist:
        return random.choices(equipment_list, weights=prob_dist, k=random.randint(1, max_items))
    else:
        return random.sample(equipment_list, random.randint(1, max_items))

def add_equipment_column(df, equipment_list, prob_dist=None):
    """Adds a new 'Equipement' column as a JSON list of equipment to the dataframe."""
    # Generate the equipment lists
    max_items = 4  # We can have a max of all items
    for _ in range(len(df)):
     equipment_column = json.dumps(generate_random_equipment(equipment_list, prob_dist, max_items)).removeprefix('""')
     df['Equipement'] = equipment_column
     return df
   

# Load data
df = pd.read_csv('project_database/cleaned_file.csv',delimiter=';')

# List of equipment (with optional probabilities)
equipment_list = [
    "Chauffage central", "Lave-vaisselle", "Meuble", "Ascenseur", 
    "Double vitrage", "Isolation phonique", "Dressing", "Cave", "Grenier", "Four", 
    "Micro-ondes", "Hotte aspirante", "Plaque de cuisson", "Refrigerateur", "Congelateur", 
    "Box internet", "Systeme domotique", "Pre-installation pour climatisation reversible", 
    "Faux-plafond", "Revetement de sol industriel", "eclairage professionnel"
]
prob_dist = [0.5] * len(equipment_list)# Add the equipment column
df = add_equipment_column(df, equipment_list,prob_dist)

# Write to CSV with ; as the delimiter
df.to_csv('project_database/aa_output.csv', sep=';', index=False, quoting=csv.QUOTE_MINIMAL)
print("CSV file generated successfully at 'project_database/aa_output.csv'")
print(df['Equipement'][0])