import streamlit as st
import fal_client
import os
import random

# --- CONFIGURARE SECURIZATĂ (Cloud + Local) ---
if "FAL_KEY" in st.secrets:
    os.environ["FAL_KEY"] = st.secrets["FAL_KEY"]
else:
    # Aici pui cheia ta doar pentru teste locale. 
    # Când urci pe GitHub, Streamlit va folosi Secrets.
    os.environ["FAL_KEY"] = "PUNE_CHEIA_AICI_DOAR_PT_TEST_LOCAL"

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="AI Master Studio 2026", page_icon="💎", layout="wide")

if 'last_image_url' not in st.session_state: st.session_state.last_image_url = None
if 'enhanced_prompt' not in st.session_state: st.session_state.enhanced_prompt = ""
if 'seed' not in st.session_state: st.session_state.seed = random.randint(1, 999999)

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
        with st.spinner("Asistentul AI lucrează..."):
            try:
                res = fal_client.subscribe("fal-ai/any-llm", arguments={
                    "model": "meta-llama/llama-3.1-70b-instruct", 
                    "prompt": f"Detailed English prompt for: '{user_idea}'. Preserve facial identity. Return ONLY the prompt."
                })
                st.session_state.enhanced_prompt = res["output"]
            except Exception as e: st.error(f"Eroare: {e}")

final_prompt = st.text_area("Prompt Final:", value=st.session_state.enhanced_prompt)

# PASUL 1: FOTO
uploaded_file = st.file_uploader("Încarcă poza:", type=["jpg", "png", "jpeg"])
if st.button("Generează Imaginea 🎨", type="primary"):
    if uploaded_file and final_prompt:
        with st.spinner("Se pictează..."):
            try:
                img_url = fal_client.upload_file(uploaded_file.getvalue())
                handler = fal_client.submit("fal-ai/flux/dev/image-to-image", arguments={
                    "image_url": img_url, "prompt": final_prompt, "strength": strength, "seed": st.session_state.seed
                })
                st.session_state.last_image_url = handler.get()['images'][0]['url']
            except Exception as e: st.error(f"Eroare: {e}")

if st.session_state.last_image_url:
    st.image(st.session_state.last_image_url, use_container_width=True)
    
    # PASUL 2: VIDEO
    if st.button("🚀 Transformă în Video"):
        with st.spinner("Randare video Kling..."):
            try:
                res_video = fal_client.subscribe("fal-ai/kling-video/v1/standard/image-to-video", arguments={
                    "image_url": st.session_state.last_image_url, "prompt": "Fluid cinematic motion"
                })
                st.video(res_video['video']['url'])
            except Exception as e: st.error(f"Eroare: {e}")