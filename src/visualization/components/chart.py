import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def display_chart(df: pd.DataFrame, title: str, chart_type: str,legend_name:str):
    fig = make_subplots(
            rows=1, cols=1,
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
                "日付: %{x|%Y-%m-%d}<br>" +  # 日付フォーマットを指定
                "ドル: %{y:,.0f}<br>" +
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
        title=title,
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

    st.plotly_chart(fig, use_container_width=True)

def display_chart1(df1: pd.DataFrame, df2: pd.DataFrame, title: str = None, **kwargs):
    fig = make_subplots(
            rows=1, cols=1,
        )

    # 左Y軸の折れ線
    fig.add_trace(
            go.Scatter(
                name='入金',
                x=df1[df1.columns[0]],
                y=df1[df1.columns[1]],
                mode='lines+markers',
                line=dict(color='blue'),
                hovertemplate=(
                "<b>入金</b><br>" +
                "日付: %{x|%Y-%m-%d}<br>" +  # 日付フォーマットを指定
                "ドル: %{y:,.0f}<br>" +
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
                "<b>出金</b><br>" +
                "日付: %{x|%Y-%m-%d}<br>" +  # 日付フォーマットを指定
                "ドル: %{y:,.0f}<br>" +
                "<extra></extra>"
                )
            )
        )
    
    fig.update_layout(
            title=title,
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

    st.plotly_chart(fig, use_container_width=True)




def display_nft_sell_chart(df: pd.DataFrame, title: str = None, legend_name:str = None, **kwargs):
    fig = go.Figure(data=[go.Bar(x=df.iloc[:,0], 
                                y=df.iloc[:,1],
                                hovertemplate=(
                                f"{df.columns[0]}: %{{x:,}}<br>" +    # カンマ区切りの数値を維持
                                f"{df.columns[1]}: %{{y:,}}<br>" +    # カンマ区切りの数値を維持
                                "<extra></extra>"
                                ),
                                marker_color='#0000FF')])
    fig.update_layout(title=title,
                  xaxis_title=df.columns[0],
                  yaxis_title=df.columns[1],
                  bargap=0.1
                  )    
    st.plotly_chart(fig, use_container_width=True)

def display_supply_and_price_chart(df: pd.DataFrame, title: str = None, **kwargs):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[df.columns[0]],
        y=df[df.columns[1]],
        name=df.columns[1],
        mode='lines+markers',
        line=dict(color='blue'),
        yaxis='y',
        hovertemplate=(
        "日付: %{x|%Y-%m-%d}<br>" +    
        "枚数: %{y:,.0f}<br>" +      
        "<extra></extra>"           
        )
    ))
    fig.add_trace(go.Scatter(
        x=df[df.columns[0]],
        y=df[df.columns[2]],
        name=df.columns[2],
        mode='lines+markers',
        line=dict(color='red'),
        yaxis='y2',
        hovertemplate=(
        "日付: %{x|%Y-%m-%d}<br>" +    
        "ドル: $%{y:,.0f}<br>" +      
        "<extra></extra>"           
        )
    ))
    fig.update_layout(
        title=title,
        xaxis=dict(title='日付',
                   rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all", label="All")
                    ])
                ),
        # レンジスライダー（下部のスライダー）
        rangeslider=dict(visible=True),
        type="date"),
        yaxis=dict(
            title='保有枚数',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title='ドル換算',
            titlefont=dict(color='red'),
            tickfont=dict(color='red'),
            overlaying='y',
            side='right'
        )
    )
    st.plotly_chart(fig, use_container_width=True)
