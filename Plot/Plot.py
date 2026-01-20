import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_plotly_chart(df, trades_df, equity_curve, final_value, start_value):
    """使用 Plotly 生成互動式回測圖表"""
    
    # 計算移動平均線
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # 建立子圖
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.3, 0.55, 0.25],
        subplot_titles=("Equity", "OHLC Chart", "Volume")
    )
    
    # 第1圖：權益曲線
    fig.add_trace(
        go.Scatter(
            x=equity_curve.index,
            y=equity_curve.values,
            mode='lines',
            name='Equity',
            cliponaxis=False, # 確保線條不會被裁切
            line=dict(color='#1f77b4', width=2)
        ),
        row=1, col=1
    )
    
    # 第2圖：K線圖 (OHLC)
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=2, col=1
    )
    
    # 新增移動平均線
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA5'],
            mode='lines',
            name='SMA(5)',
            line=dict(color='orange', width=1)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA20'],
            mode='lines',
            name='SMA(20)',
            line=dict(color='blue', width=1)
        ),
        row=2, col=1
    )
    
    # 新增買賣點標記
    if len(trades_df) > 0:
        buy_trades = trades_df[trades_df['交易動作'] == '買進']
        sell_trades = trades_df[trades_df['交易動作'] == '賣出']
        
        # 買進點 (綠色三角)
        if len(buy_trades) > 0:
            buy_prices = []
            for trade_date in buy_trades['時間']:
                # 轉換日期格式以匹配df索引
                try:
                    if isinstance(trade_date, pd.Timestamp):
                        idx = trade_date
                    else:
                        idx = pd.Timestamp(trade_date)
                    
                    # 尋找最接近的日期
                    if idx in df.index:
                        buy_prices.append(df.loc[idx, 'Low'] * 0.98)
                    else:
                        buy_prices.append(None)
                except:
                    buy_prices.append(None)
            
            fig.add_trace(
                go.Scatter(
                    x=buy_trades['時間'],
                    y=buy_prices,
                    mode='markers',
                    name='Buy',
                    marker=dict(symbol='triangle-up', size=12, color='green')
                ),
                row=2, col=1
            )
        
        # 賣出點 (紅色三角)
        if len(sell_trades) > 0:
            sell_prices = []
            for trade_date in sell_trades['時間']:
                # 轉換日期格式以匹配df索引
                try:
                    if isinstance(trade_date, pd.Timestamp):
                        idx = trade_date
                    else:
                        idx = pd.Timestamp(trade_date)
                    
                    # 尋找最接近的日期
                    if idx in df.index:
                        sell_prices.append(df.loc[idx, 'High'] * 1.02)
                    else:
                        sell_prices.append(None)
                except:
                    sell_prices.append(None)
            
            fig.add_trace(
                go.Scatter(
                    x=sell_trades['時間'],
                    y=sell_prices,
                    mode='markers',
                    name='Sell',
                    marker=dict(symbol='triangle-down', size=12, color='red')
                ),
                row=2, col=1
            )
    
    # 第3圖：成交量
    # 設定顏色：收盤價 >= 開盤價 為綠色，否則為紅色
    colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df.iterrows()]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker=dict(color=colors)
        ),
        row=3, col=1
    )
    
    # 更新布局
    fig.update_layout(
        title_text=f"Backtrader - MA5/MA20 黃金交叉策略回測<br>初始資金: ${start_value:,.0f} | 最終資金: ${final_value:,.0f}",
        height=1000,
        hovermode='x unified',
        template='plotly_white',
        # 1. 關閉所有預設可能產生的滑桿 (尤其是 Candlestick 自帶的)
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        xaxis3_rangeslider_visible=False,
        # 2. 強制在第3個 X 軸 (xaxis3) 下方開啟滑桿
        xaxis3=dict(
            rangeslider=dict(
                visible=True,
                thickness=0.05  # 控制滑桿厚度，避免壓到下方的 Volume 圖
            ),
            anchor="y3",        # 確保它錨定在第二個子圖的 Y 軸下方
            type="date"
        )
    )
    # 3. 確保所有圖表跟隨 xaxis2 的縮放
    fig.update_xaxes(matches='x')

    fig.update_yaxes(title_text='Equity ($)', range=[equity_curve.min(), equity_curve.max()], row=1, col=1)
    fig.update_yaxes(title_text='Price ($)', row=2, col=1)
    fig.update_yaxes(title_text='Volume', row=3, col=1)
    
    return fig

