import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def create_chart(df: pd.DataFrame, title: str = None, y_axis_titles: dict = None, **kwargs):
    # 2カラムの場合（1つのサブプロット、2軸）
    fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=(title,)
        )

    # 左Y軸の折れ線
    fig.add_trace(
        go.Scatter(
            name='エアドロップ',
                x=df[df.columns[0]],
                y=df[df.columns[1]],
                mode='lines+markers',
                line=dict(color='blue'),
                hovertemplate=(
                "日時: %{x|%Y-%m-%d}<br>" +  # 日付フォーマットを指定
                "枚数: %{y:,.0f}<br>" +
                "<extra></extra>"
                )
            )
        )
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all", label="All")
                    ])
                ),
                fixedrange=True
            ),
             yaxis=dict(
                range=[df[df.columns[1]].min()*0.5, df[df.columns[1]].max() * 1.1],  # 最大値の10%余裕を持たせる
                fixedrange=True
            )
        )

    # 共通のレイアウト設定
    # fig.update_layout(
    #     height=800,
    #     showlegend=True,
    #     title_text="Dynamic Subplots"
    # )
    
    return fig

def create_chart1(df: pd.DataFrame, df2: pd.DataFrame, title: str, **kwargs):
    fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=(title,)
        )

    # 左Y軸の折れ線
    fig.add_trace(
            go.Scatter(
                name='入金',
                x=df[df.columns[0]],
                y=df[df.columns[1]],
                mode='lines+markers',
                line=dict(color='blue'),
                hovertemplate=(
                "<b>入金情報</b><br>" +
                "日時: %{x|%Y-%m-%d}<br>" +  # 日付フォーマットを指定
                "枚数: %{y:,.0f}<br>" +
                "<extra></extra>"
                )
            )
        )
    fig.add_trace(
            go.Scatter(
                name='出金',
                x=df2[df2.columns[0]],
                y=df2[df2.columns[1]],
                mode='lines+markers',
                line=dict(color='red'),
                hovertemplate=(
                "<b>出金情報</b><br>" +
                "日時: %{x|%Y-%m-%d}<br>" +  # 日付フォーマットを指定
                "枚数: %{y:,.0f}<br>" +
                "<extra></extra>"
                )
            )
        )
    
    fig.update_layout(
            xaxis=dict(
                rangeslider=dict(visible=True),
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all", label="All")
                    ])
                ),
                fixedrange=True
            )
           
        )

    return fig

def display_chart(df: pd.DataFrame, title: str = None, y_axis_titles: dict = None, **kwargs):
    """
    チャートを作成し、Streamlitで表示する関数
    
    :param df: 入力データフレーム
    :param title: チャートのタイトル
    :param y_axis_titles: Y軸のタイトル（辞書形式）
    :param kwargs: その他のオプション引数
    """
    chart = create_chart(df, title, y_axis_titles, **kwargs)
    st.plotly_chart(chart, use_container_width=True)

def display_chart1(df: pd.DataFrame, df2: pd.DataFrame, title: str = None, **kwargs):
    chart = create_chart1(df, df2, title, **kwargs)
    st.plotly_chart(chart, use_container_width=True)
