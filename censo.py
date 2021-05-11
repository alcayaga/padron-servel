import geopandas as gpd
import pandas as pd

censo = gpd.read_file('input/gse_censo_2012.json')

#df = pd.read_csv('output_geocode/padron.csv')
df = pd.read_csv('padron.csv')

df_condir = df[~df['lat'].isnull()]
df_sindir = df[df['lat'].isnull()]

padron = gpd.GeoDataFrame(
    df_condir, geometry=gpd.points_from_xy(df_condir.long, df_condir.lat))

padron = padron.set_crs("EPSG:4326")

padron_gse = gpd.sjoin(padron, censo, how='left')

padron_gse = padron_gse[['nombre', 'ci', 'genero', 'direccion', 'circunscripcion', 'mesa', 'region', 'provincia', 'comuna', 'lat', 'long', 'HacinClas', 'GSE_final']]

padron_gse = padron_gse.append(df_sindir)

padron_gse.to_csv('padron_censo.csv', index=False)