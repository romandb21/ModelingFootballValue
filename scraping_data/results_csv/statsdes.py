import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def histo_country(frame):
    df = pd.read_csv(frame)
    df_unique = df.drop_duplicates(subset=['Player']) # drop  duplicates of players who appear more than once
    country_counts = df_unique['Country'].value_counts()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=country_counts.index, y=country_counts.values, palette="icefire")
    plt.title('Nombre de joueurs par pays dans les sept grands championnats européens, de 2010 à 2024', fontsize=16)
    plt.xlabel('Pays', fontsize=14)
    plt.ylabel('Nombre', fontsize=14)
    plt.xticks(rotation=45)  
    plt.tight_layout()  
    plt.show()



def diag_country(frame1):
    
    country_name_map = {
    'eng ENG': 'Anglaise',
    'nl NED': 'Néerlandaise',
    'fr FRA': 'Française',
    'it ITA': 'Italienne',
    'es ESP': 'Espagnole',
    'de GER': 'Allemande',
    'Autres pays': 'Autres nationalités'
}
    
    df = pd.read_csv(frame1)
    df_unique = df.drop_duplicates(subset=['Player'])  # drop  duplicates of players who appear more than once
    countries_to_keep = ['eng ENG', 'nl NED', 'fr FRA', 'it ITA', 'es ESP', 'de GER']
    df_unique['Country Grouped'] = df_unique['Country'].apply(lambda x: x if x in countries_to_keep else 'Autres pays') #group for other countries
    country_counts = df_unique['Country Grouped'].value_counts()
    country_counts.index = country_counts.index.map(country_name_map)
    
    plt.figure(figsize=(8, 8))
    plt.pie(country_counts.values, labels=country_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('icefire'))
    plt.title('Répartition des nationalités dans les sept grands championnats européens, de 2010 à 2024')
    plt.show()

def sum_att(frame): 
    df = pd.read_csv(frame)
    goals_per_season = df.groupby('Season')['Performance : G+A'].sum()
    plt.figure(figsize=(10, 6))
    plt.plot(goals_per_season.index, goals_per_season.values, marker='o', linestyle='-', color='skyblue', label='Total G+A')
    plt.title('Nombre total de buts et passes décisives par saison', fontsize=14)
    plt.xlabel('Saison', fontsize=12)
    plt.ylabel('Total des buts et passes décisives (G+A)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

