# Crude Oil Impact on Nifty 50
### A Macro Market Analysis Dashboard

## Overview

This project analyzes the relationship between **crude oil prices and the Indian equity market (Nifty 50)** using historical data and quantitative analysis.

Crude oil is a key macroeconomic variable for India because the country imports a large portion of its energy needs. Changes in oil prices can influence inflation, currency stability, corporate costs, and overall market sentiment.

The goal of this project is to **quantitatively explore whether and how crude oil price movements affect the Nifty 50 index**.

An interactive **Streamlit dashboard** was built to visualize and analyze these relationships.

---

##Live Dashboard
https://macro-risk-dashboard-53dkwz987sd2dcijfxkbze.streamlit.app/

## Research Questions

This project explores the following questions:

- Does crude oil have a strong correlation with Nifty returns?
- How does the crude–Nifty relationship change over time?
- Does Nifty behave differently when oil prices are high?
- How does the market react to large oil price shocks?
- How important is crude compared to other macro drivers like VIX or global markets?

---

## Data Sources

The analysis uses daily market data from **Yahoo Finance**.

Assets included:

- Nifty 50 Index
- Brent Crude Oil
- USD/INR Exchange Rate
- India VIX
- S&P 500 Index

Time period analyzed:

2010 – Present

---

## Methodology

Several quantitative techniques were used to analyze the relationship between crude oil and Nifty.

### 1. Correlation Analysis
A correlation heatmap compares the relationship between Nifty returns and macro variables including crude oil, volatility, currency, and global markets.

### 2. Rolling Correlation
A **30-day rolling correlation** was calculated to study how the relationship between crude oil and Nifty changes across time and market regimes.

### 3. Rolling Beta
Rolling beta measures the **sensitivity of Nifty returns to crude oil movements**, helping identify periods when oil had stronger market influence.

### 4. Oil Price Regime Analysis
Oil prices were categorized into regimes:

- Low Oil (<80)
- Moderate (80–100)
- High (100–110)
- Very High (110–120)
- Extreme (>120)

Nifty returns and volatility were analyzed across these regimes.

### 5. Oil Shock Event Study
Large oil price shocks were studied to observe Nifty's reaction.

Shock thresholds examined:

- >3%
- >5%
- >8%
- >10%
- >20%

Average Nifty returns were measured after **1-day, 3-day, and 5-day horizons**.

---

## Key Findings

Some key insights from the analysis:

- **Crude oil has a weak direct correlation with daily Nifty returns.**
- The crude–Nifty relationship **changes significantly across time**, indicating regime dependence.
- Extremely high oil prices (>120) are associated with **negative Nifty returns and higher volatility**.
- Market volatility (**VIX**) shows a much stronger relationship with Nifty than crude oil.
- Global markets (**S&P 500**) also influence Nifty movements.

Overall, the results suggest that **oil price movements affect market conditions indirectly through macroeconomic channels rather than acting as a dominant short-term driver of Nifty returns**.

---

## Dashboard

An interactive **Streamlit dashboard** was built to explore the analysis visually.

The dashboard includes:

- Nifty vs Crude price comparison
- Correlation heatmap
- Rolling correlation analysis
- Rolling beta (Nifty sensitivity to oil)
- Oil shock event study
- Oil price regime analysis

Users can interactively explore how crude oil movements relate to the Indian equity market.

---

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Plotly
- Streamlit
- yfinance

---

## Running the Dashboard

Clone the repository and install dependencies:

```
pip install -r requirements.txt
```

Run the Streamlit dashboard:

```
python -m streamlit run macro_dashboard.py
```

---

## Project Structure

```
.
├── macro_dashboard.py
├── crude_nifty_analysis.py
└── README.md
```

---

## Author

**Kunal Singh**

Computer Science student interested in **financial markets, data analysis, and quantitative research**.
