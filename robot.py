import streamlit as st
import fal_client
import os
import random

# 1. --- CONFIGURARE CHEIE API ---
os.environ["FAL_KEY"] = "753c9dd9-4b7d-4c40-8187-9a349a2680c3:1d28147e02850019b602742d1f0d0a10"

# 2. --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="AI Master Studio 2026", page_icon="💎", layout="wide")

# Inițializăm memoria sesiunii
if 'last_image_url' not in st.session_state:
    st.session_state.last_image_url = None
if 'upscaled_image_url' not in st.session_state:
    st.session_state.upscaled_image_url = None
if 'enhanced_prompt' not in st.session_state:
    st.session_state.enhanced_prompt = ""
if 'seed' not in st.session_state:
    st.session_state.seed = random.randint(1, 999999)

# --- SIDEBAR: CENTRUL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Control Tehnic")
    if st.button("🔄 Seed Nou"):
        st.session_state.seed = random.randint(1, 999999)
        st.rerun()
    st.session_state.seed = st.number_input("Seed (Ancora)", value=st.session_state.seed)
    st.divider()
    st.header("🎨 Setări Foto")
    strength = st.slider("Puterea Modificării", 0.1, 1.0, 0.70, 0.05)
    st.caption("Sugestie: 0.70 pentru transformări artistice.")

# --- ZONA PRINCIPALĂ ---
st.title("💎 AI Master Studio: Fluxul Complet")

# PASUL 0: PROMPT ENHANCER
st.header("🪄 Pasul 0: Rafinare Idee")
user_idea = st.text_input("Ce vrei să creezi? (română/engleză):", placeholder="Ex: fă-mă un explorator pe Marte")

if st.button("Îmbunătățește Prompt-ul ✨"):
    if user_idea:
        with st.spinner("Asistentul AI optimizează descrierea..."):
            try:
                llm_prompt = f"Rewrite this idea into a detailed English prompt for Flux AI: '{user_idea}'. Include 'preserve facial features' and high-end artistic details. Return ONLY the prompt."
                res = fal_client.subscribe(
                    "fal-ai/any-llm",
                    arguments={
                        "model": "meta-llama/llama-3.1-70b-instruct", 
                        "prompt": llm_prompt
                    }
                )
                st.session_state.enhanced_prompt = res["output"]
                st.success("Prompt optimizat!")
            except Exception as e:
                st.error(f"Eroare asistent: {e}")

final_prompt = st.text_area("Prompt Final:", value=st.session_state.enhanced_prompt, height=80)

st.divider()

# PASUL 1: GENERARE FOTO
st.header("📸 Pasul 1: Transformare Foto")
col_up, col_res = st.columns(2)

with col_up:
    uploaded_file = st.file_uploader("Încarcă poza ta:", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Sursă", width=300)

with col_res:
    if st.button("Generează Imaginea Artistivă 🎨", type="primary"):
        if uploaded_file and final_prompt:
            with st.spinner("Se pictează..."):
                try:
                    temp_path = "temp_studio_final.jpg"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    img_url = fal_client.upload_file(temp_path)
                    handler = fal_client.submit(
                        "fal-ai/flux/dev/image-to-image",
                        arguments={
                            "image_url": img_url,
                            "prompt": final_prompt,
                            "strength": strength,
                            "seed": st.session_state.seed
                        },
                    )
                    result = handler.get()
                    st.session_state.last_image_url = result['images'][0]['url']
                    st.session_state.upscaled_image_url = None # Resetăm upscale-ul vechi
                    
                    if os.path.exists(temp_path): os.remove(temp_path)
                except Exception as e:
                    st.error(f"Eroare Imagine: {e}")

if st.session_state.last_image_url:
    st.image(st.session_state.last_image_url, caption="Rezultat Generat", use_container_width=True)

st.divider()

# PASUL 2: UPSCALE 4K (NOU)
st.header("💎 Pasul 2: Upscale & Claritate 4K")
if st.session_state.last_image_url:
    st.write("Mărește rezoluția și adaugă detalii ultra-realiste.")
    
    col_u1, col_u2 = st.columns([1, 2])
    with col_u1:
        creativity = st.slider("Creativitate Upscale", 0.0, 1.0, 0.35, 0.05, help="Mai mult înseamnă că AI-ul va 'inventa' mai multe detalii fine.")
    
    if st.button("🚀 Transformă în 4K"):
        with st.spinner("Se procesează Upscale-ul (poate dura 30 sec)..."):
            try:
                # Folosim Clarity Upscaler pentru detalii profesionale
                res_upscale = fal_client.subscribe(
                    "fal-ai/clarity-upscaler",
                    arguments={
                        "image_url": st.session_state.last_image_url,
                        "creativity": creativity,
                        "rescale_factor": 2
                    },
                )
                st.session_state.upscaled_image_url = res_upscale["image"]["url"]
                st.success("Imaginea 4K este gata!")
            except Exception as e:
                st.error(f"Eroare Upscale: {e}")

    if st.session_state.upscaled_image_url:
        st.image(st.session_state.upscaled_image_url, caption="Rezultat 4K (Apasă click dreapta -> Save image as pentru rezoluție maximă)")
        st.link_button("Descarcă Imaginea 4K 📥", st.session_state.upscaled_image_url)
else:
    st.info("Generează o imagine la Pasul 1 pentru a debloca Upscaler-ul.")

st.divider()

# PASUL 3: VIDEO
st.header("🎥 Pasul 3: Animare Video")
if st.session_state.last_image_url:
    v_prompt = st.text_input("Descrie mișcarea dorită:", "Slow cinematic zoom, the painting comes to life with fluid textures")
    if st.button("🎬 Generează Video"):
        with st.spinner("Kling AI randează..."):
            try:
                # Trimitem imaginea (putem trimite și varianta upscale dacă vrem, dar durează mai mult)
                res_video = fal_client.subscribe(
                    "fal-ai/kling-video/v1/standard/image-to-video",
                    arguments={
                        "image_url": st.session_state.last_image_url,
                        "prompt": v_prompt
                    }
                )
                st.video(res_video['video']['url'])
            except Exception as e:
                st.error(f"Eroare Video: {e}")