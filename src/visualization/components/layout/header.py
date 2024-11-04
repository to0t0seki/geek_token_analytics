import streamlit as st

def display_fixed_header(text: str):
    """
    ページの左上に固定でテキストを表示する関数。

    :param text: 表示するテキスト
    """
    st.markdown(
        f"""
        <style>
        .common-header {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #f0f2f6;
            padding: 10px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        .main-content {{
            padding-top: 60px;  /* ヘッダーの高さに合わせて調整 */
        }}
        </style>
        <div class="common-header">
            <h3 style="margin: 0;">{text}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )