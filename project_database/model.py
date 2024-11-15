from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship,declarative_base
import pandas as pd
import os

# Load environment variables from docker-compose.yml
DATABASE_USER = os.getenv("POSTGRES_USER", "postgres")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
DATABASE_HOST = "localhost"  # or use the service name from docker-compose, "db"
DATABASE_PORT = "5432"
DATABASE_NAME = os.getenv("POSTGRES_DB", "db")

# Define the database URL for SQLAlchemy
DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Load data from CSV file
df = pd.read_csv('project_database/aa_output.csv', on_bad_lines='skip', sep=';').reset_index()
print(df.info())

# Define the PostgreSQL connection URL
engine = create_engine(DATABASE_URL)

# Initialize the declarative base
Base = declarative_base()

# Define the Ville class for the "ville" table
class Ville(Base):
    __tablename__ = 'ville'
    
    id_ville = Column(Integer, primary_key=True, autoincrement=True)
    name_ville = Column(Text, nullable=False)
    
    # Relationship to Annonce
    annonces = relationship("Annonce", back_populates="ville")

# Define the Annonce class for the "annonce" table
class Annonce(Base):
    __tablename__ = 'annonce'
    
    id_annonce = Column(Integer, primary_key=True, autoincrement=True)
    titre = Column(String(50), nullable=True)
    prix = Column(Float, nullable=True)
    chambres = Column(Integer, nullable=True)
    douches = Column(Integer, nullable=True)
    surface = Column(Float, nullable=True)
    link = Column(Text, nullable=True)
    
    # Foreign key to Ville
    id_ville = Column(Integer, ForeignKey('ville.id_ville'))
    
    # Relationships
    ville = relationship("Ville", back_populates="annonces")
    annonce_equipements = relationship("AnnonceEquipement", back_populates="annonce")

# Define the Equipement class for the "equipement" table
class Equipement(Base):
    __tablename__ = 'equipement'
    
    id_equipement = Column(Integer, primary_key=True, autoincrement=True)
    name_equipement = Column(Text, nullable=True)
    
    # Relationship to AnnonceEquipement
    annonce_equipements = relationship("AnnonceEquipement", back_populates="equipement")

# Define the AnnonceEquipement class for the association table
class AnnonceEquipement(Base):
    __tablename__ = 'annonce_equipements'
    
    # Composite primary key for many-to-many relationship
    id_annonce = Column(Integer, ForeignKey('annonce.id_annonce'), primary_key=True)
    id_equipement = Column(Integer, ForeignKey('equipement.id_equipement'), primary_key=True)
    
    # Relationships
    annonce = relationship("Annonce", back_populates="annonce_equipements")
    equipement = relationship("Equipement", back_populates="annonce_equipements")

# Create tables in the database
Base.metadata.create_all(engine)

# Configure the session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Loop over each row in the DataFrame and add to the 'Annonce' table
for index, row in df.iterrows():
    new_ville = Ville(name_ville=row['localisation'])
    session.add(new_ville)
    session.commit()  # Commit so we get the ID for the new Ville
    
    new_annonce = Annonce(
        titre=row['titre'],
        prix=row['prix'],
        chambres=row['chambres'],
        douches=row['douches'],
        surface=row['surface'],
        link=row['URL'],
        id_ville=new_ville.id_ville  # Associate with new_ville's id
    )
    session.add(new_annonce)
    session.commit()  # Commit to get the ID for the new Annonce

    # Create equipment and associate it with the current Annonce
    for equip_name in [
        "Chauffage central", "Lave-vaisselle", "Meuble", "Ascenseur", 
        "Double vitrage", "Isolation phonique", "Dressing", "Cave", "Grenier", "Four", 
        "Micro-ondes", "Hotte aspirante", "Plaque de cuisson", "Refrigerateur", "Congelateur", 
        "Box internet", "Systeme domotique", "Pre-installation pour climatisation reversible", 
        "Faux-plafond", "Revetement de sol industriel", "eclairage professionnel"
    ]:
        new_equipement = Equipement(name_equipement=equip_name)
        session.add(new_equipement)
        session.commit()  # Commit to get the ID for the new Equipement
        
        # Add association in AnnonceEquipement
        annonce_equipement = AnnonceEquipement(
            id_annonce=new_annonce.id_annonce,
            id_equipement=new_equipement.id_equipement
        )
        session.add(annonce_equipement)
        session.commit()

# Close the session
session.close()

print("Data successfully inserted into the database.")
