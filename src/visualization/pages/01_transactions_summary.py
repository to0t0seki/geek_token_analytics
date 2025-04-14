import streamlit as st
from src.visualization.components.chart import display_chart
from src.database.data_access.queries.queries import get_transaction_summary, get_jst_4am_close_price
from src.visualization.components.content import initialize_page
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd



initialize_page()


st.title("各種トランザクション情報")


with st.spinner('データを取得中...'):
    df = get_transaction_summary(st.session_state.db_client)

params={
    'xgeekToGeek':{
        "title":"入金",
        "memo":"ラスメモマイページでのGeekからxGeekへの変換",
    },
    'exportToken':{
        "title":"出金",
        "memo":None,
    },
    'transferForBuy':{
        "title":"アイテム購入",
        "memo":"Geekショップでの購入に使われたGeek",
    },
    'exportAdp':{
        "title":"エアドロップ",
        "memo":None,
    }
}

ohlcv_df = get_jst_4am_close_price(st.session_state.db_client)

def display_transaction_summary(df:pd.DataFrame, method:str):
    st.write(f"### {params[method]['title']}")
    if params[method]['memo'] is not None:
        st.markdown(params[method]['memo'])

    df = df[df['method']==method]

    
    merged_df = pd.merge(
        df[['date', 'amount', 'address_count']],
        ohlcv_df[['date','close']],
        left_on='date',
        right_on='date',
        how='left'
    )[['date', 'amount', 'close','address_count']]
    merged_df['dollar_base'] = merged_df['close'] * merged_df['amount']
    merged_df= merged_df[['date','amount','close','dollar_base','address_count']]
    merged_df['dollar_base'] = merged_df['dollar_base'].round(0)
    merged_df['date'] = pd.to_datetime(merged_df['date']).dt.strftime('%Y-%m-%d')
    merged_df.rename(columns={'date':'日付','amount':f'{params[method]["title"]}枚数','address_count':'ユニークアドレス数','close':'終値','dollar_base':'ドル換算'}, inplace=True)

    gb = GridOptionsBuilder.from_dataframe(merged_df)
    gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)
    gb.configure_columns(
        [f'{params[method]["title"]}枚数', "ユニークアドレス数", "ドル換算"],
        valueFormatter="Math.floor(value).toLocaleString()"
    )


    grid_response = AgGrid(
        merged_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.NO_UPDATE,
        key=f'{method}_grid'
    )

    total_deposits = merged_df[f"{params[method]['title']}枚数"].sum()
    total_dollar_base = merged_df['ドル換算'].sum()
    st.markdown(f"総{params[method]['title']}枚数: {total_deposits:,.0f} ドル換算: {total_dollar_base:,.0f}")
    st.markdown("\n\n\n")

    return merged_df

deposits_df = display_transaction_summary(df, 'xgeekToGeek')
withdrawals_df = display_transaction_summary(df, 'exportToken')

display_chart(
    [deposits_df[['日付','ドル換算']],'入金','blue','y'],
    [withdrawals_df[['日付','ドル換算']],'出金','red','y'],
    title='入出金のドル換算推移',
)

item_purchases_df = display_transaction_summary(df, 'transferForBuy')

display_chart(
    [item_purchases_df[['日付','ドル換算']],'ドル換算','blue','y'],
    [item_purchases_df[['日付','アイテム購入枚数']],'枚数','red','y2'],
    title='Geekショップの購入推移',
)

airdrops_df = display_transaction_summary(df, 'exportAdp')

display_chart(
    [airdrops_df[['日付','ドル換算']],'ドル換算','blue','y'],
    [airdrops_df[['日付','エアドロップ枚数']],'枚数','red','y2'],
    title='エアドロップの推移',
)



