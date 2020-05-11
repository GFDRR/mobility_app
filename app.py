import streamlit as st
import pandas as pd
import pylab as plt
import seaborn as sns
import datetime as dt
import altair as alt
import numpy as np
from scipy.stats import pearsonr
#import geopandas as gpd

st.write('hello')

df = pd.read_csv('data/df_india_may9.csv')
df.ds = pd.to_datetime(df.ds)
df = df.set_index('ds')
df['datetime'] = df.index.copy()

## Header

st.title('Mobility trends of states in India')
st.write('This plot shows change in daily mobility for Facebook users in Indian states starting on March 1, 2020. We look at mean number of grid cells that each user visits during a given day, as picked up from their GPS pings.')
st.write('The chart compares this with February 2020 mobility as a baseline. We see major reductions corresponding with March 22 (the Janata curfew) and March 25 (the lockdown order), though lower-income and more rural states see less of a mobility reduction.')
st.write('States are returning towards pre-lockdown mobility levels although movements remain around 40-60 percent lower.')

default_states = ['Punjab','Maharashtra','Odisha','NCT of Delhi']
states = st.multiselect('Select a state',df.polygon_name.unique().tolist(), default = default_states)

# Line plot

colors = 'rgbycmkrgbycmkrgbycmkrgbycmk'
plt.style.use('seaborn-darkgrid')

f, ax = plt.subplots(figsize = [9,6])
for background_state in df.polygon_name.unique():
    sns.lineplot(x=df.index[df.polygon_name == background_state], y=df["all_day_bing_tiles_visited_relative_change"][df.polygon_name == background_state], color = 'grey', alpha = 0.2, linewidth = 2)
for n, state in enumerate(states):
	col = colors[n]
	sns.lineplot(x=df.index[df.polygon_name == state], y="all_day_bing_tiles_visited_relative_change", color = col,data=df[df.polygon_name == state], linewidth = 3.5)
plt.axvline(dt.datetime(2020, 3, 22),linestyle='--', alpha = 0.5)
plt.axvline(dt.datetime(2020, 3, 24),linestyle='--', alpha = 0.5)
plt.title('Change in daily mobility compared with baseline period', fontsize = 16)
ax.xaxis.set_label_text("")
ax.yaxis.set_label_text("")
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[1:], labels=labels[1:])
 
st.pyplot()

# Table

st.write('This table shows the percentage decline against the pre-lockdown baseline (past 7 days compared with March 1 - 15 period).')

mean_pre_lockdown = df['2020-03-01': '2020-03-15'].groupby('polygon_name')['all_day_bing_tiles_visited_relative_change'].mean()
mean_last_week = df[df.index.unique()[-7]: df.index.unique()[-1]].groupby('polygon_name')['all_day_bing_tiles_visited_relative_change'].mean()
df_change = (mean_last_week - mean_pre_lockdown) * 100
#df_change = pd.DataFrame(df_change.loc[states].sort_values(ascending = True))
df_change = pd.DataFrame(df_change.sort_values(ascending = True))
df_change.columns = ['percent_decline']
df_change['percent_decline'] = ["{:0.1f}".format(num) for num in df_change['percent_decline']]
st.table(df_change)

# altair line chart

st.subheader("Explaining mobility decline with states' characteristics")
st.write('This plot compares decline in mobility during the past 7 days with the February baseline period. Select a variable from income (Net State Domestic Product, US dollars - NSDP), percent population that lives in an urban area, population density (persons per km2), or total population. Income and urban population both correlate with decline in mobility.')
states_df = pd.read_csv('data/states_data.csv')
states_df.nsdp = [x[4:] for x in states_df.nsdp]
states_df.nsdp = states_df.nsdp.str.replace(',','')
states_df.nsdp = states_df.nsdp.astype(int)
states_df.population = states_df.population.str.replace(',','')
states_df.population = states_df.population.astype(int)
states_df.persons_per_km2 = states_df.persons_per_km2.str.replace(',','')
states_df.persons_per_km2 = states_df.persons_per_km2.astype(int)
states_df = states_df.merge(df_change, left_on = 'state', right_on = 'polygon_name')
states_df.percent_decline = states_df.percent_decline.astype(float)
var = st.selectbox('Choose variable: ',['nsdp','persons_per_km2','percent_urban','population'])

#plt.plot(states_df[var], states_df.percent_decline)
states_df.plot.scatter(x = var,y = 'percent_decline')
corr = pearsonr(states_df[var].astype(float),states_df.percent_decline.astype(float))[0]
plt.suptitle('Mobility decline versus {}'.format(var))

st.pyplot()
st.write("Pearson's correlation coefficient: {:.2f}".format(corr))
st.write(states_df)

