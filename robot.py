import streamlit as st
import fal_client
import os
import random
import time

# --- CONFIGURARE SECURIZATĂ ---
# Dacă suntem pe Cloud, luăm cheia din Secrets. Dacă suntem local, folosim cheia de test.
if "FAL_KEY" in st.secrets:
    os.environ["FAL_KEY"] = st.secrets["FAL_KEY"]
# else:
#     os.environ["FAL_KEY"] = "PUNE_CHEIA_TA_AICI_DOAR_PT_TEST_LOCAL"

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="AI Master Studio v2", page_icon="🎨", layout="wide")

# Inițializăm memoria
if 'txt2img_url' not in st.session_state: st.session_state.txt2img_url = None
if 'img2img_url' not in st.session_state: st.session_state.img2img_url = None
if 'seed' not in st.session_state: st.session_state.seed = random.randint(1, 999999)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Control General")
    if st.button("🎲 Seed Nou (Resetare Stil)"):
        st.session_state.seed = random.randint(1, 999999)
        st.rerun()
    st.session_state.seed = st.number_input("Seed Activ:", value=st.session_state.seed, help="Același număr = aceeași 'mână' a artistului.")
    
    st.divider()
    st.header("🔧 Setări Transformare Foto")
    strength = st.slider("Puterea Modificării", 0.1, 1.0, 0.75, 0.05, help="Valori mari (0.9+) pentru schimbări radicale (ex: camera -> junglă).")

st.title("🎨 AI Master Studio v2")
st.markdown("Alege fluxul de lucru dorit:")

tab1, tab2 = st.tabs(["✨ Generare de la ZERO (Text-to-Image)", "📸 Transformare FOTO (Image-to-Image)"])

# =========================================
# TAB 1: GENERARE DE LA ZERO (Text-to-Image)
# =========================================
with tab1:
    st.header("Creează ceva nou din cuvinte")
    raw_prompt = st.text_input("Ce vrei să creezi?", placeholder="Ex: un cui spiralat verde, fotorealist")
    
    # Asistent Llama pentru Text-to-Image
    if st.button("🪄 Generează Imaginea (cu Asistent AI)"):
        if raw_prompt:
            with st.spinner("Asistentul Llama rafinează ideea..."):
                try:
                    # 1. Rafinăm promptul
                    llm_res = fal_client.subscribe("fal-ai/any-llm", arguments={
                        "model": "meta-llama/llama-3.1-70b-instruct", 
                        "prompt": f"Create a highly detailed, photorealistic English prompt for: '{raw_prompt}'. Focus on textures, lighting, and realism. Return ONLY the prompt."
                    })
                    enhanced_prompt = llm_res["output"]
                    st.caption(f"Prompt rafinat: {enhanced_prompt}")

                    # 2. Generăm imaginea de la zero (folosind Flux Dev)
                    with st.spinner("Se generează imaginea..."):
                        handler = fal_client.submit("fal-ai/flux/dev", arguments={
                            "prompt": enhanced_prompt,
                            "seed": st.session_state.seed,
                            "image_size": "landscape_4_3" # Poți schimba în "square_hd" sau "portrait_4_3"
                        })
                        result = handler.get()
                        st.session_state.txt2img_url = result['images'][0]['url']
                        st.success("Gata!")

                except Exception as e: st.error(f"Eroare: {e}")

    if st.session_state.txt2img_url:
        st.image(st.session_state.txt2img_url, caption="Rezultat Text-to-Image", use_container_width=True)
        # Opțiune de Upscale rapid
        if st.button("💎 Mărește la 4K (Upscale)", key="upscale_txt"):
             with st.spinner("Se face upscale..."):
                try:
                    res_up = fal_client.subscribe("fal-ai/clarity-upscaler", arguments={"image_url": st.session_state.txt2img_url, "creativity": 0.3, "rescale_factor": 2})
                    st.image(res_up["image"]["url"], caption="Versiune 4K")
                except Exception as e: st.error(f"Eroare Upscale: {e}")


# =========================================
# TAB 2: TRANSFORMARE FOTO (Image-to-Image)
# =========================================
with tab2:
    st.header("Modifică o poză existentă")
    st.info(f"💡 Sfat: Pentru schimbări radicale (ex: junglă), crește 'Puterea Modificării' din stânga la peste 0.90. Valoarea actuală: {strength}")

    user_idea_img = st.text_input("Cum modificăm poza?", placeholder="Ex: transformă camera într-o junglă luxuriantă")
    uploaded_file = st.file_uploader("Încarcă poza de bază:", type=["jpg", "png", "jpeg"])

    if st.button("🎨 Transformă Poza (cu Asistent AI)"):
        if uploaded_file and user_idea_img:
            with st.spinner("Asistentul Llama gândește strategia..."):
                try:
                    # 1. Rafinăm promptul (specific pentru păstrarea structurii sau nu)
                    preserve_instruction = "preserve the main structure but change textures radically" if strength < 0.85 else "completely transform the scene, ignoring original structure"
                    llm_res = fal_client.subscribe("fal-ai/any-llm", arguments={
                        "model": "meta-llama/llama-3.1-70b-instruct", 
                        "prompt": f"Detailed English prompt for Image-to-Image transformation: '{user_idea_img}'. Instruction: {preserve_instruction}. Return ONLY the prompt."
                    })
                    enhanced_prompt_img = llm_res["output"]
                    st.caption(f"Prompt rafinat: {enhanced_prompt_img}")

                    # 2. Procesăm imaginea (Metoda fișier temporar pentru Cloud)
                    with st.spinner("Se pictează..."):
                        temp_name = f"temp_{int(time.time())}.jpg"
                        with open(temp_name, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        img_url = fal_client.upload_file(temp_name)
                        handler = fal_client.submit("fal-ai/flux/dev/image-to-image", arguments={
                            "image_url": img_url,
                            "prompt": enhanced_prompt_img,
                            "strength": strength, # Folosim slider-ul din stânga
                            "seed": st.session_state.seed
                        })
                        st.session_state.img2img_url = handler.get()['images'][0]['url']
                        if os.path.exists(temp_name): os.remove(temp_name)
                        st.success("Transformare reușită!")

                except Exception as e: st.error(f"Eroare: {e}")

    if st.session_state.img2img_url:
        st.image(st.session_state.img2img_url, caption="Rezultat Transformare", use_container_width=True)
        # Opțiune de Video rapid
        if st.button("🎬 Animare Video", key="video_img"):
             with st.spinner("Se randează video Kling..."):
                try:
                    res_vid = fal_client.subscribe("fal-ai/kling-video/v1/standard/image-to-video", arguments={"image_url": st.session_state.img2img_url, "prompt": "Slow cinematic camera move"})
                    st.video(res_vid['video']['url'])
                except Exception as e: st.error(f"Eroare Video: {e}")
