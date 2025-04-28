import streamlit as st
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Akıllı Patates Sınıflandırma Sistemi", page_icon="🥔")

# --- Giriş ekranı kontrolü ---
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    # Giriş Ekranı
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>Akıllı Patates Sınıflandırma Sistemi 🥔</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Çürük ve Taze Patateslerin Gerçek Zamanlı Ayrımı</h3>", unsafe_allow_html=True)
    st.markdown("---")

    # Kullanıcı adı ve şifre doğrulama
    kullanici_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap"):
        if kullanici_adi == "codecappadocia" and sifre == "12345":
            st.session_state.giris_yapildi = True
            st.session_state.kullanici_adi = kullanici_adi
            st.success("Giriş başarılı!")
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")

else:
    # --- Sidebar Menü ---
    st.sidebar.title("Menü")
    menu_secimi = st.sidebar.radio(
        "Gitmek istediğiniz bölümü seçin:",
        ("Ana Sayfa", "Canlı İzleme", "İstatistikler")
    )

    # --- Ortak Data ---
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=["Saatler", "Toplam Ayıklanan", "Çürük Patates", "Sağlam Patates"])

    # --- Disardan Veri Okuma Fonksiyonu ---
    def disardan_veri_oku():
        try:
            with open("veri.txt", "r") as dosya:
                satirlar = dosya.readlines()

                if not satirlar:
                    st.warning("Veri dosyası boş!")
                    return

                for satir in satirlar:
                    veri = satir.strip().split(',')
                    if len(veri) == 3:
                        saat, toplam_ayiklanan, curuk_patates = veri
                        saglam_patates = int(toplam_ayiklanan) - int(curuk_patates)
                        yeni_veri = pd.DataFrame([{
                            "Saatler": saat,
                            "Toplam Ayıklanan": int(toplam_ayiklanan),
                            "Çürük Patates": int(curuk_patates),
                            "Sağlam Patates": saglam_patates
                        }])
                        st.session_state.df = pd.concat([st.session_state.df, yeni_veri], ignore_index=True)

                st.success(f"{len(satirlar)} adet veri başarıyla yüklendi!")

        except FileNotFoundError:
            st.error("veri.txt dosyası bulunamadı!")

    # --- Ana Sayfa ---
    if menu_secimi == "Ana Sayfa":
        st.subheader("Ana Sayfa")

        kullanici_adi = st.session_state.get("kullanici_adi", "kullanıcı")
        st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>Hoş geldin, {kullanici_adi} 👋</h1>", unsafe_allow_html=True)
        st.markdown("---")

        if st.button("Geri Dön"):
            st.session_state.giris_yapildi = False
            st.rerun()

        st.write(""" Bu sistem, patates bant hattı üzerindeki ürünlerin takibini yapmanızı sağlar.
        - Çürük ve sağlam patateslerin saatlik takibini yapabilirsiniz.
        - İstatistiklere ve grafiklere ulaşabilirsiniz.
        """)

        st.subheader("Veri Yükle")
        uploaded_file = st.file_uploader("Bir CSV veya Excel Dosyası Yükleyin", type=["csv", "xlsx"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                st.session_state.df = pd.read_excel(uploaded_file)
            st.success("Veri başarıyla yüklendi!")

        if not st.session_state.df.empty:
            st.subheader("Veriyi İndir")
            st.download_button(
                label="Veriyi CSV Olarak İndir",
                data=st.session_state.df.to_csv(index=False),
                file_name="patates_ayiklama.csv",
                mime="text/csv"
            )

    # --- Canlı İzleme ---
    elif menu_secimi == "Canlı İzleme":
        st.subheader("Canlı İzleme")

        saatler = ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']

        with st.form(key='patates_form'):
            st.subheader("Yeni Veri Girişi")
            saat = st.selectbox("Saat Seçin", saatler)
            toplam_ayiklanan = st.number_input("Toplam Ayıklanan Patates", min_value=0)
            curuk_patates = st.number_input("Çürük Patates", min_value=0)

            veri_kaydet = st.form_submit_button("Verileri Kaydet")

        if veri_kaydet:
            saglam_patates = toplam_ayiklanan - curuk_patates
            yeni_veri = pd.DataFrame([{
                "Saat": saat,
                "Toplam Ayıklanan": toplam_ayiklanan,
                "Çürük Patates": curuk_patates,
                "Sağlam Patates": saglam_patates
            }])
            st.session_state.df = pd.concat([st.session_state.df, yeni_veri], ignore_index=True)
            st.success(f"{saat} için veriler kaydedildi!")

        if st.button("Yeni Verileri Oku"):
            disardan_veri_oku()

        if not st.session_state.df.empty:
            st.subheader("Anlık Görüntü")
            st.dataframe(st.session_state.df)

    # --- İstatistikler ---
    elif menu_secimi == "İstatistikler":
        st.subheader("İstatistikler")

        if st.session_state.df.empty:
            st.warning("Henüz kayıtlı veri bulunmuyor!")
        else:
            st.subheader("Saatlik Ayıklanan Patatesler Grafiği")
            st.line_chart(st.session_state.df.set_index("Saatler")[["Toplam Ayıklanan", "Çürük Patates", "Sağlam Patates"]])

            st.subheader("Detaylı Saatlik Rapor")
            st.dataframe(st.session_state.df)

            st.subheader("Toplam İstatistikler 📊")
            st.metric(label="Toplam Ayıklanan Patates", value=st.session_state.df["Toplam Ayıklanan"].sum())
            st.metric(label="Toplam Çürük Patates", value=st.session_state.df["Çürük Patates"].sum())
            st.metric(label="Toplam Sağlam Patates", value=st.session_state.df["Sağlam Patates"].sum())

            st.subheader("Çürük Patates Oranı")
            toplam_ayiklanan = st.session_state.df["Toplam Ayıklanan"].sum()
            toplam_curuk = st.session_state.df["Çürük Patates"].sum()

            if toplam_ayiklanan > 0:
                oran = toplam_curuk / toplam_ayiklanan
                st.write(f"Çürük Patateslerin Oranı: {oran:.2%}")
            else:
                st.write("Yeterli veri bulunmuyor.")

            if toplam_curuk > 100:
                st.warning("⚠ Çürük patates sayısı yüksek! Kontrol edilmesi gerek!!")