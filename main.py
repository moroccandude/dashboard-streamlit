import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder

import csv
# Read the CSV file into a DataFrame
df = pd.read_csv('dt.csv')

# clean Columns =>  etracter la partie numeric
df['prix'] = df['prix'].str.replace("DH", "", regex=False)
df['prix'] = df['prix'].str.replace("/Nuit", "", regex=False)
df['prix'] = df['prix'].replace("PRIX NON SPÉCIFIÉ", np.nan)
df['prix'] = df['prix'].apply(lambda x: "".join(x.split()) if isinstance(x, str) else x)
df['prix'] = df['prix'].str.strip()
870000.0
# Convert les valeur to numeric, forcing errors to NaN where necessary
df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
df['chambres'] = pd.to_numeric(df['chambres'], errors='coerce')
df['douches'] = pd.to_numeric(df['douches'], errors='coerce')
df['surface'] = pd.to_numeric(df['surface'], errors='coerce')
df['etage'] = pd.to_numeric(df['etage'], errors='coerce')


# Drop unnecessary columns
df.drop(columns=['Salons', 'Âge_bien',' '], inplace=True)

print("___________________")
prix_mean =df['prix'].mean()
prix_median =df['prix'].median()
prix_mode =df['prix'].mode()[0] # mode() returns a series, so we take the first mode
prix_std=df['prix'].std()

print(f'\nMean prix: {prix_mean}')
print(f'Median prix: {prix_median}')
print(f'Mode prix: {prix_mode}')
print(f'std prix: {prix_std}')
print("___________________")
chambres_mean =df['chambres'].mean()
chambres_median =df['chambres'].median()
chambres_mode =df['chambres'].mode()[0] # mode() returns a series, so we take the first mode
chambres_std=df['chambres'].std()

print(f'\nMean chambres: {chambres_mean}')
print(f'Median chambres: {chambres_median}')
print(f'Mode chambres: {chambres_mode}')
print(f'std chambres: {chambres_std} \n')

print("___________________")

douches_mean =df['douches'].mean()
douches_median =df['douches'].median()
douches_mode =df['douches'].mode()[0] # mode() returns a series, so we take the first mode
douches_std=df['douches'].std()

print(f'\nMean douches: {douches_mean}')
print(f'Median douches: {douches_median}')
print(f'Mode douches: {douches_mode}')
print(f'std douches: {douches_std} \n')
print("___________________")

surface_mean =df['surface'].mean()
surface_median =df['surface'].median()
surface_mode =df['surface'].mode()[0] # mode() returns a series, so we take the first mode
surface_std=df['surface'].std()

print(f'\nMean surface: {surface_mean}')
print(f'Median surface: {surface_median}')
print(f'Mode surface: {surface_mode}')
print(f'std surface: {surface_std} \n')
print("___________________")

etage_mean =df['etage'].mean()
etage_median =df['etage'].median()
etage_mode =df['etage'].mode()[0] # mode() returns a series, so we take the first mode
etage_std=df['etage'].std()

print(f'\nMean etage: {etage_mean}')
print(f'Median etage: {etage_median}')
print(f'Mode etage: {etage_mode}')
print(f'std etage: {etage_std} \n')

print("___________________")

# Check for missing values in the 'prix' column
print('Missing values in prix:', df['prix'].isnull().sum())

# Calculate missing percentage for the whole DataFrame
missing_percentage = df.isnull().mean() * 100
print('Missing percentage:\n', missing_percentage)


df['prix'] = df['prix'].fillna(df['prix'].median())
df['chambres'] = df['chambres'].fillna(df['chambres'].mode().iloc[0])
# inplace() is an argument used in many pandas methods (like fillna(), drop(), rename(), etc.) 
# to decide whether to modify the DataFrame in place or return a new modified DataFrame.

# il y des valuers frequent so on va utiliser mode pour replacer les valeur manquants
# mode return index anf frequent value 0 5 iloc[0] => to take first
df['douches'] = df['douches'].fillna(df['douches'].mode().iloc[0])
df['surface'] = df['surface'].fillna(df['surface'].median())
df['etage'] = df['etage'].fillna(df['etage'].median())

print('Missing values in prix after imputation:', df['prix'].isnull().sum())


# detecter les valeurs aberrantes => outliers
# for i in ['chambres','douches','prix','surface','etage'] :
Q1 = df['prix'].quantile(0.25)  # Premier quartile (25%)
Q3 = df['prix'].quantile(0.75)  # Troisième quartile (75%)
IQR = Q3 - Q1 

Lower_Bound=Q1-1.5*IQR
Upper_Bound=Q3+1.5*IQR
print(f"Lower bound = {Lower_Bound} | upper bound={Upper_Bound}")
i = df[(df['prix'] < Lower_Bound) | (df['prix'] > Upper_Bound)]
df2=df.copy()
# use for normal distrubition 
df2['score_Z_douches'] = (df2['douches'] - df2['douches'].mean()) / df2['douches'].std()
print(df2[['score_Z_douches','douches','titre']])
# Un score Z proche de 0 signifie que la donnée est proche de la moyenne.
# Un score Z positif =  moyenne< donnée
# Un score Z négatif = moyenne >  donnée

df2['score_Z_chambres'] = (df2['chambres'] - df2['chambres'].mean()) / df2['chambres'].std()
print(df2[['score_Z_chambres','chambres','titre']])

# detecter values aberrantes
Q1 = df2['surface'].quantile(0.25)  # Premier quartile (25%)
Q3 = df2['surface'].quantile(0.75)  # Troisième quartile (75%)
IQR = Q3 - Q1 

Lower_Bound=Q1-1.5*IQR
Upper_Bound=Q3+1.5*IQR
print(f"Lower bound = {Lower_Bound} | upper bound={Upper_Bound}")
measure = df[(df['surface'] < Lower_Bound) | (df['surface'] > Upper_Bound)]



df2['score_Z_etage'] = (df2['etage'] - df2['etage'].mean()) / df2['etage'].std()
print(df2[['score_Z_etage','etage','titre']])

plt.figure(figsize=(8, 6))
plt.grid('both')
sns.boxplot(x=df['douches'], color="lightblue", width=0.5)


plt.title("Box Plot for Chambres - Detecting Outliers")
plt.xlabel("Number of douches")

# Show the plot
plt.show()

# Affichage du DataFrame avec les scores Z
print(df)


df_copy = df.copy()
normalizeMinMax=MinMaxScaler()


df_copy['prix']=normalizeMinMax.fit_transform(df_copy[['prix']])
# Convert the result to a DataFrame and print


Normalize_stndard=StandardScaler()
df_copy[['chambres']]=Normalize_stndard.fit_transform(df_copy[['chambres']])


df_copy['douches']=normalizeMinMax.fit_transform(df_copy[['douches']])

df_copy['surface']=normalizeMinMax.fit_transform(df_copy[['surface']])

df_copy[['etage']]=Normalize_stndard.fit_transform(df_copy[['etage']])

natomic=[]
for i in df.columns:
        if df[i].apply(lambda x: isinstance(x, (list, tuple, set))).any():
           natomic.append(x)
        else:
              print(f"{i} : is atomic column")



# with open('cleaned_file.csv','w',newline='') as file:
#     fieldnames = df.columns.tolist()
#     csv_writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     csv_writer.writerow(fieldnames)
#     csv_writer.writerows(df.values)


 # Apply SMOTE
df_copy[['prix','chambres','douches','surface','etage']]



 # Assuming 'prix' is the target (can be replaced with any classification label)
# Apply SMOTE to balance the dataset
# Check for nulls or mixed types in 'localisation'
df_copy['Type']=df_copy['Type'].fillna("unknown")
print(f"total null is : {df_copy['Type'].isnull().sum()}")
# categorize with numbers
labelEncoder_Type=LabelEncoder()
df_copy['Type']=labelEncoder_Type.fit_transform(df_copy['Type'])


labelEncoder_city=LabelEncoder()
df_copy['localisation']=labelEncoder_city.fit_transform(df_copy['localisation'])


# definier les independant values et dependant values (x(features): pour dire a Smote to generer samples basee sur cette Dataframe y(target):column quel nous se intreson )
x=df_copy[['localisation', 'prix']]
# we use df.copy()[] to create copy of dataframe
y=df_copy.copy()['Type']


smote = SMOTE(random_state=42, k_neighbors=2)
X_resampled, y_resampled = smote.fit_resample(x, y)
print(f"{X_resampled} \n {y_resampled}")

