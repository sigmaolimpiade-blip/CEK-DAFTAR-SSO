import os
import pandas as pd
from PIL import Image
import streamlit as st

# 1. Konfigurasi Halaman Web & Tab Browser
st.set_page_config(
    page_title="Sisingamangaraja Science Olympiad",
    page_icon="🏆",
    layout="wide",
)

# 2. Custom CSS Perbaikan Layout & Tampilan
st.markdown(
    """
    <style>
    /* Memberikan ruang atas yang pas agar banner tidak terpotong */
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Memastikan gambar banner tampil utuh */
    div[data-testid="stImage"] img {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* Judul dan Subheader Warna Merah Khas SSO */
    h2, h3 {
        color: #B71C1C !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700 !important;
    }
    
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 3. TAMPILKAN BANNER GAMBAR ---
banner_names = [
    "banner.png",
    "banner.jpg",
    "OLIMPIADE ILMU SISINGAMANGARAJA (1).png",
]
banner_loaded = False

for b_name in banner_names:
    if os.path.exists(b_name):
        try:
            image = Image.open(b_name)
            st.image(image, use_container_width=True)
            banner_loaded = True
            break
        except Exception:
            pass

if not banner_loaded:
    st.info("💡 Gambar banner sedang dimuat/nama file disesuaikan.")

st.markdown(
    "<h3 style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>🔍 SISTEM CEK DATA PESERTA</h3>",
    unsafe_allow_html=True,
)
st.divider()


# --- 4. FUNGSI STANDARISASI KOLOM ---
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


# --- 5. LOAD DATA DARI EXCEL ---
@st.cache_data
def load_all_data():
    try:
        # PENTING: dtype=str memelihara format 0001, 0002
        df_sd = pd.read_excel("DATA SSO SD 2026.xlsx", dtype=str)
        df_smp = pd.read_excel("DATA SSO SMP 2026.xlsx", dtype=str)
        df_sma = pd.read_excel("DATA SSO SMA 2026.xlsx", dtype=str)

        # Standarisasi Kolom
        df_sd = standardize_columns(df_sd)
        df_smp = standardize_columns(df_smp)
        df_sma = standardize_columns(df_sma)

        # Penanda Jenjang
        df_sd["Jenjang Sekolah"] = "SD/MI"
        df_smp["Jenjang Sekolah"] = "SMP/MTS"
        df_sma["Jenjang Sekolah"] = "SMK/SMA/MA"

        # Gabungkan Data
        df_combined = pd.concat([df_sd, df_smp, df_sma], ignore_index=True)

        # Bersihkan Spasi & Kosong
        for col in df_combined.columns:
            df_combined[col] = (
                df_combined[col].fillna("").astype(str).str.strip()
            )
            df_combined[col] = df_combined[col].replace("nan", "")

        return df_combined
    except Exception as e:
        st.error(f"Gagal membaca file data. Pastikan nama file Excel sesuai: {e}")
        return pd.DataFrame()


df = load_all_data()

if not df.empty:
    # --- 6. FORM FILTER PENCARIAN ---
    st.subheader("📋 Form Pencarian Peserta")

    col1, col2, col3 = st.columns(3)

    with col1:
        pilihan_jenjang = [
            "-- Semua Jenjang --",
            "SD/MI",
            "SMP/MTS",
            "SMK/SMA/MA",
        ]
        selected_jenjang = st.selectbox(
            "Tingkat / Jenjang Sekolah:", pilihan_jenjang
        )

    with col2:
        input_nama = st.text_input(
            "Ketik Nama Peserta:", placeholder="Contoh: Syakila..."
        )

    with col3:
        if "Bidang" in df.columns:
            daftar_bidang = ["-- Semua Bidang --"] + sorted(
                [
                    b
                    for b in df["Bidang"].unique().tolist()
                    if b and b not in ["nan", "None"]
                ]
            )
        else:
            daftar_bidang = ["-- Semua Bidang --"]
        selected_bidang = st.selectbox("Pilih Bidang Lomba:", daftar_bidang)

    # --- 7. DETEKSI STATUS PENCARIAN ---
    # Hasil HANYA akan diproses jika minimal ada 1 filter yang dipilih/diketik
    is_searching = (
        selected_jenjang != "-- Semua Jenjang --"
        or len(input_nama.strip()) > 0
        or selected_bidang != "-- Semua Bidang --"
    )

    if is_searching:
        filtered_df = df.copy()

        if selected_jenjang != "-- Semua Jenjang --":
            filtered_df = filtered_df[
                filtered_df["Jenjang Sekolah"] == selected_jenjang
            ]

        if input_nama and "Nama" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["Nama"].str.contains(
                    input_nama, case=False, na=False
                )
            ]

        if (
            selected_bidang != "-- Semua Bidang --"
            and "Bidang" in filtered_df.columns
        ):
            filtered_df = filtered_df[filtered_df["Bidang"] == selected_bidang]

        # --- 8. TAMPILAN HASIL PENCARIAN ---
        st.divider()
        st.subheader("📌 Hasil Pencarian")

        target_columns = [
            "Nama",
            "Asal Sekolah",
            "Bidang",
            "Nomor Peserta",
            "Ruang",
        ]
        available_columns = [
            col for col in target_columns if col in filtered_df.columns
        ]

        if not filtered_df.empty:
            st.dataframe(
                filtered_df[available_columns],
                use_container_width=True,
                hide_index=True,
            )
            st.success(f"🎉 Ditemukan **{len(filtered_df)}** data peserta.")
        else:
            st.warning(
                "⚠️ Data tidak ditemukan. Silakan periksa kembali kata kunci Nama, Jenjang, atau Bidang Lomba."
            )
    else:
        # Tampilan pesan bantuan saat pertama kali membuka web
        st.divider()
        st.info(
            "💡 **Petunjuk:** Silakan pilih Tingkat Sekolah, ketik Nama Peserta, atau pilih Bidang Lomba di atas untuk menampilkan data peserta."
        )
