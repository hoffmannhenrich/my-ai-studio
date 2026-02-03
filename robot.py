import streamlit as st
import fal_client
import os
import random
import time

if "FAL_KEY" in st.secrets:
    os.environ["FAL_KEY"] = st.secrets["FAL_KEY"]

st.set_page_config(page_title="AI Master Studio v3.2", page_icon="💎", layout="wide")

if 'txt2img_url' not in st.session_state: st.session_state.txt2img_url = None
if 'img2img_url' not in st.session_state: st.session_state.img2img_url = None
if 'seed' not in st.session_state: st.session_state.seed = random.randint(1, 999999)

with st.sidebar:
    st.header("⚙️ Control")
    if st.button("🎲 Seed Nou"):
        st.session_state.seed = random.randint(1, 999999)
        st.rerun()
    
    selected_style = st.selectbox("Alege stilul:", ["Photorealistic", "Cyberpunk", "Disney 3D", "Cinematic"])
    strength = st.slider("Putere Transformare", 0.1, 1.0, 0.75)
    
    st.divider()
    # NOU: Căsuța de Negative Prompt
    neg_prompt = st.text_area("🚫 CE SĂ EVITE (Negative Prompt):", value="evening dress, long dress, gown, blurry, deformed, bad anatomy, nsfw")

st.title("💎 AI Master Studio v3.2")
tab1, tab2 = st.tabs(["✨ Generare de la ZERO", "📸 Transformare FOTO"])

# TAB 1
with tab1:
    raw_prompt = st.text_input("Ce vrei să creezi?", placeholder="Ex: woman in denim shorts washing dishes")
    if st.button("🪄 Generează"):
        if raw_prompt:
            with st.spinner("AI-ul lucrează la precizie..."):
                try:
                    # Llama combină ideea ta cu stilul
                    llm_res = fal_client.subscribe("fal-ai/any-llm", arguments={
                        "model": "meta-llama/llama-3.1-70b-instruct", 
                        "prompt": f"Detailed English prompt for: '{raw_prompt}'. Style: {selected_style}. Return ONLY the prompt text."
                    })
                    
                    handler = fal_client.submit("fal-ai/flux/dev", arguments={
                        "prompt": llm_res["output"],
                        "negative_prompt": neg_prompt, # Trimitem instrucțiunile de "interzis"
                        "seed": st.session_state.seed,
                        "image_size": "landscape_4_3"
                    })
                    st.session_state.txt2img_url = handler.get()['images'][0]['url']
                except Exception as e: st.error(f"Eroare: {e}")

    if st.session_state.txt2img_url:
        st.image(st.session_state.txt2img_url, use_container_width=True)
