import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from typing import Any

def create_chart(df: pd.DataFrame, title: str = None, y_axis_titles: dict = None, **kwargs):
    """
    データフレームのカラム数に応じて動的にサブプロットを作成する
    
    :param df: データフレーム（最初の列は日付を想定）
    :return: Plotly Figure オブジェクト
    """
    num_columns = len(df.columns)

    if num_columns == 2:
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
                mode='lines',
                line=dict(color='blue')
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

        

        
        # # Y軸のタイトル設定
        # fig.update_yaxes(title_text=df.columns[1], secondary_y=False)
        # fig.update_yaxes(title_text=df.columns[2], secondary_y=True)

    elif num_columns == 3:
        # 3カラムの場合（2つのサブプロット）
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=('Main Plot', 'Volume'),
            specs=[[{"secondary_y": True}],
                  [{"secondary_y": False}]]
        )
        
        # メインプロット（2つの折れ線）
        fig.add_trace(
            go.Scatter(
                name=df.columns[1],
                x=df.index,
                y=df[df.columns[1]],
                mode='lines'
            ),
            row=1, col=1,
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                name=df.columns[2],
                x=df.index,
                y=df[df.columns[2]],
                mode='lines'
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        # ボリュームプロット
        fig.add_trace(
            go.Bar(
                name=df.columns[3],
                x=df.index,
                y=df[df.columns[3]]
            ),
            row=2, col=1
        )
        
    elif num_columns == 4:
        # 4カラムの場合（4つのサブプロット）
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.4, 0.2, 0.2, 0.2],
            subplot_titles=('Main Plot', 'Volume 1', 'Additional Data', 'Volume 2'),
            specs=[[{"secondary_y": True}],
                  [{"secondary_y": False}],
                  [{"secondary_y": True}],
                  [{"secondary_y": False}]]
        )
        
        # メインプロット（2つの折れ線）
        fig.add_trace(
            go.Scatter(
                name=df.columns[1],
                x=df.index,
                y=df[df.columns[1]],
                mode='lines'
            ),
            row=1, col=1,
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                name=df.columns[2],
                x=df.index,
                y=df[df.columns[2]],
                mode='lines'
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        # 追加のプロット
        for i, col in enumerate(df.columns[3:], start=2):
            fig.add_trace(
                go.Bar(
                    name=col,
                    x=df.index,
                    y=df[col]
                ),
                row=i, col=1
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
                mode='lines',
                line=dict(color='blue')
            )
        )
    fig.add_trace(
            go.Scatter(
                name='出金',
                x=df2[df2.columns[0]],
                y=df2[df2.columns[1]],
                mode='lines',
                line=dict(color='red')
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
