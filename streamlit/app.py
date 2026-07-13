import os

import pandas as pd
import psycopg
import streamlit as st


st.set_page_config(
    page_title="Fraud Detection Report",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data(ttl=60)
def load_transactions() -> pd.DataFrame:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("La variable DATABASE_URL n'est pas définie.")

    query = """
        SELECT
            trans_num,
            amt,
            category,
            gender,
            state,
            zip,
            city_pop,
            fraud_probability,
            threshold,
            is_fraud,
            notified,
            prediction_time
        FROM transactions
        ORDER BY prediction_time DESC
    """

    with psycopg.connect(database_url) as connection:
        return pd.read_sql(query, connection)


def format_percent(value: float) -> str:
    return f"{value:.1%}"


def filter_transactions(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtres")

    fraud_filter = st.sidebar.selectbox(
        "Type de transaction",
        ["Toutes", "Fraudes", "Non frauduleuses"],
    )

    categories = sorted(data["category"].dropna().unique())
    selected_categories = st.sidebar.multiselect(
        "Catégories",
        categories,
        default=categories,
    )

    states = sorted(data["state"].dropna().unique())
    selected_states = st.sidebar.multiselect(
        "États",
        states,
        default=states,
    )

    min_amount = float(data["amt"].min()) if not data.empty else 0.0
    max_amount = float(data["amt"].max()) if not data.empty else 0.0
    if min_amount == max_amount:
        st.sidebar.caption(f"Montant unique : {min_amount:.2f}")
        amount_range = (min_amount, max_amount)
    else:
        amount_range = st.sidebar.slider(
            "Montant",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount),
        )

    filtered = data.copy()

    if fraud_filter == "Fraudes":
        filtered = filtered[filtered["is_fraud"] == 1]
    elif fraud_filter == "Non frauduleuses":
        filtered = filtered[filtered["is_fraud"] == 0]

    filtered = filtered[filtered["category"].isin(selected_categories)]
    filtered = filtered[filtered["state"].isin(selected_states)]
    filtered = filtered[
        filtered["amt"].between(amount_range[0], amount_range[1], inclusive="both")
    ]

    return filtered


def show_kpis(data: pd.DataFrame) -> None:
    total_transactions = len(data)
    total_frauds = int(data["is_fraud"].sum()) if total_transactions else 0
    fraud_rate = total_frauds / total_transactions if total_transactions else 0
    total_amount = data["amt"].sum() if total_transactions else 0
    avg_probability = data["fraud_probability"].mean() if total_transactions else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Transactions", f"{total_transactions:,}".replace(",", " "))
    col2.metric("Fraudes", f"{total_frauds:,}".replace(",", " "))
    col3.metric("Taux de fraude", format_percent(fraud_rate))
    col4.metric("Montant total", f"{total_amount:,.2f}".replace(",", " "))
    col5.metric("Probabilité moyenne", format_percent(avg_probability))


def show_charts(data: pd.DataFrame) -> None:
    left, right = st.columns(2)

    with left:
        st.subheader("Transactions par jour")
        daily = (
            data.assign(day=data["prediction_time"].dt.date)
            .groupby("day")
            .agg(transactions=("trans_num", "count"), fraudes=("is_fraud", "sum"))
            .sort_index()
        )
        st.line_chart(daily)

    with right:
        st.subheader("Répartition fraude / non fraude")
        fraud_breakdown = (
            data.assign(type=data["is_fraud"].map({0: "Non fraude", 1: "Fraude"}))
            .groupby("type")
            .size()
            .rename("transactions")
        )
        st.bar_chart(fraud_breakdown)

    left, right = st.columns(2)

    with left:
        st.subheader("Top catégories")
        category_summary = (
            data.groupby("category")
            .agg(transactions=("trans_num", "count"), fraudes=("is_fraud", "sum"))
            .sort_values("transactions", ascending=False)
            .head(10)
        )
        st.bar_chart(category_summary)

    with right:
        st.subheader("Top États")
        state_summary = (
            data.groupby("state")
            .agg(transactions=("trans_num", "count"), fraudes=("is_fraud", "sum"))
            .sort_values("transactions", ascending=False)
            .head(10)
        )
        st.bar_chart(state_summary)


def show_tables(data: pd.DataFrame) -> None:
    st.subheader("Transactions les plus risquées")
    risky_columns = [
        "trans_num",
        "amt",
        "category",
        "state",
        "fraud_probability",
        "threshold",
        "is_fraud",
        "prediction_time",
    ]
    st.dataframe(
        data.sort_values("fraud_probability", ascending=False)[risky_columns].head(20),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Toutes les transactions filtrées")
    st.dataframe(data, use_container_width=True, hide_index=True)

    csv = data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger le rapport CSV",
        data=csv,
        file_name="fraud_detection_report.csv",
        mime="text/csv",
    )


st.title("Rapport Fraud Detection")
st.caption("Suivi des transactions, des scores de fraude et des alertes enregistrées.")

if st.button("Rafraîchir les données"):
    st.cache_data.clear()

try:
    transactions = load_transactions()
except Exception as error:
    st.error("Impossible de charger les transactions depuis PostgreSQL.")
    st.info(
        "Vérifie que Docker est lancé, que la table `transactions` existe et que "
        "`DATABASE_URL` pointe vers la bonne base."
    )
    st.exception(error)
    st.stop()

if transactions.empty:
    st.warning("Aucune transaction trouvée dans la table `transactions`.")
    st.stop()

transactions["prediction_time"] = pd.to_datetime(transactions["prediction_time"])

filtered_transactions = filter_transactions(transactions)

if filtered_transactions.empty:
    st.warning("Aucune transaction ne correspond aux filtres sélectionnés.")
    st.stop()

show_kpis(filtered_transactions)
st.divider()
show_charts(filtered_transactions)
st.divider()
show_tables(filtered_transactions)
