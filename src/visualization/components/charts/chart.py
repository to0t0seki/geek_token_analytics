import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def create_chart(df: pd.DataFrame, title: str, chart_type: str,legend_name:str):
    fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=(title,)
        )

    if chart_type == 'line':
        fig.add_trace(
            go.Scatter(
                name=legend_name,
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
    elif chart_type == 'bar':
        fig.add_trace(
            go.Bar(
                name=legend_name,
                x=df[df.columns[0]],
                y=df[df.columns[1]],
            )
        )
    else:
        raise ValueError(f"Invalid chart type: {chart_type}")
    
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

def display_chart(df: pd.DataFrame, title: str = 'チャート', chart_type: str = 'line',legend_name:str = None, **kwargs):
    """
    チャートを作成し、Streamlitで表示する関数
    
    :param df: 入力データフレーム
    :param title: チャートのタイトル
    :param chart_type: チャートのタイプ
    :param legend_name: 凡例の名前
    :param kwargs: その他のオプション引数
    """
    chart = create_chart(df, title, chart_type, legend_name, **kwargs)
    st.plotly_chart(chart, use_container_width=True)

def display_chart1(df: pd.DataFrame, df2: pd.DataFrame, title: str = None, **kwargs):
    chart = create_chart1(df, df2, title, **kwargs)
    st.plotly_chart(chart, use_container_width=True)


def display_nft_sell_chart(df: pd.DataFrame, title: str = None, legend_name:str = None, **kwargs):
    fig = go.Figure(data=[go.Bar(x=df['buy_count'], 
                                 y=df['count'],
                                 hovertemplate=(
                                "人数: %{x:,}<br>" +    # カンマ区切りの数値
                                "購入個数: %{y:,}<br>" +      # カンマ区切りの数値
                                "<extra></extra>"           # 余分な情報を非表示
                                ),
                                
                                 marker_color='#0000FF')])
    fig.update_layout(title=title,
                  xaxis_title='人数',
                  yaxis_title='購入個数',
                  bargap=0.1
                  )    
    st.plotly_chart(fig, use_container_width=True)
