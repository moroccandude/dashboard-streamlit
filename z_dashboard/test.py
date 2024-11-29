import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import seaborn as sns


database_url = 'postgresql://postgres:1234@localhost:5432/db'
try:
 engine = create_engine(database_url)
 with engine.connect() as conn:
    conn.execute(text("select 1"))
except Exception as e:
    st.error("connection filed")
    st.stop()    
with engine.connect() as connection:
    query_ville = """SELECT * FROM "ville";"""
    query_annonce = """SELECT * FROM "annonce";"""
    query_equipement = """SELECT * FROM "equipement";"""
    annonce_equipement=""" SELECT * FROM "annonce_equipements";"""
   
    ville_result = connection.execute(text(query_ville))
    annonce_result = connection.execute(text(query_annonce))
    equipement_result = connection.execute(text(query_equipement))
    result_annonce_equipement=connection.execute(text(annonce_equipement))
    df_ville = pd.DataFrame(ville_result.fetchall(), columns=ville_result.keys())
    df_annonce = pd.DataFrame(annonce_result.fetchall(), columns=annonce_result.keys())
    df_equipement = pd.DataFrame(equipement_result.fetchall(), columns=equipement_result.keys())
    df_annonce_equipement=pd.DataFrame(result_annonce_equipement.fetchall())
st.sidebar.title("Filtres interactifs :")

with st.sidebar.form(key="control_data"):
    price_min, price_max = st.slider(
        "Gamme de prix",
        min_value=int(df_annonce["prix"].min()),
        max_value=int(df_annonce["prix"].max()),
        value=(int(df_annonce["prix"].min()), int(df_annonce["prix"].max()))
    )

    chamber = st.slider(
        "Nombre de chambres",
        min_value=int(df_annonce["chambres"].min()),
        max_value=int(df_annonce["chambres"].max()),
        value=int(df_annonce["chambres"].min())
    )

    
    douches = st.slider(
        "Nombre de salles de bain",
        min_value=int(df_annonce["douches"].min()),
        max_value=int(df_annonce["douches"].max()),
        value=int(df_annonce["douches"].min())
    )

    selected_ville = st.selectbox(
        "Sélection de ville",
        options=["All"] + df_ville["name_ville"].unique().tolist()
    )

    selected_equipement = st.multiselect(
        "Équipements",
        options=df_equipement["name_equipement"].tolist(),
        default=[]
    )

    submit_button = st.form_submit_button(label="Appliquer les filtres")
st.html('<h1 style=text-align:center>pricipale <b>page</b> 🏠</h1>')
if submit_button:
    filters = {
        "min_price": price_min,
        "max_price": price_max,
        "rooms": chamber,
        "bathrooms": douches,
        "city": selected_ville if selected_ville != "All" else None,
        "annonce_eq": [selected_equipement] if selected_equipement else None
    }
 
    filtered_query = """
    SELECT  
        a.*,
        v.name_ville,
        STRING_AGG(eq.name_equipement, ', ') AS name_equipement
    FROM 
        annonce a
    JOIN 
        annonce_equipements an_eq ON an_eq.id_annonce = a.id_annonce
    JOIN 
        equipement eq ON an_eq.id_equipement = eq.id_equipement
    JOIN 
        ville v ON a.id_ville = v.id_ville  
    WHERE 
        a.prix BETWEEN :min_price AND :max_price
        AND a.chambres >= :rooms
        AND a.douches >= :bathrooms
        AND (:annonce_eq IS NULL OR eq.name_equipement = ANY(:annonce_eq))
        AND (:city IS NULL OR v.name_ville = :city)
    GROUP BY
        a.id_annonce, a.titre, v.name_ville;
    """
    
   
    with engine.connect() as connection:
        filtered_result = connection.execute(text(filtered_query), filters)
        # result_z = connection.execute(text(query_getEach_eq), filters)  # Pass filters here

        df_filtered = pd.DataFrame(filtered_result.fetchall(), columns=filtered_result.keys())
        # filtered_result_eq_percentage=pd.DataFrame(result_z.fetchall,columns=result_z.keys())
    # Display results
    st.write("### Résultats filtrés")
    st.dataframe(df_filtered)

    st.write("### Équipements sélectionnés")
    st.write(selected_equipement)
    merged_table=pd.merge(df_annonce, df_ville,how='inner')
    merged_table=pd.merge(merged_table,df_annonce_equipement)

    merged_table=pd.merge(merged_table,df_equipement)
    merged_table=merged_table.merge(merged_table)
    result=merged_table.groupby('name_ville')['id_annonce'].count().reset_index()

    result.reset_index()
    result.columns = ['name_ville', 'annonce_count']
    st.html('<h2 style="text-align:center">Un graphique à barres<span style="color:#f40386"> montrant le nombre d’annonces par ville </h2>') 
    st.bar_chart(result.set_index('name_ville')['annonce_count'],color='#f40386',x_label='les villes',y_label='le nombre d’annonces')
    prices_movements=merged_table.groupby('name_ville')['prix'].sum().sort_values(ascending=False)
   
    st.html('<h2 style="text-align:center">Un graphique à barres<span style="color:#0259a7"> pour comprendre la répartition des prix</h2>') 
   
    
    st.bar_chart(prices_movements,color='#0259a7',x_label='les villes',y_label='la somme de prix (dh)')  
    
    df_city = merged_table[merged_table['name_ville'] == filters.get('city')]
    
    pieces_ville = merged_table.groupby('name_ville').agg(
    moyenne_chambres=('chambres', 'mean'),
    moyenne_salles_bain=('douches', 'mean')
).reset_index()
    pieces_ville.set_index('name_ville', inplace=True)
    st.html('<h1 style=text-align:center>pour Analyse des <span style=color:#ffed00>caractéristiques des biens</span></h1> on va calculer  le nombre moyen de pièces et de salles de bain par ville. ')
    col1, col2 = st.columns(2)
    with col1:
      st.bar_chart(pieces_ville[['moyenne_chambres']],color='#ffed00')
    with col2:
      st.bar_chart(pieces_ville[['moyenne_salles_bain']],color='#ffed00')
    st.html('<h1>pour exploreration <span style=color:#00feff>la relation entre la surface et le prix des biens</span></h1>')
    col3, col4 = st.columns(2)
    filter_by_ville=merged_table[merged_table['name_ville'] == filters.get('city')]
    relation_surface_prix=filter_by_ville.groupby('name_ville').agg(
     moyenne_suface=('surface', 'mean'),
     moyenne_prix=('prix','mean')  )
    # with col3:
    #  st.bar_chart(relation_surface_prix[['moyenne_prix']])
  
    # with col4:
    #  st.bar_chart(relation_surface_prix[['moyenne_suface']])
     
    st.area_chart(filter_by_ville,y='surface',x='prix',color="#00feff")
   
