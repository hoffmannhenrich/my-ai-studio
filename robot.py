import streamlit as st
import fal_client
import os
import random
import time

# --- CONFIGURARE SECURIZATĂ ---
if "FAL_KEY" in st.secrets:
    os.environ["FAL_KEY"] = st.secrets["FAL_KEY"]

st.set_page_config(page_title="AI Master Studio v3.1", page_icon="💎", layout="wide")

# Inițializăm memoria de sesiune
if 'txt2img_url' not in st.session_state: st.session_state.txt2img_url = None
if 'img2img_url' not in st.session_state: st.session_state.img2img_url = None
if 'seed' not in st.session_state: st.session_state.seed = random.randint(1, 999999)

# --- SIDEBAR (PANOU DE CONTROL) ---
with st.sidebar:
    st.header("⚙️ Setări Studio")
    if st.button("🎲 Generează Seed Nou"):
        st.session_state.seed = random.randint(1, 999999)
        st.rerun()
    st.write(f"Seed curent: `{st.session_state.seed}`")
    
    st.divider()
    st.header("🎨 Stil Artistic")
    selected_style = st.selectbox("Alege stilul:", [
        "Photorealistic", "Cyberpunk Neon", "Disney/Pixar 3D", 
        "Oil Painting", "Pencil Sketch", "Cinematic Movie Look", "Vintage 70s Photo"
    ])
    
    st.divider()
    st.header("🔧 Putere Transformare")
    strength = st.slider("Strength (doar pt Foto)", 0.1, 1.0, 0.75, 0.05, help="0.95 = transformare totală")

st.title("💎 AI Master Studio v3.1")

tab1, tab2 = st.tabs(["✨ Generare de la ZERO", "📸 Transformare FOTO"])

# =========================================
# TAB 1: GENERARE DE LA ZERO (Text-to-Image)
# =========================================
with tab1:
    raw_prompt = st.text_input("Ce vrei să creezi?", placeholder="Ex: un cui verde spiralat")
    
    if st.button("🪄 Generează Imagine"):
        if raw_prompt:
            with st.spinner("Llama & Flux lucrează..."):
                try:
                    llm_res = fal_client.subscribe("fal-ai/any-llm", arguments={
                        "model": "meta-llama/llama-3.1-70b-instruct", 
                        "prompt": f"Detailed English prompt for: '{raw_prompt}'. Style: {selected_style}. Return ONLY the prompt text."
                    })
                    enhanced_prompt = llm_res["output"]
                    
                    handler = fal_client.submit("fal-ai/flux/dev", arguments={
                        "prompt": enhanced_prompt, "seed": st.session_state.seed, "image_size": "landscape_4_3"
                    })
                    st.session_state.txt2img_url = handler.get()['images'][0]['url']
                except Exception as e: st.error(f"Eroare: {e}")

    if st.session_state.txt2img_url:
        st.image(st.session_state.txt2img_url, use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎬 Animare Video", key="vid_t1"):
                with st.spinner("Randare Kling..."):
                    res = fal_client.subscribe("fal-ai/kling-video/v1/standard/image-to-video", arguments={"image_url": st.session_state.txt2img_url, "prompt": "Cinematic motion"})
                    st.video(res['video']['url'])
        with col2:
            if st.button("💎 Upscale 4K", key="up_t1"):
                with st.spinner("Mărire calitate..."):
                    res = fal_client.subscribe("fal-ai/clarity-upscaler", arguments={"image_url": st.session_state.txt2img_url})
                    st.image(res["image"]["url"])


# =========================================
# TAB 2: TRANSFORMARE FOTO (Image-to-Image)
# =========================================
with tab2:
    user_idea_img = st.text_input("Ce vrei să modifici la poză?", placeholder="Ex: transformă în junglă")
    uploaded_file = st.file_uploader("Încarcă poza:", type=["jpg", "png", "jpeg"])

    if st.button("🎨 Transformă"):
        if uploaded_file and user_idea_img:
            with st.spinner("Se procesează imaginea..."):
                try:
                    llm_res = fal_client.subscribe("fal-ai/any-llm", arguments={
                        "model": "meta-llama/llama-3.1-70b-instruct", 
                        "prompt": f"Detailed Image-to-Image prompt: '{user_idea_img}'. Style: {selected_style}. Return ONLY the prompt."
                    })
                    
                    temp_name = f"temp_{int(time.time())}.jpg"
                    with open(temp_name, "wb") as f: f.write(uploaded_file.getbuffer())
                    
                    img_url = fal_client.upload_file(temp_name)
                    handler = fal_client.submit("fal-ai/flux/dev/image-to-image", arguments={
                        "image_url": img_url, "prompt": llm_res["output"], 
                        "strength": strength, "seed": st.session_state.seed
                    })
                    st.session_state.img2img_url = handler.get()['images'][0]['url']
                    if os.path.exists(temp_name): os.remove(temp_name)
                except Exception as e: st.error(f"Eroare: {e}")

    if st.session_state.img2img_url:
        st.image(st.session_state.img2img_url, use_container_width=True)
        col3, col4 = st.columns(2)
        with col3:
            if st.button("🎬 Animare Video", key="vid_t2"):
                with st.spinner("Randare Kling..."):
                    res = fal_client.subscribe("fal-ai/kling-video/v1/standard/image-to-video", arguments={"image_url": st.session_state.img2img_url, "prompt": "Fluid cinematic movement"})
                    st.video(res['video']['url'])
        with col4:
            if st.button("💎 Upscale 4K", key="up_t2"):
                with st.spinner("Mărire calitate..."):
                    res = fal_client.subscribe("fal-ai/clarity-upscaler", arguments={"image_url": st.session_state.img2img_url})
                    st.image(res["image"]["url"])
