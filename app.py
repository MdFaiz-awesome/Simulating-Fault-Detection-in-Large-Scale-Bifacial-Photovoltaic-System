import streamlit as st
import time

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Addition Dashboard",
    page_icon="➕",
    layout="wide"
)

# =========================
# CSS (ANIMATIONS + UI STYLE)
# =========================
st.markdown("""
    <style>

        /* Fade-in animation */
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(10px);}
            to {opacity: 1; transform: translateY(0);}
        }

        /* Slide-in animation */
        @keyframes slideIn {
            from {opacity: 0; transform: translateX(-20px);}
            to {opacity: 1; transform: translateX(0);}
        }

        .main-title {
            font-size: 40px;
            font-weight: 700;
            color: #1A5276;
            text-align: center;
            margin-bottom: 10px;
            animation: fadeIn 1s ease-in-out;
        }
        .section-title {
            font-size: 22px;
            font-weight: 600;
            color: #154360;
            margin-top: 20px;
            animation: fadeIn 1.2s ease-in-out;
        }
        .result-box {
            background-color: #E8F6F3;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #D1F2EB;
            text-align: center;
            font-size: 26px;
            color: #0B5345;
            font-weight: bold;
            margin-top: 10px;
            animation: slideIn 0.8s ease-out;
        }
        .history-box {
            background-color: #FEF9E7;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #F9E79F;
            font-size: 16px;
            color: #7D6608;
            margin-top: 10px;
            animation: fadeIn 0.6s ease;
        }

        /* Hover animation */
        .history-box:hover {
            background-color: #FCF3CF;
            transform: scale(1.02);
            transition: 0.2s;
        }

        /* Icon styling */
        .icon-big {
            font-size: 60px;
            text-align: center;
            animation: fadeIn 1s ease;
        }

    </style>
""", unsafe_allow_html=True)


# =========================
# SIDEBAR NAVIGATION
# =========================
st.sidebar.title("📊 Dashboard Navigation")
menu = st.sidebar.radio(
    "Menu",
    ["Calculator", "History Log", "About Project"]
)


# =========================
# SESSION STATE (HISTORY)
# =========================
if "history" not in st.session_state:
    st.session_state.history = []


# =========================
# MAIN CONTENT
# =========================

if menu == "Calculator":

    st.markdown('<p class="icon-big">➕</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title">Addition Calculator Dashboard</p>', unsafe_allow_html=True)
    st.markdown("### Masukkan dua nombor untuk membuat kiraan tambah")

    col1, col2 = st.columns(2)

    with col1:
        num1 = st.number_input("🔢 Nombor Pertama", value=0.0)

    with col2:
        num2 = st.number_input("🔢 Nombor Kedua", value=0.0)

    # Button
    if st.button("🚀 Calculate"):

        # LOADING SPINNER ANIMATION
        with st.spinner("Sedang mengira... ⏳"):
            time.sleep(1.5)  # simulate processing delay
            result = num1 + num2

        # CONFETTI CELEBRATION
        st.balloons()

        # Result Box
        st.markdown(f"""
            <div class="result-box">
                📘 Hasil Tambah:<br><br> {result}
            </div>
        """, unsafe_allow_html=True)

        # Save into history
        st.session_state.history.append(f"{num1} + {num2} = {result}")


elif menu == "History Log":

    st.markdown('<p class="icon-big">📝</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title">Calculation History Log</p>', unsafe_allow_html=True)

    if len(st.session_state.history) == 0:
        st.info("Belum ada rekod kiraan.")
    else:
        for record in st.session_state.history:
            st.markdown(f"""
                <div class="history-box">
                    📌 {record}
                </div>
            """, unsafe_allow_html=True)


elif menu == "About Project":

    st.markdown('<p class="icon-big">📘</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title">Project Information</p>', unsafe_allow_html=True)

    st.markdown("""
        ## 🎯 Tujuan Dashboard  
        Dashboard ini dibangunkan sebagai contoh aplikasi Python berbasis Streamlit dengan UI profesional,  
        animasi, serta fungsi log yang berkualiti untuk tugasan universiti dan projek sebenar.

        ## 🎆 Ciri Terbaru  
        - ⏳ **Loading animation** semasa mengira  
        - 🎉 **Confetti celebration** selepas kiraan berjaya  
        - 💎 UI premium dengan CSS animations  

        ## 🛠 Teknologi Digunakan  
        - **Python**
        - **Streamlit**
        - **Custom CSS Animations**
        - **Session State History Tracking**

        ## 🎓 Sesuai Untuk:
        - Assignment Python  
        - Projek mini  
        - FYP prototaip UI  
        - Dashboard pembelajaran  
        - Demo profesional untuk presentation  
    """)
