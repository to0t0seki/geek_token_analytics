import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def display_chart(*args:tuple[pd.DataFrame,str,str,str],title:str):
    fig = go.Figure()
    for df,name,color,yaxis in args:
        fig.add_trace(
                go.Scatter(
                    name=name,
                    x=df[df.columns[0]],
                    y=df[df.columns[1]],
                    mode='lines+markers',
                    line=dict(color=color),
                    yaxis=yaxis,
                    customdata=[[df.columns[0], df.columns[1]] for _ in range(len(df))],
                    hovertemplate=(
                    "<b>%{data.name}</b><br>" +
                    "%{customdata[0]}: %{x|%Y-%m-%d}<br>" +  # 日付フォーマットを指定
                    "%{customdata[1]}: %{y:,.0f}<br>" +
                    "<extra></extra>"
                    )
                )
            )
        
    layout_dict = {
        'title': title,
        'xaxis': dict(
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
        # 対数表示切り替えボタンの追加
        'updatemenus': [
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=[
                    dict(
                        args=[{"yaxis.type": "linear"}],
                        label="Linear Scale",
                        method="relayout"
                    ),
                    dict(
                        args=[{"yaxis.type": "log"}],
                        label="Log Scale",
                        method="relayout"
                    )
                ]
            )
        ]
    }

        # 複数軸対応の対数表示切り替えボタン設定
    buttons_args_linear = {f"yaxis{i}.type" if i > 1 else "yaxis.type": "linear" for i in range(1, len(args) + 1)}
    buttons_args_log = {f"yaxis{i}.type" if i > 1 else "yaxis.type": "log" for i in range(1, len(args) + 1)}

    layout_dict['updatemenus'] = [
        dict(
            type="buttons",
            direction="right",
            x=0.7,
            y=1.2,
            showactive=True,
            buttons=[
                dict(
                    args=[buttons_args_linear],
                    label="Linear Scale",
                    method="relayout"
                ),
                dict(
                    args=[buttons_args_log],
                    label="Log Scale",
                    method="relayout"
                )
            ]
        )
    ]
    
    for i, (df, name, color, yaxis) in enumerate(args, 1):
        if i == 1:
            # メインのY軸
            layout_dict['yaxis'] = dict(
                title=df.columns[1],
                title_font=dict(color=color),
                tickfont=dict(color=color),
                side='left'
            )
        else:
            # 追加のY軸
            layout_dict[f'yaxis{i}'] = dict(
                title=df.columns[1],
                title_font=dict(color=color),
                tickfont=dict(color=color),
                overlaying='y',
                side='right',
                range=[df[df.columns[1]].min()*0.5, df[df.columns[1]].max() * 1.1],
                # position=0.85 + (i-2)*0.15  # 3つ目以降の軸は少しずつ右にずらす
            )

    fig.update_layout(**layout_dict)
    st.plotly_chart(fig, use_container_width=True)


def display_nft_sell_chart(df: pd.DataFrame, title: str = None, legend_name:str = None, **kwargs):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df.iloc[:,0], 
            y=df.iloc[:,1],
            hovertemplate=(
            f"{df.columns[0]}: %{{x:,}}<br>" +    # カンマ区切りの数値を維持
            f"{df.columns[1]}: %{{y:,}}<br>" +    # カンマ区切りの数値を維持
            "<extra></extra>"
            ),
            marker_color='#0000FF'))
    fig.update_layout(title=title,
                  xaxis_title=df.columns[0],
                  yaxis_title=df.columns[1],
                  bargap=0.1
                  )    
    st.plotly_chart(fig, use_container_width=True)
