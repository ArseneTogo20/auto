import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

# Configuration de la page Streamlit
st.set_page_config(layout="wide")

# Chemin vers l'image locale
image_path = 'logo.jpg'

# Chargement et affichage du logo
try:
    image = Image.open(image_path)
    st.image(image, caption='', width=200)  # Ajustez la largeur ici
except Exception as e:
    st.error(f"Erreur lors du chargement de l'image : {e}")

# Uploader le fichier à analyser
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=["xlsx"])

# Fonction pour demander le mois
def select_month():
    months = [
        "Janvier", "Février", "Mars", "Avril", "Mai",
        "Juin", "Juillet", "Août", "Septembre",
        "Octobre", "Novembre", "Décembre"
    ]
    selected_month = st.selectbox("Veuillez sélectionner un mois :", months)
    return selected_month

if uploaded_file is not None:
    # Demander à l'utilisateur de sélectionner un mois
    month = select_month()

    # Charger le fichier Excel
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier Excel : {e}")
        st.stop()

    # Nettoyage des données
    df.dropna()

    # Vérifier les valeurs uniques dans la colonne TECHNOLOGIE(S)
    if 'TECHNOLOGIE(S)' not in df.columns:
        st.error("La colonne 'TECHNOLOGIE(S)' est absente du fichier.")
        st.stop()

    # Filtrage des données pour 2G/3G/4G
    data_filtered = df[df['TECHNOLOGIE(S)'] == '2G/3G/4G']
    
    if 'Down Time' not in df.columns:
        st.error("La colonne 'Down Time' est absente du fichier.")
        st.stop()
    
    df['Down Time'] = pd.to_numeric(df['Down Time'], errors='coerce')
    data_filtered['Down Time'] = pd.to_numeric(data_filtered['Down Time'], errors='coerce')

    # Calcul pour DR1
    data_DR1 = data_filtered[data_filtered['Down Time'] >= 60]
    down_time_count = data_DR1.groupby('Site').size().reset_index(name='DR1')
    down_time_count['DR1'] -= 2
    result_DR1 = down_time_count[down_time_count['DR1'] >= 1]
    result_DR1.set_index('Site', inplace=True)
    total_DR1 = result_DR1['DR1'].sum()

    # Calcul pour DR2
    data_DR2 = data_filtered[data_filtered['Down Time'] >= 180]
    down_time_count2 = data_DR2.groupby('Site').size().reset_index(name='DR2')
    down_time_count2.set_index('Site', inplace=True)
    total_DR2 = down_time_count2['DR2'].sum()

    # Résumé par date
    if ' Date de Fin' in df.columns:
        data_use = data_filtered[data_filtered['Down Time'] >= 180]
        data_use[' Date de Fin'] = pd.to_datetime(data_use[' Date de Fin'], errors='coerce')
        down_time_counts = data_use.groupby(data_use[' Date de Fin'].dt.date)['Down Time'].count().reset_index(name='Total Down Times')
        down_time_counts.columns = ['Date', 'Nombre de violation de DR2']
    else:
        down_time_counts = pd.DataFrame(columns=['Date', 'Nombre de violation de DR2'])

    # Affichage des résultats
    st.markdown("<h1 style='font-family: Arial; color: orange;'>RAPPORT DR1&2 ARCEP</h1>", unsafe_allow_html=True)

    # Affichage du tableau DR1 avec le mois sélectionné
    st.markdown(f"<h3 style='font-family: Arial; color: orange;'>DR1 du mois de {month} 2024</h3>", unsafe_allow_html=True)
    
    columns = st.columns(5)
    rows_per_column = 20
    for i in range(5):
        start_row = i * rows_per_column
        end_row = start_row + rows_per_column
        if start_row < len(result_DR1):
            columns[i].dataframe(result_DR1.iloc[start_row:end_row], height=750)

    # Total DR1
    st.markdown(f"""<div style="border: 2px solid #FF4500; padding: 5px; border-radius: 5px;">
                    <h4>Total DR1 en terme de non conformités ARCEP = {total_DR1}</h4>
                    </div>""", unsafe_allow_html=True)

    # Affichage du tableau DR2 avec le mois sélectionné
    st.markdown(f"<h3 style='font-family: Arial; color: orange;'>DR2 mois de {month} 2024</h3>", unsafe_allow_html=True)
    
    columns = st.columns(5)
    for i in range(5):
        start_row = i * rows_per_column
        end_row = start_row + rows_per_column
        if start_row < len(down_time_count2):
            columns[i].dataframe(down_time_count2.iloc[start_row:end_row], height=750)

    # Total DR2
    st.markdown(f"""<div style="border: 2px solid #FF4500; padding: 5px; border-radius: 5px;">
                    <h4>Total DR2 en terme de non conformités ARCEP = {total_DR2}</h4>
                    </div>""", unsafe_allow_html=True)

    # Récapitulatif des violations avec le mois sélectionné
    st.markdown(f"<h3 style='font-family: Arial; color: orange;'>Récapitulatif des violations mois de {month} 2024</h3>", unsafe_allow_html=True)
    
    st.dataframe(down_time_counts)

    # Tableau interactif pour comparaison DR1 et DR2 avec le mois sélectionné dans le titre
    data2 = {
        'Janvier 2024': ['','',''],
        'Fevrier 2024': ['','',''],
        'Mars 2024': ['','',''],
        'Avril 2024': ['','',''],
        'Mai 2024': ['','',''],
        'Juin 2024': ['','',''],
        'Juillet 2024': ['','',''],
        'Aout 2024': ['','',''],
        'Septembre 2024': ['','',''],
        'Octobre 2024': ['','',''],
        'Novembre 2024': ['','',''],
        'Décembre 2024': ['','',''],
    }
    
    row_names = ['DR1', 'DR2', 'DR1 + DR2']
    df2 = pd.DataFrame(data2, index=row_names)

    st.markdown(f"<h3 style='font-family: Arial; color: orange;'>Comparaison DR1 et DR2 de Janvier à {month} 2024</h3>", unsafe_allow_html=True)
    edited_df2 = st.data_editor(df2, key="self")
    st.write(edited_df2)

     # Vérifiez si des valeurs ont été saisies
    if edited_df2 is not None:
        try:
            dr1_values = pd.to_numeric(edited_df2.loc['DR1'], errors='coerce')
            dr2_values = pd.to_numeric(edited_df2.loc['DR2'], errors='coerce')
            dr1_plus_dr2_values = pd.to_numeric(edited_df2.loc['DR1 + DR2'], errors='coerce')

            plt.figure(figsize=(10, 6))
            plt.plot(data2.keys(), dr1_values, marker='o', linestyle='-', color='b', label='DR1')
            plt.plot(data2.keys(), dr2_values, marker='o', linestyle='-', color='g', label='DR2')
            plt.plot(data2.keys(), dr1_plus_dr2_values, marker='o', linestyle='-', color='r', label='DR1 + DR2')

            plt.title('Comparaison des valeurs de DR1, DR2 et DR1 + DR2')
            plt.xlabel('Mois')
            plt.ylabel('Valeurs')
            plt.xticks(rotation=45)
            plt.grid()
            plt.legend()
            plt.tight_layout()

            st.pyplot(plt)

        except Exception as e:
            st.error("Erreur lors de la conversion des données : " + str(e))

     # Courbe d'évolution DR2 mois avec le mois sélectionné dans le titre 
    st.markdown(f"<h3 style='font-family: Arial; color: orange;'>Courbe d'evolution DR2 mois {month} 2024</h3>", unsafe_allow_html=True)

    plt.figure(figsize=(10, 4))
    plt.plot(down_time_counts['Date'], down_time_counts['Nombre de violation de DR2'], marker='o', linestyle='-', color='b') 
    plt.title('Somme DR2 par jour')
    plt.xlabel('Date')
    plt.ylabel('Somme DR2 par jour')
    plt.xticks(rotation=45)  
    plt.grid()
    plt.tight_layout()  

    st.pyplot(plt)