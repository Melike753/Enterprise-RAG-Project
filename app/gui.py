import streamlit as st
import requests

# Sayfa Ayarları
st.set_page_config(
    page_title="Y İnovasyon AI | Kurumsal Asistan",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Yan Menü Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Mesaj Balonları */
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #30363D;
    }
    
    /* Sidebar Başlığı */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #58A6FF;
        margin-bottom: 20px;
        text-align: center;
    }

    div[data-testid="stChatInput"] {
        max-width: 60%; 
        margin-left: auto;
        margin-right: auto;
        left: 0;
        right: 0;
        bottom: 30px;
    }

    .main .block-container {
        padding-bottom: 120px;
    }
    </style>
    """, unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:8000"

# --- SIDEBAR (Sol Panel) ---
with st.sidebar:
    st.markdown('<p class="sidebar-header">⚡Y İnovasyon AI</p>', unsafe_allow_html=True)
    
    with st.container():
        st.info("🤖 **Model:** Gemma 2 9B\n\n⚙️ **Engine:** RAG Enabled")
        
    st.divider()
    st.subheader("🛠️ Yönetim Paneli")
    
    if st.button("🔍 Sistem Check-up"):
        try:
            health = requests.get(f"{BASE_URL}/health").json()
            st.success(f"Sistem Aktif\n\n{health['message']}")
        except:
            st.error("Servis Bağlantısı Kesildi!")

    if st.button("🔄 Veritabanını Tazele"):
        with st.status("Veriler senkronize ediliyor...", expanded=False) as status:
            res = requests.get(f"{BASE_URL}/index").json()
            status.update(label="İşlem Tamamlandı!", state="complete", expanded=False)
            st.toast(res["message"])

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("🚀 Y İnovasyon ve Teknoloji A.Ş.")

# --- ANA EKRAN ---
col_left, col_main, col_right = st.columns([1, 2.5, 1])

with col_main:
    # Başlık ve Tanıtım
    st.title("🤖 Kurumsal RAG Asistanı")
    st.markdown("""
        Merhaba! Ben Y İnovasyon asistanıyım. Şirket politikaları, çalışma düzeni ve kültürümüz hakkında 
        bana her şeyi sorabilirsin.
        """)

    # Sohbet geçmişi
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mesajların Akışı
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- KULLANICI GİRİŞİ ---
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Asistan Yanıt Tetikleyici
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]
    
    with col_main:
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyorum..."):
                try:
                    # Zaman aşımı süresi 120 saniyeye çıkarıldı (timeout=120)
                    response = requests.get(f"{BASE_URL}/ask", params={"query": last_query}, timeout=120).json()
                    answer = response.get("response", "Hata oluştu.")
                    
                    if "metadata" in response:
                        proc_time = response["metadata"]["processing_time_sec"]
                        full_response = f"{answer}\n\n--- \n *⏱️ Analiz Süresi: {proc_time} sn*"
                    else:
                        full_response = answer

                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun()
                except Exception as e:
                    st.error("Bağlantı Hatası! Sunucu çok yoğun olabilir, lütfen biraz bekleyip tekrar deneyin.")
                    