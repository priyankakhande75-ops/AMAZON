# Amazon Product Insights — Streamlit App

A Streamlit dashboard built using the supplied Amazon product dataset.

## Features
- Overview dashboard with dataset KPIs and charts
- Search and filter products by name, category, rating and discount
- Category-level comparisons
- Rating, price and discount analysis
- Export filtered products to CSV
- Product links from the original dataset

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Extract this ZIP file.
2. Create a new GitHub repository and upload `app.py`, `amazon.csv`, `requirements.txt`, and `README.md`.
3. Open https://share.streamlit.io/ and sign in.
4. Choose **Create app**, select your repository and branch.
5. Set the main file path to `app.py`, then deploy.

Keep `amazon.csv` in the same folder as `app.py`.

## Dataset
The app uses the supplied `amazon.csv` file (1,465 product records). It is an academic analysis dashboard, not a live Amazon shopping or payment application.
