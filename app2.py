import streamlit as st
import pandas as pd
import seaborn as sns
import pylab as plt
import datetime as dt
#import geopandas as gpd

df = pd.read_csv('/Users/nicholasjones/Desktop/code/wbg-location-data/notebooks/nick/df_india_may9.csv')
df.ds = pd.to_datetime(df.ds)
df = df.set_index('ds')
df['datetime'] = df.index.copy()

## Header

st.title('Mobility trends of states in India')
st.write('This app visualizes mobility trends for states in India, based on the Facebook movement range maps data.')

default_states = ['Gujarat','NCT of Delhi','West Bengal','Rajasthan','Tamil Nadu','Maharashtra','Bihar']
states = st.multiselect('Select a state',df.polygon_name.unique())

# Line plot

colors = 'rgbycmkrgbycmkrgbycmkrgbycmk'

f, ax = plt.subplots(figsize = [9,9])
for background_state in df.polygon_name.unique():
    sns.lineplot(x=df.index[df.polygon_name == background_state], y=df["all_day_bing_tiles_visited_relative_change"][df.polygon_name == background_state], color = 'grey', alpha = 0.3, linewidth = 1)
for n, state in enumerate(list(states)):
	col = colors[n]
	ax = sns.lineplot(x=df.index[df.polygon_name == state], y="all_day_bing_tiles_visited_relative_change", color = col,data=df[df.polygon_name == state], linewidth = 4)
plt.axvline(dt.datetime(2020, 3, 22),linestyle='--', alpha = 0.5)
plt.axvline(dt.datetime(2020, 3, 24),linestyle='--', alpha = 0.5)
plt.title('Percent users remaining in home grid cell all day', fontsize = 16);
 
st.write(f)

df

## Map

gdf = gpd.read_file('/Users/nicholasjones/Desktop/code/data/FB/India/gadm36_IND_shp/gadm36_IND_1.shp')
gdf = gdf[['NAME_1','geometry']]

income_data = pd.read_csv('/Users/nicholasjones/Desktop/code/data/FB/India/NSDP_per_capita.csv',names=['state','nsdp_USD'])
income_data = income_data.dropna()
income_data.nsdp_USD = [x[4:] for x in income_data.nsdp_USD]
income_data.nsdp_USD = income_data.nsdp_USD.str.replace(',','')
income_data.nsdp_USD = income_data.nsdp_USD.astype(int)

gdf = gpd.GeoDataFrame(df.merge(gdf, left_on='polygon_name', right_on = 'NAME_1'))
gdf = gdf[['NAME_1','all_day_bing_tiles_visited_relative_change','all_day_ratio_single_tile_users','geometry','datetime']]
gdf.head(1)

mydate = st.selectbox('Select a date',['2020-03-05','2020-03-22','2020-04-29'])
f = gdf[gdf.datetime == mydate].plot(column = 'all_day_bing_tiles_visited_relative_change')
st.pyplot()
