import pandas as pd
import streamlit as st

# Set Konfigurasi Halaman Web
st.set_page_config(page_title="Pencarian Data Peserta", layout="wide")

st.title("🔍 Sistem Cek Data Peserta Ringkas")


# Fungsi untuk menyesuaikan nama kolom secara otomatis dari Excel
def standardize_columns(df):
    column_mapping = {}
    for col in df.columns:
        col_clean = str(col).strip().lower()
        if "nama" in col_clean:
            column_mapping[col] = "Nama"
        elif "sekolah" in col_clean or "asal" in col_clean:
            column_mapping[col] = "Asal Sekolah"
        elif "bidang" in col_clean:
            column_mapping[col] = "Bidang"
        elif "peserta" in col_clean or "nomor" in col_clean or "no" in col_clean:
            column_mapping[col] = "Nomor Peserta"
        elif "ruang" in col_clean or "room" in col_clean:
            column_mapping[col] = "Ruang"

    return df.rename(columns=column_mapping)


# Load & Gabungkan Data dari 3 File Excel
@st.cache_data
def load_all_data():
    try:
        # Load masing-masing file Excel
        df_sd = pd.read_excel("DATA SSO SD 2026.xlsx")
        df_smp = pd.read_excel("DATA SSO SMP 2026.xlsx")
        df_sma = pd.read_excel("DATA SSO SMA 2026.xlsx")

        # Otomatis deteksi & seragamkan nama kolom
        df_sd = standardize_columns(df_sd)
        df_smp = standardize_columns(df_smp)
        df_sma = standardize_columns(df_sma)

        # Tambahkan kolom penanda Jenjang Sekolah
        df_sd["Jenjang Sekolah"] = "SD/MI"
        df_smp["Jenjang Sekolah"] = "SMP/MTS"
        df_sma["Jenjang Sekolah"] = "SMK/SMA/MA"

        # Menggabungkan ketiga dataframe
        df_combined = pd.concat([df_sd, df_smp, df_sma], ignore_index=True)

        # Membersihkan spasi berlebih pada isi data
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
        pilihan_jenjang = [
            "-- Semua Jenjang --",
            "SD/MI",
            "SMP/MTS",
            "SMK/SMA/MA",
        ]
        selected_jenjang = st.selectbox(
            "Jenjang / Tingkat Sekolah:", pilihan_jenjang
        )

    with col2:
        input_nama = st.text_input("Nama:")

    with col3:
        if "Bidang" in df.columns:
            daftar_bidang = ["-- Semua Bidang --"] + sorted(
                [
                    b
                    for b in df["Bidang"].dropna().unique().tolist()
                    if b not in ["nan", "None"]
                ]
            )
        else:
            daftar_bidang = ["-- Semua Bidang --"]
        selected_bidang = st.selectbox("Bidang:", daftar_bidang)

    # --- PROSES FILTER DATA ---
    filtered_df = df.copy()

    # Filter berdasarkan Jenjang Sekolah
    if selected_jenjang != "-- Semua Jenjang --":
        filtered_df = filtered_df[
            filtered_df["Jenjang Sekolah"] == selected_jenjang
        ]

    # Filter berdasarkan Nama
    if input_nama and "Nama" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["Nama"].str.contains(input_nama, case=False, na=False)
        ]

    # Filter berdasarkan Bidang
    if selected_bidang != "-- Semua Bidang --" and "Bidang" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Bidang"] == selected_bidang]

    # --- TAMPILKAN HASIL ---
    st.divider()
    st.subheader("Hasil Pencarian")

    # Kolom utama yang wajib tampil
    target_columns = ["Nama", "Asal Sekolah", "Bidang", "Nomor Peserta", "Ruang"]
    available_columns = [
        col for col in target_columns if col in filtered_df.columns
    ]

    if not filtered_df.empty:
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            hide_index=True,
        )
        st.success(f"Ditemukan **{len(filtered_df)}** data.")
    else:
        st.warning("Data tidak ditemukan. Silakan menyesuaikan kata kunci pencarian.")
