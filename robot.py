import streamlit as st
import fal_client
import os
import random

# --- CONFIGURARE SECURIZATĂ (Cloud + Local) ---
# Încercăm să luăm cheia din secretele Streamlit (Cloud)
# Dacă nu le găsim (Local), folosim varianta de rezervă (else)
try:
    os.environ["FAL_KEY"] = st.secrets["FAL_KEY"]
except Exception:
    # Aici pui cheia ta reală DOAR pentru a testa pe calculatorul tău.
    # Când urci pe GitHub, poți lăsa cheia aici SAU o poți șterge pentru siguranță.
    os.environ["FAL_KEY"] = ""

st.set_page_config(page_title="AI Master Studio Online", page_icon="💎", layout="wide")

# Inițializăm starea
if 'last_image_url' not in st.session_state: st.session_state.last_image_url = None
if 'enhanced_prompt' not in st.session_state: st.session_state.enhanced_prompt = ""
if 'seed' not in st.session_state: st.session_state.seed = random.randint(1, 999999)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control")
    if st.button("🔄 Seed Nou"):
        st.session_state.seed = random.randint(1, 999999)
        st.rerun()
    st.session_state.seed = st.number_input("Seed", value=st.session_state.seed)
    strength = st.slider("Puterea Modificării", 0.1, 1.0, 0.70, 0.05)

st.title("💎 AI Master Studio Online")

# PASUL 0: PROMPT ENHANCER
user_idea = st.text_input("Ideea ta (română/engleză):", placeholder="Ex: Van Gogh style")
if st.button("Îmbunătățește Prompt-ul ✨"):
    if user_idea:
        with st.spinner("AI-ul lucrează la prompt..."):
            try:
                res = fal_client.subscribe("fal-ai/any-llm", arguments={
                    "model": "meta-llama/llama-3.1-70b-instruct", 
                    "prompt": f"Detailed English prompt for: '{user_idea}'. Preserve facial identity. Return ONLY the prompt."
                })
                st.session_state.enhanced_prompt = res["output"]
            except Exception as e: st.error(f"Eroare asistent: {e}")

final_prompt = st.text_area("Prompt Final:", value=st.session_state.enhanced_prompt)

# PASUL 1: FOTO
uploaded_file = st.file_uploader("Încarcă poza:", type=["jpg", "png", "jpeg"])
if st.button("Generează Imaginea 🎨", type="primary"):
    if uploaded_file and final_prompt:
        with st.spinner("Se pictează imaginea..."):
            try:
                # --- SOLUȚIA PENTRU EROAREA ASCII ---
                # Salvăm imaginea într-un fișier temporar pe server
                temp_filename = "temp_cloud_fix.jpg"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Trimitem calea fișierului, nu datele brute
                img_url = fal_client.upload_file(temp_filename)
                
                handler = fal_client.submit("fal-ai/flux/dev/image-to-image", arguments={
                    "image_url": img_url, 
                    "prompt": final_prompt, 
                    "strength": strength, 
                    "seed": st.session_state.seed
                })
                
                st.session_state.last_image_url = handler.get()['images'][0]['url']
                
                # Ștergem fișierul temporar după ce am terminat
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
            except Exception as e: 
                st.error(f"Eroare Imagine: {e}")
    else:
        st.warning("⚠️ Încarcă o poză și scrie un prompt!")

if st.session_state.last_image_url:
    st.image(st.session_state.last_image_url, use_container_width=True)
    
    # PASUL 2: VIDEO
    if st.button("🚀 Transformă în Video"):
        with st.spinner("Kling AI generează video-ul..."):
            try:
                res_video = fal_client.subscribe("fal-ai/kling-video/v1/standard/image-to-video", arguments={
                    "image_url": st.session_state.last_image_url, 
                    "prompt": "Cinematic fluid motion"
                })
                st.video(res_video['video']['url'])
            except Exception as e: 
                st.error(f"Eroare Video: {e}")