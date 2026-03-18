import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="My Financial Planner 2026", layout="centered")

# --- DATABASE SESSION ---
if 'transaksi' not in st.session_state:
    st.session_state['transaksi'] = []
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- SISTEM LOGIN ---
if not st.session_state['logged_in']:
    st.title("🔐 Secure Finance Login")
    pw = st.text_input("Masukkan Password Access", type="password")
    if st.button("Masuk ke Dashboard"):
        if pw == "1234": # Silakan ganti password ini jika ingin lebih aman
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Password Salah!")
else:
    # --- DATA PROCESSING ---
    df = pd.DataFrame(st.session_state['transaksi'])
    target_100jt = 100000000
    DAFTAR_KANTONG = ["Dana Darurat", "Tabungan 100 Juta", "Investasi", "Kebutuhan Pokok"]
    
    # --- SIDEBAR: TARGET & KANTONG ---
    st.sidebar.header("🎯 Target & Alokasi")
    if not df.empty:
        total_masuk = df[df['Tipe'] == "Pemasukan"]['Nominal'].sum()
        total_keluar = df[df['Tipe'] == "Pengeluaran"]['Nominal'].sum()
        saldo_skrg = total_masuk - total_keluar
        
        st.sidebar.metric("Total Saldo", f"Rp {saldo_skrg:,.0f}")
        st.sidebar.progress(min(max(saldo_skrg/target_100jt, 0.0), 1.0))
        st.sidebar.caption(f"Progress: {(saldo_skrg/target_100jt)*100:.1f}% Ke 100 Juta")
        
        st.sidebar.divider()
        st.sidebar.subheader("📂 Isi Kantong")
        for k in DAFTAR_KANTONG:
            val = df[(df['Kategori'] == "Tabungan") & (df['Keterangan'].str.contains(k, na=False))]['Nominal'].sum()
            st.sidebar.write(f"{k}: **Rp {val:,.0f}**")
    else:
        st.sidebar.info("Belum ada data transaksi.")

    # --- DASHBOARD UTAMA ---
    st.title("💰 Smart Budgeter 2026")
    
    # Kalkulator Sedekah Otomatis (2.5% dari Pemasukan)
    if not df.empty:
        wajib_sedekah = total_masuk * 0.025
        sudah_sedekah = df[df['Kategori'] == "Sedekah/Zakat"]['Nominal'].sum()
        sisa_sedekah = max(wajib_sedekah - sudah_sedekah, 0.0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**Kewajiban Sedekah (2.5%):**\nRp {wajib_sedekah:,.0f}")
        with c2:
            warna = "inverse" if sisa_sedekah > 0 else "normal"
            st.metric("Sisa Belum Sedekah", f"Rp {sisa_sedekah:,.0f}", delta=-sisa_sedekah, delta_color=warna)

    # --- FORM INPUT TRANSAKSI ---
    st.subheader("📝 Catat Transaksi")
    with st.form("input_form", clear_on_submit=True):
        ket = st.text_input("Keterangan (misal: Gaji, Makan, Setor Dana Darurat)")
        nom = st.number_input("Nominal (Rp)", min_value=0, step=5000)
        col_a, col_b = st.columns(2)
        with col_a:
            tipe = st.selectbox("Tipe", ["Pengeluaran", "Pemasukan"])
        with col_b:
            kat = st.selectbox("Kategori", ["Gaji", "Makanan", "Bensin", "Sedekah/Zakat", "Tabungan", "Hiburan"])
        
        if st.form_submit_button("Simpan Data"):
            if ket and nom > 0:
                st.session_state['transaksi'].append({
                    "Tanggal": datetime.now().strftime("%Y-%m-%d"),
                    "Keterangan": ket, "Tipe": tipe, "Kategori": kat, "Nominal": nom
                })
                st.success("Data Berhasil Disimpan!")
                st.rerun()
            else:
                st.warning("Mohon isi keterangan dan nominal.")

    # --- VISUALISASI & LAPORAN ---
    if not df.empty:
        st.divider()
        t1, t2 = st.tabs(["📊 Statistik & Grafik", "📋 Riwayat Lengkap"])
        
        with t1:
            st.subheader("Alokasi Pengeluaran")
            df_out = df[df['Tipe'] == "Pengeluaran"]
            if not df_out.empty:
                fig, ax = plt.subplots()
                df_out.groupby('Kategori')['Nominal'].sum().plot(kind='pie', autopct='%1.1f%%', ax=ax)
                st.pyplot(fig)
            else:
                st.write("Belum ada data pengeluaran untuk ditampilkan.")

        with t2:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Laporan (.csv)", data=csv, file_name=f"Laporan_2026.csv")

    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
