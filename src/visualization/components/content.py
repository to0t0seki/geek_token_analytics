import streamlit as st
from datetime import timedelta
from src.database.data_access.queries.queries import (get_latest_timestamp,
                                                       get_jst_4am_close_price,
                                                       get_latest_balances,
                                                       get_address_info)
from src.database.data_access.queries.by_category import ( get_all,
                                                           get_game_wallet,
                                                           get_admin,
                                                           get_exchange,
                                                           get_others,
                                                           get_circulating_supply)
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from src.visualization.components.chart import display_chart
from streamlit_local_storage import LocalStorage
from src.database.data_access.database_client import DatabaseClient



def setup_content_page(data_category:str):
    """
    ページの初期化を行う。
    - データベースクライアントの設定
    - サイドバーの表示
    - ヘッダーの表示
    - その他の初期設定
    """

    initialize_page()

    _setup_content(data_category)

def initialize_page(background_image:str = "https://lastmemories.io/special/assets/fankit-assets/PC/01_5_komari.jpg",is_top:bool = False):
        # DBクライアントの初期化
    if 'db_client' not in st.session_state:
        st.session_state.db_client = DatabaseClient()

    if 'show_background' not in st.session_state:
            st.session_state.show_background = True

    st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")
    
    if is_top:
        if st.session_state.show_background:
            style = f'''
            <style>
            .stApp {{
                background-image: url('{background_image}');
                background-size: cover;
                background-repeat: no-repeat;}}
            .stCustomComponentV1 {{
                max-width: 100% !important;
            }}
            .main-svg {{
                background: transparent !important;
            }}
            </style>
            '''
        else:
            style = '''
            <style>
            .stApp {
                background-color: white;
            }
            .stCustomComponentV1 {
                max-width: 100% !important;
            }
            .main-svg {
                background: transparent !important;
            }
            </style>
            '''
    else:
        if st.session_state.show_background:
            style = f'''
            <style>
            .stApp {{
                background-image: url('{background_image}');
                background-size: cover;
                background-repeat: no-repeat;
            }}
            .stCustomComponentV1 {{
                max-width: 80% !important;
            }}
            </style>
            '''
        else:
            style = '''
            <style>
            .stApp {
                background-color: white;
            }
            .stCustomComponentV1 {
                max-width: 80% !important;
            }
            </style>
            '''
    st.markdown(style, unsafe_allow_html=True)

    # サイドバーの設定
    _setup_sidebar()
    # ヘッダーの設定
    _setup_header()

def _setup_sidebar():

    latest_timestamp = get_latest_timestamp(st.session_state.db_client)
    latest_timestamp = (latest_timestamp + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')

    with st.sidebar:
        st.image("img/logo2.jpg", width=200)
        st.page_link("holder_distribution.py", label="ホルダー分布")
        st.page_link("pages/01_transactions_summary.py", label="各種トランザクション情報")
        st.page_link("pages/05_total_max_supply.py", label="総供給量")
        st.page_link("pages/06_circulating_supply.py", label="循環供給量")
        st.page_link("pages/10_game_wallet.py", label="ゲームウォレット残高")
        st.page_link("pages/11_admin.py", label="運営ウォレット残高")
        st.page_link("pages/12_exchange.py", label="取引所残高")
        st.page_link("pages/13_others.py", label="外部ウォレット残高")
        st.page_link("pages/withdrawal_arena_2_usdt.py", label="出金アリーナランキングUSDT")
        st.page_link("pages/withdrawal_arena_2_geek.py", label="出金アリーナランキングGEEK")
        st.page_link("pages/site_guide.py", label="サイトガイド")
        st.page_link("pages/change_log.py", label="更新履歴")
        st.markdown(f"""取り込んだ最新のtx時間  
                      {latest_timestamp}  """)
    



def _setup_header():
    # ヘッダー部分に背景表示・非表示のトグルボタンを配置
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        # 背景表示・非表示のトグルボタン
  
        show_background = st.toggle("背景画像を表示", value=st.session_state.show_background)
        if show_background != st.session_state.show_background:
            st.session_state.show_background = show_background
            st.rerun()
        



def _setup_content(data_category:str):
    params = {"all":{"title":"総供給量"},
          "game_wallet":{"title":"ゲームウォレット残高"},
          "admin":{"title":"運営ウォレット残高"},
          "exchange":{"title":"取引所残高"},
          "others":{"title":"外部ウォレット残高"},
          "circulating_supply":{"title":"循環供給量"}}
    
    def _get_df(data_category:str):
        func= f"get_{data_category}"
        df = globals()[func](st.session_state.db_client)
        return df
    
    st.title(params[data_category]["title"])
    st.write("##### トータル推移")
    
    with st.spinner('データを取得中...'):
        df = _get_df(data_category)
   

    ohlcv_df = get_jst_4am_close_price(st.session_state.db_client)


    geek_price = float(ohlcv_df.iloc[0]['close'])

    merged_df = pd.merge(
        df,
        ohlcv_df[['date','close']],
        left_on='date',
        right_on='date',
        how='left'
    )[['date', 'balance', 'close']]

    merged_df['dollar_base'] = merged_df['balance'] * merged_df['close']
    merged_df['date'] = pd.to_datetime(merged_df['date']).dt.strftime('%Y-%m-%d')

    merged_df.rename(columns={'date':'日付','balance':'保有枚数','close':'終値','dollar_base':'ドル換算'}, inplace=True)

    gb = GridOptionsBuilder.from_dataframe(merged_df)

    gb.configure_column('保有枚数',valueFormatter="Math.floor(value).toLocaleString()")
    gb.configure_column('ドル換算',valueFormatter="Math.floor(value).toLocaleString()")
    gb.configure_column("終値", valueFormatter="value ? value.toFixed(7) : ''")
    gb.configure_grid_options(rowSelection='multiple',enableRangeSelection=True)

    grid_response = AgGrid(
        merged_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.NO_UPDATE,
    )


    display_chart(
        [merged_df[['日付','ドル換算']],'ドル換算','blue','y'],
        [merged_df[['日付','保有枚数']],'保有枚数','red','y2'],
        title='保有枚数とドル換算の推移',
    )

    st.write("##### 個別アドレス")
    local_storage = LocalStorage()


    with st.spinner('データを取得中...'):
        individual_df = get_latest_balances(st.session_state.db_client)

    individual_df['balance'] = (individual_df['balance'].astype(float) / 1e18).round(0)


    match data_category:
        case "all":
            pass
        case "circulating_supply":
            individual_df = individual_df[individual_df['main_type'] != "admin"]
        case _:
            individual_df = individual_df[individual_df['main_type'] == data_category]

    

    individual_df = individual_df[['address', 'balance']]
    individual_df.sort_values(by='balance', ascending=False, inplace=True)
    individual_df.insert(0, 'No', range(1, len(individual_df) + 1))
    individual_df['balance'] = individual_df['balance'].astype(int)
    individual_df['dollar_base'] = individual_df['balance'] * geek_price
    individual_df['dollar_base'] = individual_df['dollar_base'].astype(int)
    individual_df['メモ'] = None




    with open("addresses.json", 'r',encoding='utf-8') as f:
        address_data = json.load(f)

    address_name_map = {item['address']: item['name'] for item in address_data}

    if local_storage.getItem("Note") is not None:
        local_storage_dict = local_storage.getItem("Note")
        address_name_map = address_name_map | local_storage_dict





    individual_df['メモ'] = individual_df['address'].map(address_name_map)
    individual_df.rename(columns={'address':'アドレス','balance':'残高(geek)','dollar_base':'残高(dollar)'}, inplace=True)



    gb = GridOptionsBuilder.from_dataframe(individual_df)
    gb.configure_column('メモ', editable=True)
    gb.configure_selection('single')
    gb.configure_column('アドレス', filter=True)
    gb.configure_columns(["残高(geek)", "残高(dollar)"],valueFormatter="Math.floor(value).toLocaleString()")



    grid_response = AgGrid(
        individual_df,
        gridOptions=gb.build(),
        height=300,
        width='100%',
        theme='streamlit' ,
        update_mode=GridUpdateMode.MANUAL,
        key=data_category
    )



    filtered_df = grid_response['data'].loc[grid_response['data']['メモ'].notna() & (grid_response['data']['メモ'] != '')]
    note_dict = filtered_df.set_index('アドレス').to_dict(orient='index')
    converted_data = {key: value.get("メモ", "") for key, value in note_dict.items()}
    merged_converted_note = address_name_map | converted_data
    local_storage.setItem("Note", merged_converted_note)

    st.write(f"現在のgeek価格: {format(geek_price, '.8f')}ドル")


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
            ohlcv_df,
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
        gb.configure_column("close", valueFormatter="value ? value.toFixed(7) : ''")

        grid_response = AgGrid(
            merged_df,
            gridOptions=gb.build(),
            height=300,
            width='100%',
            theme='streamlit' ,
            update_mode=GridUpdateMode.NO_UPDATE,
            key=f"{data_category}_info_key"
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
