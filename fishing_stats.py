import math
import pandas as pd
import streamlit as st
import datetime
@st.cache_data
def load_data(filename, **kwargs):
    return pd.read_csv(filename, **kwargs)


def main():
    st.title('ChattyKathy Fishing Stats')
    data=load_data('FishingLog.csv',low_memory=False)
    try:
        data2=load_data("https://www.dropbox.com/scl/fi/zhop5outw301q2pfjwrl1/FishingLogUpdated.txt?rlkey=ush67h3eqhdt1geoq0e8mvppf&st=2zuiqwmu&dl=1",header=0,skiprows=range(1,11005),low_memory=False)
        data2.loc[data2['FishName']=='Pickle','FishName']='Big Mamma Pickle'
        data2.loc[data2['FishName']=='Keys','FishName']='Some Keys'
        data2.loc[data2['FishName']=='Henrys Shoe','FishName']="Henry's Shoe"
        data2.loc[data2['FishName']=='Fish Drawing','FishName']='Weird Drawing of a Fish?'
    except pd.errors.EmptyDataError:
        print("Not Enough rows")
        data2=pd.DataFrame()
    if not data2.empty:
        data=pd.concat([data,data2],ignore_index=True)
    choicereset=st.multiselect('ResetDate:',data['ResetDate'].unique())
    filtered_data=data
    if choicereset:
        filtered_data=filtered_data[filtered_data['ResetDate'].isin(choicereset)]
    #filtered_data['date']=pd.to_datetime(data['date'],errors='coerce',yearfirst=True)
    filtered_data.loc[:,'DateTime']=pd.to_datetime(filtered_data['DateTime'], format="%m/%d/%Y %I:%M:%S %p",errors='coerce').dt.tz_localize("UTC")
    #print(filtered_data[filtered_data['date']=='NaT'])
    valid_dates=filtered_data['DateTime'].dropna()
    if not valid_dates.empty:
        min_dt=valid_dates.min().date()
        max_dt=valid_dates.max().date()
    else:
        min_dt=datetime.date(2024,1,1)
        max_dt=datetime.date(2034,1,1)
    start_date=pd.Timestamp(st.date_input("Start Date",min_value=min_dt,max_value=max_dt,value=min_dt)).tz_localize('UTC')
    end_date=pd.Timestamp(st.date_input("End Date",min_value=min_dt,max_value=max_dt,value=max_dt))+ pd.Timedelta(days=1)
    end_date=end_date.tz_localize('UTC')
    if start_date > end_date:
        st.error('Error: End date must be greater than start date.')
    else:
        filtered_data=filtered_data[(filtered_data['DateTime']>=start_date) &(filtered_data['DateTime']<=end_date)]
    if choicefishtype:
        filtered_data=filtered_data[filtered_data['Category'].isin(choicefishtype)]
    choicefishrarity=st.multiselect("Pick Fish Rarity:",pd.Series(['Junk','Common','Uncommon','Rare','Epic','Legendary']))
    if choicefishrarity:
        filtered_data=filtered_data[filtered_data['Rarity'].isin(choicefishrarity)]
    max_weight=max(filtered_data['Weight'].astype(float))
    start_weight,end_weight=st.slider('Fish weight:',min_value=0.0,max_value=max_weight,value=(0.0,max_weight))
    filtered_data=filtered_data[(filtered_data['Weight']>=start_weight)&(filtered_data['Weight']<=end_weight)]

    max_coins=max(filtered_data['Value'].astype(int))
    start_coins,end_coins=st.slider('Fish Gold:',min_value=1,max_value=max_coins,value=(1,max_coins))
    filtered_data=filtered_data[(filtered_data['Value']>=start_coins)&(filtered_data['Value']<=end_coins)]
    choiceuser=st.multiselect("Pick User:",sorted(filtered_data['Username'].unique()))

    if choiceuser:
        filtered_data=filtered_data[filtered_data['Username'].isin(choiceuser)]
    choicefish=st.multiselect("Pick Fish:",sorted(filtered_data['FishName'].unique()))
    if choicefish:
        filtered_data=filtered_data[filtered_data['FishName'].isin(choicefish)]
    choice0=st.selectbox('GroupBy:',['Catch','Fish','User'])

    filtered_data=filtered_data.rename(columns={'Username':'User','Value':'Gold'})
    x=filtered_data.reset_index()
    if choice0=='User':
        x=filtered_data.groupby(['User']).agg(
            TotalCatches=('FishName','count'),
            TotalGold=('Gold','sum'),
            FishesCaught=('FishName',lambda x:x.nunique()),
            FirstCatches=('IsNew',lambda x: (x=='New').sum()),
            BiggestCatch=('Gold','max'),
            BiggestCatchIndex=('Gold','idxmax'),
            HeaviestCatch=('Weight','max'),
            HeaviestCatchIndex=('Weight','idxmax'),
        ).reset_index()
        x=x.sort_values(by='TotalCatches',ascending=False)
        x['BiggestCatchFish']=""
        x['HeaviestCatchFish']=""
        for idx,row in x.iterrows():
            index1=row['BiggestCatchIndex']
            x.loc[idx,'BiggestCatchFish']=filtered_data.loc[index1,'FishName']
            index2=row['HeaviestCatchIndex']
            x.loc[idx,'HeaviestCatchFish']=filtered_data.loc[index2,'FishName']
        if st.button('Check Stats'):
            x=x.drop(columns=['BiggestCatchIndex','HeaviestCatchIndex'])
            st.dataframe(x)
    elif choice0=='Fish':
        choicemissing=False
        if choiceuser:
            choicemissing=st.checkbox("Show Missing",value=False)
        if choicemissing:
            unique_x=set(filtered_data['FishName'].unique())
            unique_y=set(data['FishName'].unique())
            missing=unique_y-unique_x
            missing_rows=data[data['FishName'].isin(missing)]
            result=(missing_rows.sort_values('Rarity')).groupby('FishName').agg({'Category':'last','Rarity':'last'}).reset_index()
            if choicefishrarity:
                result=result[result['Rarity'].isin(choicefishrarity)]
            if choicefishtype:
                result=result[result['Category'].isin(choicefishtype)]        
        else:
            x=filtered_data.groupby(['FishName','Category']).agg(
                TotalCatches=('FishName','count'),
                BiggestCatch=('Gold','max'),
                HeaviestCatch=('Weight','max'),
                UniqueCatchers=('User',lambda x:x.nunique()),
                FirstCatch=('DateTime','min'),
                FirstFishCatcherIndex=('DateTime','idxmin'),
                BiggestFishCatcherIndex=('Weight','idxmax'),
            ).reset_index()
            x=x.sort_values(by='TotalCatches',ascending=False)
            x['BiggestFishCatcher']=""
            x['FirstFishCatcher']=""
            for idx,row in x.iterrows():
                index1=row['BiggestFishCatcherIndex']
                x.loc[idx,'BiggestFishCatcher']=filtered_data.loc[index1,'User']
                index2=row['FirstFishCatcherIndex']
                x.loc[idx,'FirstFishCatcher']=filtered_data.loc[index2,'User']
            x=x.rename(columns={'FishName':'Fish'}).reset_index()
            x=x.drop(columns=['BiggestFishCatcherIndex','FirstFishCatcherIndex','index'])
        if st.button('Check Stats'):
            if choicemissing:
                st.dataframe(result)
            else:
                if choiceuser:
                    x=x.drop(columns=['BiggestFishCatcher','FirstFishCatcher','UniqueCatchers'])
                st.dataframe(x)
    elif choice0=='Catch':
        x=x.drop(columns=['Rating','Date','Time','ResetDate','index']).reset_index()
        x=x.reindex(index=x.index[::-1])
        x=x.rename(columns={'FishName':'Fish'})
        x=x.loc[:,['Fish','User','Gold','Weight','Rarity','Category','DateTime','IsNew']]
        st.dataframe(x)

if __name__=='__main__':
    main()
