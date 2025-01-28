import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Fungsi untuk memuat data
@st.cache_data
def load_data(filepath):
    data = pd.read_csv(filepath, parse_dates=[
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ])
    return data

# Memuat dataset
data_path = "orders_dataset.csv"  # Ganti dengan path dataset Anda
data = load_data(data_path)

# Judul Dashboard
st.title("Dashboard Analisis Data Pesanan")
st.markdown("### Analisis Distribusi dan Performa Pesanan")

# Sidebar untuk navigasi
menu = st.sidebar.selectbox("Pilih Analisis", ["Distribusi Status Pesanan", "Tren Pemesanan Bulanan", "Performa Waktu Pengiriman"])

if menu == "Distribusi Status Pesanan":
    st.header("Distribusi Status Pesanan")

    # Hitung distribusi status dan hilangkan "created" serta "approved"
    status_counts = data['order_status'].value_counts()
    status_counts = status_counts.drop(index=["created", "approved"], errors="ignore")  # Menghapus status tertentu

    # Membuat label untuk legenda dengan persentase
    labels_with_percentage = [
        f"{label}: {count} ({count / status_counts.sum() * 100:.1f}%)"
        for label, count in zip(status_counts.index, status_counts.values)
    ]

    # Membuat pie chart tanpa label persentase di dalam chart
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(
        status_counts,
        labels=None,  # Tidak menampilkan label di dalam pie
        startangle=140,
        colors=sns.color_palette("Set2"),
        wedgeprops={'edgecolor': 'black'}
    )

    # Menambahkan legenda di kiri bawah dengan angka persentase
    ax.legend(
        labels=labels_with_percentage,
        loc="lower left",  # Lokasi legenda di kiri bawah
        fontsize=12,
        title="Status Pesanan"
    )

    ax.set_title("Distribusi Status Pesanan", fontsize=16)
    ax.set_aspect('equal')  # Memastikan pie chart berbentuk lingkaran
    plt.tight_layout()  # Menyesuaikan layout agar tidak terpotong

    # Menampilkan visualisasi di Streamlit
    st.pyplot(fig)




elif menu == "Tren Pemesanan Bulanan":
    st.header("Tren Pemesanan Bulanan")
    
    # Tambahkan kolom untuk bulan
    data['order_month'] = data['order_purchase_timestamp'].dt.to_period('M')
    monthly_orders = data.groupby('order_month').size()
    
    # Visualisasi Line Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=monthly_orders.index.astype(str), y=monthly_orders.values, marker='o', ax=ax, color='green')
    ax.set_title("Tren Pemesanan Bulanan", fontsize=16)
    ax.set_xlabel("Bulan", fontsize=12)
    ax.set_ylabel("Jumlah Pesanan", fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

elif menu == "Performa Waktu Pengiriman":
    st.header("Performa Waktu Pengiriman")
    
    # Hitung selisih waktu pengiriman
    data['delivery_difference'] = (data['order_estimated_delivery_date'] - data['order_delivered_customer_date']).dt.days
    
    # Visualisasi Histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data['delivery_difference'].dropna(), bins=30, kde=True, ax=ax, color='blue')
    ax.set_title("Distribusi Selisih Waktu Pengiriman", fontsize=16)
    ax.set_xlabel("Hari Selisih (Tepat Waktu vs Keterlambatan)", fontsize=12)
    ax.set_ylabel("Jumlah Pesanan", fontsize=12)
    st.pyplot(fig)

st.markdown("Dashboard ini dirancang untuk menjawab pertanyaan bisnis terkait distribusi status pesanan, tren pemesanan bulanan, dan performa waktu pengiriman.")
