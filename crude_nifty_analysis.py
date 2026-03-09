# ==========================================
# GLOBAL MACRO ANALYSIS PROJECT
# NIFTY vs CRUDE + USDINR + VIX + S&P500
# ==========================================

# pip install yfinance pandas matplotlib seaborn scikit-learn

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ==========================================
# 1 DOWNLOAD DATA
# ==========================================

nifty = yf.download("^NSEI", start="2010-01-01")
crude = yf.download("BZ=F", start="2010-01-01")
usd_inr = yf.download("INR=X", start="2010-01-01")
vix = yf.download("^INDIAVIX", start="2010-01-01")
sp500 = yf.download("^GSPC", start="2010-01-01")

# ==========================================
# 2 CLEAN DATA
# ==========================================

nifty = nifty[['Close']]
crude = crude[['Close']]
usd_inr = usd_inr[['Close']]
vix = vix[['Close']]
sp500 = sp500[['Close']]

nifty.columns = ["Nifty"]
crude.columns = ["Crude"]
usd_inr.columns = ["USDINR"]
vix.columns = ["VIX"]
sp500.columns = ["SP500"]

# ==========================================
# 3 MERGE DATA
# ==========================================

df = pd.merge(nifty, crude, left_index=True, right_index=True)
df = pd.merge(df, usd_inr, left_index=True, right_index=True)
df = pd.merge(df, vix, left_index=True, right_index=True)
df = pd.merge(df, sp500, left_index=True, right_index=True)

# ==========================================
# 4 RETURNS
# ==========================================

df["Nifty_Return"] = df["Nifty"].pct_change()
df["Crude_Return"] = df["Crude"].pct_change()
df["USDINR_Return"] = df["USDINR"].pct_change()
df["VIX_Return"] = df["VIX"].pct_change()
df["SP500_Return"] = df["SP500"].pct_change()

df["Next_Day_Return"] = df["Nifty_Return"].shift(-1)

df["Target"] = (df["Next_Day_Return"] > 0).astype(int)

df = df.dropna()

# ==========================================
# 5 CORRELATION MATRIX
# ==========================================

corr = df[
[
"Nifty_Return",
"Crude_Return",
"USDINR_Return",
"VIX_Return",
"SP500_Return"
]
].corr()

print("\nCorrelation Matrix\n")
print(corr)

plt.figure(figsize=(8,6))

sns.heatmap(
corr,
annot=True,
cmap="coolwarm",
center=0
)

plt.title("Macro Variable Correlation Matrix")
plt.show()

# ==========================================
# 6 ROLLING CORRELATION
# ==========================================

df["Rolling_Corr"] = df["Nifty_Return"].rolling(30).corr(df["Crude_Return"])

plt.figure(figsize=(10,6))

df["Rolling_Corr"].plot()

plt.title("30 Day Rolling Correlation: Nifty vs Crude")

plt.show()

# ==========================================
# 7 ROLLING BETA
# ==========================================

window = 60

df["Rolling_Beta"] = (
df["Nifty_Return"].rolling(window).cov(df["Crude_Return"])
/
df["Crude_Return"].rolling(window).var()
)

plt.figure(figsize=(10,6))

df["Rolling_Beta"].plot()

plt.axhline(0,color="black")

plt.title("Rolling Beta: Nifty Sensitivity to Crude")

plt.show()

# ==========================================
# 8 OIL PRICE REGIMES
# ==========================================

df["Crude_Regime"] = pd.cut(
df["Crude"],
bins=[0,80,100,110,120,200],
labels=[
"Low Oil (<80)",
"Moderate (80-100)",
"High (100-110)",
"Very High (110-120)",
"Extreme (>120)"
]
)

print("\nAverage Nifty Return by Oil Regime\n")

print(df.groupby("Crude_Regime")["Nifty_Return"].mean())

# ==========================================
# 9 MACRO STRESS INDICATOR
# ==========================================

df["Macro_Stress"] = (
(df["Crude_Return"] > 0.01) &
(df["USDINR_Return"] > 0) &
(df["VIX_Return"] > 0)
)

print("\nNext Day Nifty Return During Macro Stress\n")

print(df.groupby("Macro_Stress")["Next_Day_Return"].mean())

# ==========================================
# 10 MACHINE LEARNING MODEL
# ==========================================

features = df[
[
"Crude_Return",
"USDINR_Return",
"VIX_Return",
"SP500_Return",
"Nifty_Return"
]
]

target = df["Target"]

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

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", accuracy)

importance = pd.Series(
model.feature_importances_,
index=features.columns
)

importance.sort_values().plot(
kind="barh",
title="Feature Importance"
)

plt.show()

# ==========================================
# 11 EVENT STUDY : OIL SHOCKS
# ==========================================

df["Nifty_1D"] = df["Nifty"].shift(-1)/df["Nifty"] - 1
df["Nifty_3D"] = df["Nifty"].shift(-3)/df["Nifty"] - 1
df["Nifty_5D"] = df["Nifty"].shift(-5)/df["Nifty"] - 1

shock_levels = [0.03,0.05,0.08,0.10,0.20]

results = []

for level in shock_levels:

    shock_name = f"Shock_{int(level*100)}"

    df[shock_name] = abs(df["Crude_Return"]) > level

    events = df[df[shock_name]]

    results.append({

        "Shock_Level":f">{int(level*100)}%",
        "Events":len(events),
        "1D_Return":events["Nifty_1D"].mean(),
        "3D_Return":events["Nifty_3D"].mean(),
        "5D_Return":events["Nifty_5D"].mean()

    })

event_results = pd.DataFrame(results)

print("\nOil Shock Event Study\n")

print(event_results)

plt.figure(figsize=(10,6))

plt.plot(
event_results["Shock_Level"],
event_results["1D_Return"],
marker="o",
label="1D Return"
)

plt.plot(
event_results["Shock_Level"],
event_results["3D_Return"],
marker="o",
label="3D Return"
)

plt.plot(
event_results["Shock_Level"],
event_results["5D_Return"],
marker="o",
label="5D Return"
)

plt.title("Nifty Reaction After Oil Shocks")

plt.legend()

plt.grid(True)

plt.show()

# ==========================================
# 12 GLOBAL MACRO RISK INDEX
# ==========================================

macro_df = df.copy()

macro_df["Crude_Z"] = (
macro_df["Crude_Return"] -
macro_df["Crude_Return"].rolling(60).mean()
) / macro_df["Crude_Return"].rolling(60).std()

macro_df["VIX_Z"] = (
macro_df["VIX_Return"] -
macro_df["VIX_Return"].rolling(60).mean()
) / macro_df["VIX_Return"].rolling(60).std()

macro_df["USD_Z"] = (
macro_df["USDINR_Return"] -
macro_df["USDINR_Return"].rolling(60).mean()
) / macro_df["USDINR_Return"].rolling(60).std()

macro_df["SP_Z"] = (
macro_df["SP500_Return"] -
macro_df["SP500_Return"].rolling(60).mean()
) / macro_df["SP500_Return"].rolling(60).std()

macro_df["Macro_Risk_Index"] = (
macro_df["Crude_Z"] +
macro_df["VIX_Z"] +
macro_df["USD_Z"] -
macro_df["SP_Z"]
)

plt.figure(figsize=(12,6))

macro_df["Macro_Risk_Index"].plot(label="Macro Risk Index")

plt.axhline(0,color="black")

plt.title("Global Macro Risk Dashboard")

plt.legend()

plt.show()

# ==========================================
# 13 NIFTY vs MACRO RISK
# ==========================================

fig, ax1 = plt.subplots(figsize=(12,6))

ax1.plot(macro_df.index, macro_df["Nifty"], label="Nifty")

ax2 = ax1.twinx()

ax2.plot(
macro_df.index,
macro_df["Macro_Risk_Index"],
linestyle="--",
label="Macro Risk Index"
)

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.title("Nifty vs Macro Risk Index")

plt.show()

# ==========================================
# 14 RISK OFF PERIODS
# ==========================================

plt.figure(figsize=(12,6))

plt.plot(
macro_df.index,
macro_df["Nifty"],
label="Nifty",
linewidth=2
)

risk_threshold = (
macro_df["Macro_Risk_Index"].mean()
+
macro_df["Macro_Risk_Index"].std()
)

risk_periods = macro_df["Macro_Risk_Index"] > risk_threshold

plt.fill_between(
macro_df.index,
macro_df["Nifty"].min(),
macro_df["Nifty"].max(),
where=risk_periods,
color="red",
alpha=0.15,
label="Risk Off Period"
)

plt.title("Nifty with Global Risk-Off Periods")

plt.legend()

plt.show()