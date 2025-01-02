import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


# Fungsi untuk membuat DataFrame jumlah pesanan harian
def create_daily_orders_df(df):
    # Konversi kolom order_purchase_timestamp menjadi datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Resample data berdasarkan hari dan hitung jumlah pesanan serta total pendapatan
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "delivery_time": "sum"  # Anda bisa mengganti kolom ini dengan kolom numerik yang relevan
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "delivery_time": "revenue"  # Pastikan nama kolom sesuai konteks
    }, inplace=True)
    
    return daily_orders_df


def create_order_status_analysis_df(df):
    order_status_df = df.groupby('order_status').agg({
        'order_id': 'count'
    }).reset_index()
    order_status_df.rename(columns={'order_id': 'total_orders'}, inplace=True)
    order_status_df = order_status_df.sort_values(by='total_orders', ascending=False)
    return order_status_df

def create_monthly_orders_df(df):
    monthly_orders_df = df.groupby('purchase_month').agg({
        'order_id': 'count'
    }).reset_index()
    monthly_orders_df.rename(columns={'order_id': 'total_orders'}, inplace=True)
    monthly_orders_df = monthly_orders_df.sort_values(by='purchase_month')
    return monthly_orders_df


# Load dataset
all_df = pd.read_csv("cleaned_orders_dataset.csv")

# Pastikan kolom timestamp dikonversi ke datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Tentukan rentang tanggal minimum dan maksimum
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    # Pilih rentang tanggal menggunakan Streamlit sidebar
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter dataset berdasarkan rentang tanggal
main_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) & 
                 (all_df['order_purchase_timestamp'] <= str(end_date))]


# Buat DataFrame jumlah pesanan harian
daily_orders_df = create_daily_orders_df(main_df)

# Tampilkan dashboard
st.header('Dashboard Data Pesanan')
st.subheader('Jumlah Pesanan Harian')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df['order_count'].sum()
    st.metric("Total Pesanan", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df['revenue'].sum(), "IDR", locale='id_ID') 
    st.metric("Total Pendapatan", value=total_revenue)

# Plot data jumlah pesanan harian
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

tab1, tab2, tab3 = st.tabs(["Grafik Pesanan", "Analisis Status", "Grafik  Bulanan"])
# Tab untuk grafik pesanan
with tab1:
    st.subheader("Grafik Pesanan Harian")
    if not daily_orders_df.empty:
        st.line_chart(daily_orders_df.set_index("order_purchase_timestamp")["order_count"])
    else:
        st.write("Data pesanan tidak tersedia.")


# Filter dataset berdasarkan rentang tanggal
main_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) & 
                 (all_df['order_purchase_timestamp'] <= str(end_date))]

# Tab untuk analisis produk
with tab2:
    st.subheader("Analisis Status Pesanan")
    order_status_df = create_order_status_analysis_df(main_df)
    if not order_status_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=order_status_df, x='order_status', y='total_orders', ax=ax, palette='viridis')
        ax.set_title("Jumlah Pesanan Berdasarkan Status", fontsize=14)
        ax.set_xlabel("Status Pesanan", fontsize=12)
        ax.set_ylabel("Jumlah Pesanan", fontsize=12)
        st.pyplot(fig)
    else:
        st.write("Data status pesanan tidak tersedia.")

with tab3:
    st.subheader("Analisis Pembelian Bulanan")
    monthly_orders_df = create_monthly_orders_df(main_df)
    if not monthly_orders_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=monthly_orders_df, x='purchase_month', y='total_orders', marker='o', ax=ax, color="#00796B")
        ax.set_title("Jumlah Pesanan Berdasarkan Bulan", fontsize=14)
        ax.set_xlabel("Bulan", fontsize=12)
        ax.set_ylabel("Jumlah Pesanan", fontsize=12)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write("Data pembelian bulanan tidak tersedia.")


