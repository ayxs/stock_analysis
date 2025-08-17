# Stock Analysis

This project provides a Streamlit-based application to track groups of selected Chinese A-shares using data from [AKShare](https://akshare.akfamily.xyz/).

## Features
- Manage multiple stock groups with selection date and symbols.
- Calculate metrics from the selection date using 前复权 closing prices:
  - Current yield
  - Maximum yield and days to reach it
  - Number of days with ≥10% and ≥20% yield
  - Maximum drawdown

## Usage
1. Install dependencies:
   ```bash
   pip install streamlit akshare pandas
   # or use the requirements file
   pip install -r requirements.txt
   ```
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. Use the sidebar to create groups and view the analysis tables.

Stock symbols should include exchange prefixes (e.g. `sh600000`, `sz000001`). If the prefix is omitted, the app will infer it (`6` → `sh`, otherwise `sz`).
