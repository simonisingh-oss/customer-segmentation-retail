"""Streamlit deployment app for the Retail Customer Segmentation project."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans


st.set_page_config(
    page_title="Retail Customer Segmentation",
    page_icon="🛍️",
    layout="wide",
)

SEGMENT_NAMES = {
    0: "VIP Customers",
    1: "Potential Customers",
    2: "Regular Customers",
    3: "Young Shoppers",
    4: "Budget Customers",
}
RECOMMENDATIONS = {
    "VIP Customers": "Offer premium membership, exclusive rewards, and early access to new collections.",
    "Potential Customers": "Provide personalized product recommendations and loyalty offers to increase spending.",
    "Regular Customers": "Encourage repeat purchases through reward points and bundle discounts.",
    "Young Shoppers": "Promote trending products, seasonal collections, and student offers.",
    "Budget Customers": "Provide discount coupons, cashback offers, and festival sales.",
}
FEATURES = ["Age", "Annual Income (k$)", "Spending Score (1-100)"]


def add_segments(data: pd.DataFrame) -> pd.DataFrame:
    """Create clusters for raw customer data, then attach readable recommendations."""
    data = data.copy()
    missing = [column for column in FEATURES if column not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    if "Cluster" not in data.columns:
        if len(data) < 5:
            raise ValueError("At least 5 customer records are needed to create five segments.")
        model = KMeans(n_clusters=5, random_state=42, n_init=10)
        data["Cluster"] = model.fit_predict(data[FEATURES])

    data["Cluster"] = pd.to_numeric(data["Cluster"], errors="raise").astype(int)
    data["Segment"] = data["Cluster"].map(SEGMENT_NAMES).fillna("Unclassified")
    data["Recommendation"] = data["Segment"].map(RECOMMENDATIONS).fillna(
        "Review this customer segment before assigning a campaign."
    )
    return data


@st.cache_data(show_spinner=False)
def load_data(uploaded_file) -> pd.DataFrame:
    return add_segments(pd.read_csv(uploaded_file))


def local_data_path() -> Path | None:
    for filename in ("data/Customer_Segments.csv", "data/Final_Customers.csv"):
        candidate = Path(filename)
        if candidate.exists():
            return candidate
    return None


def get_data() -> pd.DataFrame | None:
    uploaded_file = st.sidebar.file_uploader("Upload customer data (CSV)", type="csv")
    source = uploaded_file or local_data_path()
    if source is None:
        st.info(
            "Upload `Customer_Segments.csv`, `Final_Customers.csv`, or the original Mall Customers CSV to begin. "
            "The app will create five segments when a Cluster column is not supplied."
        )
        return None
    try:
        return load_data(source)
    except (ValueError, pd.errors.ParserError) as error:
        st.error(f"Could not prepare the data: {error}")
        return None


def dashboard(data: pd.DataFrame) -> None:
    st.header("Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Customers", len(data))
    c2.metric("Clusters", data["Cluster"].nunique())
    c3.metric("Average income", f"${data['Annual Income (k$)'].mean():.1f}k")
    c4.metric("Average spending score", f"{data['Spending Score (1-100)'].mean():.1f}")

    left, right = st.columns(2)
    left.plotly_chart(
        px.scatter(
            data, x="Annual Income (k$)", y="Spending Score (1-100)", color="Segment",
            hover_data=[column for column in ["Age", "Gender"] if column in data.columns],
            title="Income vs. spending score",
        ),
        use_container_width=True,
    )
    right.plotly_chart(
        px.histogram(data, x="Segment", color="Segment", title="Customers by segment"),
        use_container_width=True,
    )


def segment_view(data: pd.DataFrame) -> None:
    st.header("Customer Segments")
    summary = data.groupby("Segment", dropna=False).agg(
        Customers=("Cluster", "size"),
        Average_Age=("Age", "mean"),
        Average_Income=("Annual Income (k$)", "mean"),
        Average_Spending=("Spending Score (1-100)", "mean"),
    ).round(2).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.plotly_chart(
        px.scatter(data, x="Age", y="Spending Score (1-100)", size="Annual Income (k$)",
                   color="Segment", title="Customer profiles by segment"),
        use_container_width=True,
    )


def recommendation_view(data: pd.DataFrame) -> None:
    st.header("Recommendations")
    for segment, recommendation in RECOMMENDATIONS.items():
        count = int((data["Segment"] == segment).sum())
        with st.expander(f"{segment} ({count} customers)", expanded=count > 0):
            st.write(recommendation)


def customer_search(data: pd.DataFrame) -> None:
    st.header("Customer Search")
    identifier = "CustomerID" if "CustomerID" in data.columns else None
    if identifier:
        selected = st.selectbox("Customer ID", data[identifier].tolist())
        result = data.loc[data[identifier] == selected]
    else:
        row = st.number_input("Row number", min_value=0, max_value=len(data) - 1, value=0, step=1)
        result = data.iloc[[row]]
    st.dataframe(result, use_container_width=True, hide_index=True)


st.title("🛍️ Retail Customer Segmentation & Recommendation System")
st.caption("Machine-learning customer segmentation for targeted retail campaigns.")

page = st.sidebar.radio("Navigation", ["Dashboard", "Dataset", "Customer Segments", "Recommendations", "Customer Search", "About"])
data = get_data()

if page == "About":
    st.header("About")
    st.write("This project uses K-Means clustering to group retail customers by age, annual income, and spending score.")
    st.write("Run the notebooks in order to reproduce the analysis and export the data used by this dashboard.")
elif data is not None:
    if page == "Dashboard":
        dashboard(data)
    elif page == "Dataset":
        st.header("Dataset")
        st.dataframe(data, use_container_width=True, hide_index=True)
        st.subheader("Statistics")
        st.dataframe(data.describe(include="all").T, use_container_width=True)
    elif page == "Customer Segments":
        segment_view(data)
    elif page == "Recommendations":
        recommendation_view(data)
    elif page == "Customer Search":
        customer_search(data)
