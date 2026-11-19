import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Amazon Product Insights",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f4f6fb; }
section[data-testid="stSidebar"] { background: #101b32; }
section[data-testid="stSidebar"] * { color: #eef3ff !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: 8px 10px; border-radius: 9px; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
.hero {
  background: linear-gradient(115deg,#101b32 0%,#1c3157 62%,#263f6d 100%);
  padding: 28px 32px; border-radius: 20px; color: white; margin-bottom: 22px;
  box-shadow: 0 12px 30px rgba(16,27,50,.13);
}
.hero h1 { color: white; font-size: 2.05rem; margin: 0 0 7px 0; font-weight: 800; }
.hero p { color: #d4def2; margin: 0; font-size: 1rem; }
.eyebrow { color: #ffb547; font-weight: 800; letter-spacing: .12em; font-size: .72rem; text-transform: uppercase; }
.metric-card {
  background: white; border: 1px solid #e8ecf4; border-radius: 15px;
  padding: 17px 19px; box-shadow: 0 5px 16px rgba(23,38,67,.045);
}
.metric-label { color: #69758c; font-size: .82rem; font-weight: 600; }
.metric-value { color: #14213b; font-size: 1.65rem; font-weight: 800; margin-top: 5px; }
.metric-note { color: #8792a7; font-size: .75rem; margin-top: 2px; }
.section-title { color: #172541; font-size: 1.15rem; font-weight: 800; margin: 12px 0 12px 0; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.stButton>button, .stDownloadButton>button { border-radius: 10px; font-weight: 700; }
a { color: #e28a16 !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    path = Path(__file__).parent / "amazon.csv"
    data = pd.read_csv(path)
    data["rating_num"] = pd.to_numeric(data["rating"], errors="coerce")
    for source, target in [("actual_price", "actual_price_num"),
                           ("discounted_price", "discounted_price_num")]:
        data[target] = pd.to_numeric(
            data[source].astype(str).str.replace(r"[^0-9.]", "", regex=True),
            errors="coerce"
        )
    data["discount_pct_num"] = pd.to_numeric(
        data["discount_percentage"].astype(str).str.replace("%", "", regex=False),
        errors="coerce"
    )
    data["rating_count_num"] = pd.to_numeric(
        data["rating_count"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )
    data["main_category"] = data["category"].fillna("Uncategorised").str.split("|").str[0]
    data["category_label"] = data["category"].fillna("Uncategorised").str.replace("|", "  ›  ", regex=False)
    return data

df = load_data()
if df.empty:
    st.error("The dataset is empty. Please check amazon.csv.")
    st.stop()

def money(value):
    return "₹{:,.0f}".format(value) if pd.notna(value) else "—"

def metric(label, value, note=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True
    )

with st.sidebar:
    st.markdown("## 🛍️ Amazon Insights")
    st.caption("PRODUCT DATA ANALYTICS")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Explore Products", "Category Insights", "Rating Analysis", "About Project"],
        label_visibility="visible"
    )
    st.markdown("---")
    st.caption("Dataset: amazon.csv")
    st.caption(f"{len(df):,} product records")

if page == "Overview":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">Amazon · Data Analytics Dashboard</div>
      <h1>Discover the story behind the products.</h1>
      <p>Explore pricing, discounts, customer ratings and product categories in one place.</p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: metric("PRODUCTS", f"{len(df):,}", "Rows in the supplied dataset")
    with c2: metric("CATEGORIES", f"{df['main_category'].nunique():,}", "Top-level product groups")
    with c3: metric("AVERAGE RATING", f"{df['rating_num'].mean():.2f} ★", "Across available ratings")
    with c4: metric("AVERAGE DISCOUNT", f"{df['discount_pct_num'].mean():.1f}%", "Across available discounts")

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="section-title">Top product categories</div>', unsafe_allow_html=True)
        counts = df["main_category"].value_counts().head(10).rename_axis("Category").reset_index(name="Products")
        fig = px.bar(counts.sort_values("Products"), x="Products", y="Category", orientation="h",
                     color="Products", color_continuous_scale=["#f8c879","#e58a17"])
        fig.update_layout(height=390, margin=dict(l=5,r=10,t=10,b=5), coloraxis_showscale=False,
                          paper_bgcolor="white", plot_bgcolor="white", font_color="#263550")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('<div class="section-title">Customer rating distribution</div>', unsafe_allow_html=True)
        rating_data = df["rating_num"].dropna()
        fig = px.histogram(rating_data, x=rating_data, nbins=20,
                           labels={"x":"Rating", "count":"Products"},
                           color_discrete_sequence=["#315b96"])
        fig.update_layout(height=390, margin=dict(l=5,r=10,t=10,b=5),
                          paper_bgcolor="white", plot_bgcolor="white", font_color="#263550")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Highest-rated products</div>', unsafe_allow_html=True)
    top = df.dropna(subset=["rating_num"]).sort_values(["rating_num","rating_count_num"], ascending=False).head(8)
    st.dataframe(top[["product_name","main_category","discounted_price","actual_price","rating_num"]],
                 use_container_width=True, hide_index=True,
                 column_config={"product_name":"Product","main_category":"Category","rating_num":st.column_config.NumberColumn("Rating",format="%.1f ★")})

elif page == "Explore Products":
    st.markdown('<div class="hero"><div class="eyebrow">Product catalogue</div><h1>Explore Amazon products</h1><p>Search the dataset and narrow products by category, rating and discount.</p></div>', unsafe_allow_html=True)
    f1,f2,f3 = st.columns([1.5,1,1])
    with f1: query = st.text_input("Search product name", placeholder="Try: cable, laptop, headphones...")
    with f2:
        cats = ["All"] + sorted(df["main_category"].dropna().unique().tolist())
        category = st.selectbox("Category", cats)
    with f3: min_rating = st.selectbox("Minimum rating", [0,3,3.5,4,4.5], index=0)
    f4,f5 = st.columns(2)
    with f4: min_discount = st.slider("Minimum discount (%)", 0, 95, 0)
    with f5:
        sort_by = st.selectbox("Sort products by", ["Popularity (rating count)","Highest rating","Highest discount","Lowest price","Highest price"])
    filtered = df.copy()
    if query.strip():
        filtered = filtered[filtered["product_name"].str.contains(query.strip(), case=False, na=False)]
    if category != "All": filtered = filtered[filtered["main_category"] == category]
    filtered = filtered[filtered["rating_num"].fillna(0) >= min_rating]
    filtered = filtered[filtered["discount_pct_num"].fillna(0) >= min_discount]
    sort_map = {
        "Popularity (rating count)":("rating_count_num",False),
        "Highest rating":("rating_num",False),
        "Highest discount":("discount_pct_num",False),
        "Lowest price":("discounted_price_num",True),
        "Highest price":("discounted_price_num",False)
    }
    col, asc = sort_map[sort_by]
    filtered = filtered.sort_values(col, ascending=asc, na_position="last")
    st.caption(f"Showing **{len(filtered):,}** matching products")
    display = filtered[["product_name","main_category","discounted_price","actual_price","discount_percentage","rating_num","rating_count","product_link"]].copy()
    display.columns = ["Product","Category","Deal price","Actual price","Discount","Rating","Rating count","Product link"]
    st.dataframe(display, use_container_width=True, hide_index=True, height=540,
                 column_config={"Product link":st.column_config.LinkColumn("Amazon link", display_text="View product"),
                                "Rating":st.column_config.NumberColumn("Rating",format="%.1f ★")})
    st.download_button("⬇️ Download filtered products (CSV)", filtered.to_csv(index=False).encode("utf-8"),
                       file_name="amazon_filtered_products.csv", mime="text/csv")

elif page == "Category Insights":
    st.markdown('<div class="hero"><div class="eyebrow">Category intelligence</div><h1>Understand product categories</h1><p>Compare product volume, average ratings and pricing across categories.</p></div>', unsafe_allow_html=True)
    summary = df.groupby("main_category", dropna=False).agg(
        Products=("product_id","count"),
        Avg_Rating=("rating_num","mean"),
        Avg_Discount=("discount_pct_num","mean"),
        Avg_Deal_Price=("discounted_price_num","mean")
    ).reset_index().sort_values("Products", ascending=False)
    selected = st.selectbox("Choose a category to inspect", summary["main_category"].tolist())
    row = summary[summary["main_category"] == selected].iloc[0]
    a,b,c,d = st.columns(4)
    with a: metric("PRODUCTS", f"{int(row.Products):,}")
    with b: metric("AVERAGE RATING", f"{row.Avg_Rating:.2f} ★" if pd.notna(row.Avg_Rating) else "—")
    with c: metric("AVERAGE DISCOUNT", f"{row.Avg_Discount:.1f}%" if pd.notna(row.Avg_Discount) else "—")
    with d: metric("AVERAGE DEAL PRICE", money(row.Avg_Deal_Price))
    st.markdown('<div class="section-title">Category comparison</div>', unsafe_allow_html=True)
    fig = px.bar(summary.head(15).sort_values("Products"), x="Products", y="main_category", orientation="h",
                 color="Avg_Rating", color_continuous_scale="Blues",
                 labels={"main_category":"Category","Products":"Products","Avg_Rating":"Avg. rating"})
    fig.update_layout(height=480, paper_bgcolor="white", plot_bgcolor="white", margin=dict(l=5,r=10,t=10,b=5))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(summary.rename(columns={"main_category":"Category","Avg_Rating":"Average rating","Avg_Discount":"Average discount (%)","Avg_Deal_Price":"Average deal price"}),
                 use_container_width=True, hide_index=True)

elif page == "Rating Analysis":
    st.markdown('<div class="hero"><div class="eyebrow">Customer feedback</div><h1>Ratings & value analysis</h1><p>See how customer ratings and product prices are distributed in this dataset.</p></div>', unsafe_allow_html=True)
    valid = df.dropna(subset=["rating_num","discounted_price_num","actual_price_num"]).copy()
    x,y = st.columns(2)
    with x:
        st.markdown('<div class="section-title">Rating distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(df.dropna(subset=["rating_num"]), x="rating_num", nbins=18,
                           color_discrete_sequence=["#315b96"])
        fig.update_layout(paper_bgcolor="white",plot_bgcolor="white",height=360)
        st.plotly_chart(fig,use_container_width=True)
    with y:
        st.markdown('<div class="section-title">Actual price vs rating</div>', unsafe_allow_html=True)
        fig = px.scatter(valid, x="actual_price_num", y="rating_num",
                         color="discount_pct_num", hover_name="product_name",
                         labels={"actual_price_num":"Actual price (₹)","rating_num":"Rating","discount_pct_num":"Discount (%)"},
                         color_continuous_scale="Sunset")
        fig.update_layout(paper_bgcolor="white",plot_bgcolor="white",height=360)
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section-title">Rating and discount relationship</div>', unsafe_allow_html=True)
    corr_data = df[["rating_num","discount_pct_num","actual_price_num","discounted_price_num"]].corr(numeric_only=True)
    fig = px.imshow(corr_data, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
    fig.update_layout(height=390, paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Correlation describes association in this dataset; it does not establish cause and effect.")

else:
    st.markdown('<div class="hero"><div class="eyebrow">Project information</div><h1>Amazon Product Data Analysis</h1><p>A Streamlit dashboard built from the Amazon product dataset supplied with this project.</p></div>', unsafe_allow_html=True)
    st.markdown("### Project objectives")
    st.write("- Explore product categories and product listings.")
    st.write("- Compare actual prices, discounted prices and discount percentages.")
    st.write("- Study customer ratings and rating counts.")
    st.write("- Filter products and export the filtered dataset.")
    st.markdown("### Dataset details")
    st.write(f"- **Records:** {len(df):,}")
    st.write(f"- **Columns:** {len(df.columns) - 5} original dataset fields plus calculated analysis fields.")
    st.write("- **Source file:** `amazon.csv`")
    st.markdown("### Technologies")
    st.write("Python · Streamlit · Pandas · Plotly")
    st.info("This is an exploratory data-analysis dashboard. It does not connect to Amazon's live store, place orders or process payments.")
    st.markdown("### How to run")
    st.code("pip install -r requirements.txt\nstreamlit run app.py", language="bash")

st.markdown("---")
st.caption("Amazon Product Insights · Academic data analysis project")
