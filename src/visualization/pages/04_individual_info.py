import streamlit as st
import json
import pandas as pd
from src.visualization.components.sidebar import show_sidebar
from src.database.data_access.queries import get_latest_balances_from_all_addresses, get_latest_balances_from_airdrop_recipient, get_latest_balances_from_exchange, get_latest_balances_from_operator, get_address_info, get_jst_4am_close_price
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.visualization.components.chart import display_chart
from src.database.data_access.database_client import DatabaseClient
from streamlit_local_storage import LocalStorage



st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")
style = '''
<style>
.stApp {
    background-image: url('https://lastmemories.io/special/assets/fankit-assets/PC/05_1_sana.jpg');
    background-size: cover;
    background-repeat: no-repeat;
}
.stCustomComponentV1 {
       max-width: 70% !important;
    }

</style>
'''
st.markdown(style, unsafe_allow_html=True)



st.title("個別アドレス情報")
local_storage = LocalStorage()

if 'db_client' not in st.session_state:
    st.session_state.db_client = DatabaseClient()




show_sidebar()

# データソースの選択

data_sources = {
    "全てのアドレス": lambda: get_latest_balances_from_all_addresses(st.session_state.db_client),
    "ユーザーアドレス": lambda: get_latest_balances_from_airdrop_recipient(st.session_state.db_client),
    "取引所": lambda: get_latest_balances_from_exchange(st.session_state.db_client),
    "運営": lambda: get_latest_balances_from_operator(st.session_state.db_client),
}

source_key_map = {
    "全てのアドレス": "all",
    "ユーザーアドレス": "airdrop",
    "取引所": "exchange",
    "運営": "operator",
}


geek_price_df = get_jst_4am_close_price(st.session_state.db_client)
geek_price = float(geek_price_df.iloc[0]['close'])

selected_source = st.selectbox("アドレスのカテゴリーを選択してください:", list(data_sources.keys()))

with st.spinner('データを取得中...'):
    df = data_sources[selected_source]()

safe_source_key = source_key_map[selected_source]

    



df = df[['address', 'balance']]
df.sort_values(by='balance', ascending=False, inplace=True)
df.insert(0, 'No', range(1, len(df) + 1))
df['balance'] = df['balance'].astype(int)
df['dollar_base'] = df['balance'] * geek_price
df['dollar_base'] = df['dollar_base'].astype(int)
df['メモ'] = None




with open("address_notes.json", 'r',encoding='utf-8') as f:
       address_notes = json.load(f)

if local_storage.getItem("Note") is not None:
    local_storage_dict = local_storage.getItem("Note")
    address_notes = address_notes | local_storage_dict





df['メモ'] = df['address'].map(address_notes)
df.rename(columns={'address':'アドレス','balance':'残高(geek)','dollar_base':'残高(dollar)'}, inplace=True)



gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column('メモ', editable=True)
gb.configure_selection('single')
gb.configure_column('アドレス', filter=True)
gb.configure_columns(["残高(geek)", "残高(dollar)"],valueFormatter="Math.floor(value).toLocaleString()")



grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    height=300,
    width='100%',
    theme='streamlit' ,
    update_mode=GridUpdateMode.MANUAL,
    key=safe_source_key
)



#|GridUpdateMode.VALUE_CHANGED
# grid_df_indexed = grid_response['data'].set_index('アドレス')
# df_indexed = df.set_index('アドレス')
# changed_df = df_indexed.compare(grid_df_indexed)


# if not changed_df.empty:
#     st.write(changed_df)
#     other_df = changed_df.xs('other',axis=1,level=1)
#     changed_dict = other_df.to_dict(orient='index')
#     converted_data = {key: value.get("Note", "") for key, value in changed_dict.items()}
#     local_storage.setItem("Note", converted_data)

filtered_df = grid_response['data'].loc[grid_response['data']['メモ'].notna() & (grid_response['data']['メモ'] != '')]
note_dict = filtered_df.set_index('アドレス').to_dict(orient='index')
converted_data = {key: value.get("メモ", "") for key, value in note_dict.items()}
merged_converted_note = address_notes | converted_data
local_storage.setItem("Note", merged_converted_note)

st.write(f"現在のgeek価格: {geek_price}ドル")
st.markdown('''
アドレスの詳細を見る際は、アドレス選択後「UPDATE」ボタン。
            
##### メモ機能を実装しました。  
メモを書き込めます。気になるアドレスのメモにご利用下さい。  
上手く保存できない場合があるのでご容赦ください。  
##### 使い方  
メモを編集後「UPDATE」ボタンで保存。  
メモ入力後、入力が確定されていないと保存されないので注意（他の行を選択してUPDATEの方がいいかも）。  
ブラウザのローカルストレージに保存されますので、「ブラウザのキャッシュ削除」でメモも削除されます。

''')


if st.button("メモを全削除"):
    local_storage.deleteItem("Note")
    st.rerun()


st.write("")
st.write("")

if grid_response['selected_rows'] is not None:
    selected_row = grid_response['selected_rows']

    st.write(f"選択されたアドレス: {selected_row.iloc[0]['アドレス']}, メモ: {selected_row.iloc[0]['メモ']}")
    address_info_df = get_address_info(st.session_state.db_client, selected_row.iloc[0]['アドレス'])
    merged_df = pd.merge(
        address_info_df,
        geek_price_df,
        left_on='date',
        right_on='date',
        how='left'
    )[['date','close', 'balance', 'airdrop', 'withdraw', 'deposit']]

    merged_df['balance_dollar_base'] = merged_df['close'] * merged_df['balance']
    merged_df['airdrop_dollar_base'] = merged_df['close'] * merged_df['airdrop']
    merged_df['withdraw_dollar_base'] = merged_df['close'] * merged_df['withdraw']
    merged_df['deposit_dollar_base'] = merged_df['close'] * merged_df['deposit']

    merged_df['date'] = pd.to_datetime(merged_df['date']).dt.strftime('%Y-%m-%d')
    
    # 複数カラムを一度にround
    merged_df[['balance', 'airdrop', 'withdraw', 'deposit', 
            'balance_dollar_base', 'airdrop_dollar_base', 
            'withdraw_dollar_base', 'deposit_dollar_base']] = \
        merged_df[['balance', 'airdrop', 'withdraw', 'deposit',
                'balance_dollar_base', 'airdrop_dollar_base',
                'withdraw_dollar_base', 'deposit_dollar_base']].round(0)


    merged_df.rename(columns={'date':'日付','balance':'残高(geek)','airdrop':'エアドロ(geek)','withdraw':'出金(geek)','deposit':'入金(geek)'}, inplace=True)
    merged_df.rename(columns={'balance_dollar_base':'残高(dollar)','airdrop_dollar_base':'エアドロ(dollar)','withdraw_dollar_base':'出金(dollar)','deposit_dollar_base':'入金(dollar)'}, inplace=True)
    gb = GridOptionsBuilder.from_dataframe(merged_df)
    gb.configure_columns(["残高(geek)", "エアドロ(geek)", "出金(geek)", "入金(geek)","残高(dollar)","エアドロ(dollar)","出金(dollar)","入金(dollar)"],valueFormatter="Math.floor(value).toLocaleString()")
    gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)

    grid_response = AgGrid(
        merged_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.NO_UPDATE,
        key=f"{safe_source_key}_info"
    )
    display_chart(
        [merged_df[['日付','残高(dollar)']], 'dollar', 'blue', 'y'],


        [merged_df[['日付','残高(geek)']], 'geek', 'red', 'y2'],
        title="残高推移",
    )

    display_chart(
        [merged_df[['日付','エアドロ(dollar)']], 'dollar', 'blue', 'y'],
        [merged_df[['日付','エアドロ(geek)']], 'geek', 'red', 'y2'],
        title="エアドロップ取得推移",
    )

    display_chart(
        [merged_df[['日付','出金(dollar)']], 'dollar', 'blue', 'y'],
        [merged_df[['日付','出金(geek)']], 'geek', 'red', 'y2'],
        title="出金推移",
    )

    display_chart(
        [merged_df[['日付','入金(dollar)']], 'dollar', 'blue', 'y'],
        [merged_df[['日付','入金(geek)']], 'geek', 'red', 'y2'],
        title="入金推移",
    )




