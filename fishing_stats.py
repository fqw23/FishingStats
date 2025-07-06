import math
import pandas as pd
import streamlit as st
import datetime
@st.cache_data
def load_data(file):
    data=pd.read_csv(file,low_memory=False)
    return data
def main():
    st.title('ChattyKathy Fishing Stats')
    data=load_data('FullData.csv')
    choicereset=st.multiselect('ResetDate:',data['Reset Date'].unique())
    filtered_data=data
    if choicereset:
        filtered_data=filtered_data[filtered_data['Reset Date'].isin(choicereset)]
    filtered_data['date']=pd.to_datetime(data['date'],errors='coerce',yearfirst=True)
    filtered_data['DateTime']=pd.to_datetime(filtered_data['DateTime'], dayfirst=True, format="%d/%m/%Y %I:%M:%S %p",errors='coerce').dt.tz_localize("UTC")
    print(filtered_data[filtered_data['date']=='NaT'])
    valid_dates=filtered_data['date'].dropna()
    if not valid_dates.empty:
        min_dt=valid_dates.min().date()
        max_dt=valid_dates.max().date()
    else:
        min_dt=datetime.date(2024,1,1)
        max_dt=datetime.date(2034,1,1)
    start_date=st.date_input("Start Date",min_value=min_dt,max_value=max_dt,value=min_dt)
    end_date=st.date_input("End Date",min_value=min_dt,max_value=max_dt,value=max_dt)
    if start_date > end_date:
        st.error('Error: End date must be greater than start date.')
    choicefishtype=st.multiselect("Pick Fish Category:",filtered_data['category'].unique())
    if choicefishtype:
        filtered_data=filtered_data[filtered_data['category'].isin(choicefishtype)]
    choicefishrarity=st.multiselect("Pick Fish Rarity:",filtered_data['rarity'].unique())
    if choicefishrarity:
        filtered_data=filtered_data[filtered_data['rarity'].isin(choicefishrarity)]
    max_weight=max(filtered_data['weight'].astype(float))
    start_weight,end_weight=st.slider('Fish weight:',min_value=0.0,max_value=max_weight,value=(0.0,max_weight))
    filtered_data=filtered_data[(filtered_data['weight']>=start_weight)&(filtered_data['weight']<=end_weight)]

    max_coins=max(filtered_data['value'].astype(int))
    start_coins,end_coins=st.slider('Fish Coin:',min_value=1,max_value=max_coins,value=(1,max_coins))
    filtered_data=filtered_data[(filtered_data['value']>=start_coins)&(filtered_data['value']<=end_coins)]
    if choiceuser:
        filtered_data=filtered_data[filtered_data['username'].isin(choiceuser)]
    choicefish=st.multiselect("Pick Fish:",filtered_data['fishname'].unique())
    if choicefish:
        filtered_data=filtered_data[filtered_data['fishname'].isin(choicefish)]
    choice0=st.selectbox('GroupBy:',['User','Fish','Catch'])

    choice0=st.selectbox('GroupBy:',['User','Fish','Catch'])

    filtered_data=filtered_data.rename(columns={'username':'User'})
    x=filtered_data.reset_index()
    if choice0=='User':
        x=filtered_data.groupby(['User']).agg(
            TotalCatches=('fishname','count'),
            TotalCoins=('value','sum'),
            FishesCaught=('fishname',lambda x:x.nunique()),
            FirstCatches=('isNew',lambda x: (x=='New').sum()),
            BiggestCatch=('value','max'),
            BiggestCatchIndex=('value','idxmax'),
            HeaviestCatch=('weight','max'),
            HeaviestCatchIndex=('weight','idxmax'),
        ).reset_index()
        x=x.sort_values(by='TotalCatches',ascending=False)
        x['BiggestCatchFish']=""
        x['HeaviestCatchFish']=""
        for idx,row in x.iterrows():
            index1=row['BiggestCatchIndex']
            x.loc[idx,'BiggestCatchFish']=filtered_data.loc[index1,'fishname']
            index2=row['HeaviestCatchIndex']
            x.loc[idx,'HeaviestCatchFish']=filtered_data.loc[index2,'fishname']
        if st.button('Check Stats'):
            x=x.drop(columns=['BiggestCatchIndex','HeaviestCatchIndex'])
            st.dataframe(x)
    elif choice0=='Fish':
        choicemissing=False
        if choiceuser:
            choicemissing=st.checkbox("Show Missing",value=False)
        if choicemissing:
            unique_x=set(filtered_data['fishname'].unique())
            unique_y=set(data['fishname'].unique())
            missing=unique_y-unique_x
            missing_rows=data[data['fishname'].isin(missing)]
            result=(missing_rows.sort_values('rarity')).groupby('fishname').agg({'category':'last','rarity':'last'}).reset_index()
        else:
            x=filtered_data.groupby(['fishname']).agg(
                TotalCatches=('fishname','count'),
                BiggestCatch=('value','max'),
                HeaviestCatch=('weight','max'),
                UniqueCatchers=('User',lambda x:x.nunique()),
                FirstCatch=('DateTime','min'),
                FirstFishCatcherIndex=('DateTime','idxmin'),
                BiggestFishCatcherIndex=('weight','idxmax'),
            ).reset_index()
            x=x.sort_values(by='TotalCatches',ascending=False)
            x['BiggestFishCatcher']=""
            x['FirstFishCatcher']=""
            for idx,row in x.iterrows():
                index1=row['BiggestFishCatcherIndex']
                x.loc[idx,'BiggestFishCatcher']=filtered_data.loc[index1,'User']
                index2=row['FirstFishCatcherIndex']
                x.loc[idx,'FirstFishCatcher']=filtered_data.loc[index2,'User']
            x=x.rename(columns={'fishname':'Fish'}).reset_index()
            x=x.drop(columns=['BiggestFishCatcherIndex','FirstFishCatcherIndex','index'])
        if st.button('Check Stats'):
            if choicemissing:
                st.dataframe(result)
            #x=x.drop(columns=['rating','date','time','Reset Date','index'])
            else:
                st.dataframe(x)
    elif choice0=='Catch':
        if st.button('Check Stats'):
            x=x.drop(columns=['rating','date','time','Reset Date','index'])
            st.dataframe(x)

if __name__=='__main__':
    main()
