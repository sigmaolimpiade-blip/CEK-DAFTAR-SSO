import pandas as pd
import streamlit as st

# Set Konfigurasi Halaman Web
st.set_page_config(page_title="Pencarian Data Peserta", layout="wide")

st.title("🔍 Sistem Cek Data Peserta Ringkas")


# Load & Gabungkan Data dari 3 File Excel
@st.cache_data
def load_all_data():
    try:
        # Nama file disesuaikan persis dengan file di GitHub
        df_sd = pd.read_excel("DATA SSO SD 2026.xlsx")
        df_smp = pd.read_excel("DATA SSO SMP 2026.xlsx")
        df_sma = pd.read_excel("DATA SSO SMA 2026.xlsx")

        # Menggabungkan ketiga dataframe
        df_combined = pd.concat([df_sd, df_smp, df_sma], ignore_index=True)

        # Membersihkan spasi berlebih pada string
        for col in df_combined.select_dtypes(include="object").columns:
            df_combined[col] = df_combined[col].astype(str).str.strip()

        return df_combined
    except Exception as e:
        st.error(
            f"Gagal membaca file Excel. Pastikan file ada di folder yang sama. Error: {e}"
        )
        return pd.DataFrame()


df = load_all_data()

if not df.empty:
    # --- FORM INPUT & FILTER ---
    st.subheader("Filter Pencarian")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Pilihan Asal Sekolah (Dropdown)
        daftar_sekolah = ["-- Semua Sekolah --"] + sorted(
            df["Asal Sekolah"].dropna().unique().tolist()
        )
        selected_sekolah = st.selectbox("Asal Sekolah:", daftar_sekolah)

    with col2:
        # Input Nama
        input_nama = st.text_input("Nama:")

    with col3:
        # Input atau Dropdown Bidang
        daftar_bidang = ["-- Semua Bidang --"] + sorted(
            df["Bidang"].dropna().unique().tolist()
        )
        selected_bidang = st.selectbox("Bidang:", daftar_bidang)

    # --- PROSES FILTER DATA ---
    filtered_df = df.copy()

    # Filter berdasarkan Asal Sekolah jika dipilih
    if selected_sekolah != "-- Semua Sekolah --":
        filtered_df = filtered_df[
            filtered_df["Asal Sekolah"] == selected_sekolah
        ]

    # Filter berdasarkan Nama (tidak peka huruf besar/kecil)
    if input_nama:
        filtered_df = filtered_df[
            filtered_df["Nama"].str.contains(input_nama, case=False, na=False)
        ]

    # Filter berdasarkan Bidang jika dipilih
    if selected_bidang != "-- Semua Bidang --":
        filtered_df = filtered_df[filtered_df["Bidang"] == selected_bidang]

    # --- TAMPILKAN HASIL ---
    st.divider()
    st.subheader("Hasil Pencarian")

    # Kolom yang ingin ditampilkan saja
    target_columns = ["Nama", "Asal Sekolah", "Bidang", "Nomor Peserta", "Ruang"]

    if not filtered_df.empty:
        # Menampilkan tabel hasil
        st.dataframe(
            filtered_df[target_columns],
            use_container_width=True,
            hide_index=True,
        )
        st.success(f"Ditemukan **{len(filtered_df)}** data.")
    else:
        st.warning("Data tidak ditemukan. Silakan menyesuaikan kata kunci pencarian.")
