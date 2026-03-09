import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

st.title("📊 Nifty Macro Dashboard")

# --------------------------------
# Download Data
# --------------------------------

nifty = yf.download("^NSEI", start="2010-01-01")
crude = yf.download("BZ=F", start="2010-01-01")
usd = yf.download("INR=X", start="2010-01-01")
vix = yf.download("^INDIAVIX", start="2010-01-01")
sp500 = yf.download("^GSPC", start="2010-01-01")

nifty = nifty[['Close']]
crude = crude[['Close']]
usd = usd[['Close']]
vix = vix[['Close']]
sp500 = sp500[['Close']]

nifty.columns=["Nifty"]
crude.columns=["Crude"]
usd.columns=["USDINR"]
vix.columns=["VIX"]
sp500.columns=["SP500"]

df = pd.merge(nifty, crude, left_index=True, right_index=True)
df = pd.merge(df, usd, left_index=True, right_index=True)
df = pd.merge(df, vix, left_index=True, right_index=True)
df = pd.merge(df, sp500, left_index=True, right_index=True)

# ==========================================
# MACRO EVENT TIMELINE
# ==========================================

macro_events = {
"COVID Crash": "2020-03-15",
"Oil Crash": "2020-04-20",
"Ukraine War": "2022-02-24",
"Inflation Shock": "2022-06-10",
"SVB Banking Crisis": "2023-03-10"
}

st.subheader("Market Snapshot")

latest = df.iloc[-1]

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("Nifty", round(latest["Nifty"],2))
col2.metric("Crude", round(latest["Crude"],2))
col3.metric("USDINR", round(latest["USDINR"],2))
col4.metric("VIX", round(latest["VIX"],2))
col5.metric("S&P500", round(latest["SP500"],2))

# --------------------------------
# Returns
# --------------------------------

df["Nifty_Return"] = df["Nifty"].pct_change()
df["Crude_Return"] = df["Crude"].pct_change()
df["USDINR_Return"] = df["USDINR"].pct_change()
df["VIX_Return"] = df["VIX"].pct_change()
df["SP500_Return"] = df["SP500"].pct_change()

df = df.dropna()
df = df[~df.index.isna()]

# --------------------------------
# Sidebar Filters
# --------------------------------

st.sidebar.header("Controls")

start_date = st.sidebar.date_input(
    "Start Date",
    value=df.index.min().date()
)

df = df[df.index >= pd.to_datetime(start_date)]

# --------------------------------
# Correlation Heatmap
# --------------------------------

st.subheader("Macro Correlation Heatmap")

corr = df[[
"Nifty_Return",
"Crude_Return",
"USDINR_Return",
"VIX_Return",
"SP500_Return"
]].corr()

fig = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="RdBu_r"
)

st.plotly_chart(fig)

# --------------------------------
# Rolling Correlation
# --------------------------------

st.subheader("Rolling Correlation: Nifty vs Crude")

df["Rolling_Corr"] = df["Nifty_Return"].rolling(30).corr(df["Crude_Return"])

fig = px.line(
    df,
    y="Rolling_Corr"
)

st.plotly_chart(fig)

# --------------------------------
# Rolling Beta
# --------------------------------

st.subheader("Rolling Beta (Nifty sensitivity to oil)")

window = 60

df["Rolling_Beta"] = (
df["Nifty_Return"].rolling(window).cov(df["Crude_Return"]) /
df["Crude_Return"].rolling(window).var()
)

fig = px.line(
    df,
    y="Rolling_Beta"
)

st.plotly_chart(fig)

# --------------------------------
# Macro Risk Index
# --------------------------------

st.subheader("Global Macro Risk Index")

macro = df.copy()

macro["Crude_Z"]=(macro["Crude_Return"]-macro["Crude_Return"].rolling(60).mean())/macro["Crude_Return"].rolling(60).std()
macro["VIX_Z"]=(macro["VIX_Return"]-macro["VIX_Return"].rolling(60).mean())/macro["VIX_Return"].rolling(60).std()
macro["USD_Z"]=(macro["USDINR_Return"]-macro["USDINR_Return"].rolling(60).mean())/macro["USDINR_Return"].rolling(60).std()
macro["SP_Z"]=(macro["SP500_Return"]-macro["SP500_Return"].rolling(60).mean())/macro["SP500_Return"].rolling(60).std()

macro["Macro_Risk"]=macro["Crude_Z"]+macro["VIX_Z"]+macro["USD_Z"]-macro["SP_Z"]
current_risk = macro["Macro_Risk"].iloc[-1]

if current_risk > 2:
    regime = "🔴 Risk Off"
elif current_risk < -2:
    regime = "🟢 Risk On"
else:
    regime = "🟡 Neutral"
st.subheader("Market Stress Gauge")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=current_risk,
    title={'text': "Macro Risk Level"},
    gauge={
        'axis': {'range': [-5, 5]},
        'bar': {'color': "black"},
        'steps': [
            {'range': [-5, -2], 'color': "green"},
            {'range': [-2, 2], 'color': "yellow"},
            {'range': [2, 5], 'color': "red"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': current_risk
        }
    }
))

st.plotly_chart(fig)
st.subheader("Market Regime")

st.metric(
    "Current Macro Risk Index",
    round(current_risk,2)
)

st.write("Market Regime:", regime)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=macro.index,
        y=macro["Macro_Risk"],
        name="Macro Risk"
    )
)

st.plotly_chart(fig)


# --------------------------------
# Nifty vs Macro Risk
# --------------------------------

st.subheader("Nifty with Macro Shock Timeline")

fig = go.Figure()

fig.add_trace(
go.Scatter(
x=macro.index,
y=macro["Nifty"],
name="Nifty",
line=dict(color="blue")
)
)

# Add macro event markers
for event, date in macro_events.items():

    fig.add_vline(
        x=date,
        line_dash="dash",
        line_color="red"
    )

    fig.add_annotation(
        x=date,
        y=macro["Nifty"].max(),
        text=event,
        showarrow=True,
        arrowhead=1
    )

st.plotly_chart(fig)

# --------------------------------
# ML Model
# --------------------------------

st.subheader("ML Market Signal")

# Create target
df["Target"] = (df["Nifty_Return"].shift(-1) > 0).astype(int)

# Drop NaNs
df_ml = df.dropna()

features = df_ml[[
"Crude_Return",
"USDINR_Return",
"VIX_Return",
"SP500_Return",
"Nifty_Return"
]]

target = df_ml["Target"]

X_train, X_test, y_train, y_test = train_test_split(
features,
target,
test_size=0.2,
shuffle=False
)

model = RandomForestClassifier(
n_estimators=200,
max_depth=5,
random_state=42
)

model.fit(X_train, y_train)

# Accuracy (still useful)
pred = model.predict(X_test)

acc = accuracy_score(y_test, pred)

st.metric(
"Model Accuracy",
f"{round(acc*100,2)}%"
)

# --------------------------------
# Probability Signal
# --------------------------------

proba = model.predict_proba(X_test)[-1]

up_prob = round(proba[1]*100,2)
down_prob = round(proba[0]*100,2)

st.subheader("Tomorrow's Market Probability")

col1,col2 = st.columns(2)

col1.metric(
"Nifty Up Probability",
f"{up_prob}%"
)

col2.metric(
"Nifty Down Probability",
f"{down_prob}%"
)

# Feature importance chart
importance = pd.Series(
model.feature_importances_,
index=features.columns
)

fig = px.bar(
importance,
title="Feature Importance"
)

st.plotly_chart(fig)