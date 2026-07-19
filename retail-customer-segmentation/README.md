# Retail Customer Segmentation & Recommendation System

An end-to-end customer analytics project using K-Means clustering to group retail customers by age, annual income, and spending score. The Streamlit dashboard provides interactive exploration, segment summaries, campaign recommendations, and customer lookup.

## Repository contents

- `notebooks/` — the original business understanding, analysis, preprocessing, segmentation, model comparison, recommendation, and dashboard notebooks.
- `app.py` — the deployable Streamlit application.
- `requirements.txt` — Python packages required by Streamlit Community Cloud.
- `.streamlit/config.toml` — application theme and server configuration.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The application accepts any of the following through the sidebar uploader:

- `Customer_Segments.csv` or `Final_Customers.csv` produced by the notebooks;
- the original Mall Customers CSV. In this case, the app creates five K-Means clusters automatically.

To bundle a default dashboard dataset, add `Customer_Segments.csv` or `Final_Customers.csv` to `data/`. The CSV is intentionally ignored by Git so that customer data is not published accidentally. Remove the `data/*.csv` rule only if the dataset is public and you are permitted to share it.

## Publish to GitHub

1. Create an empty GitHub repository, for example `retail-customer-segmentation`.
2. Open a terminal in this project folder and run:

   ```bash
   git init
   git add .
   git commit -m "Initial Streamlit customer segmentation app"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/retail-customer-segmentation.git
   git push -u origin main
   ```

3. Confirm that `app.py`, `requirements.txt`, and `.streamlit/config.toml` are present in the GitHub repository.

## Deploy on Streamlit Community Cloud

GitHub stores the code; the live Streamlit application is deployed from that GitHub repository.

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Choose **Create app** and select your repository and the `main` branch.
3. Set the main file path to `app.py`, then choose **Deploy**.
4. If you did not commit a public sample CSV, upload your CSV in the deployed app’s sidebar.

Every push to `main` will redeploy the app automatically.
