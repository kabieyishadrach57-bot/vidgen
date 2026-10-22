import streamlit as st
import requests
import time

# 1. Page Configuration
st.set_page_config(
    page_title="Free Cloud AI Video Generator",
    page_icon="🎬",
    layout="centered"
)

# 2. Securely read your token from Streamlit's environment backend
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("🔑 Token missing! Please paste your 'HF_TOKEN' into your Streamlit App Secrets panel.")
    st.stop()

# --- FIXED PUBLIC SUITE ENDPOINT & HEADERS ---
# Using an unlocked serverless video/multimodal endpoint pattern
API_URL = "https://huggingface.co"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
# ---------------------------------------------

st.title("🎬 Free Cloud AI Video Generator")
st.write("Hosted on Streamlit Cloud. Operating completely free via Hugging Face Serverless nodes.")

# 3. Simple UI Form Setup
with st.form("generation_form"):
    prompt = st.text_area(
        "Describe your video scene", 
        placeholder="An astronaut walking on a neon purple alien planet, crystal structures glowing around them..."
    )
    negative_prompt = st.text_input("Negative Prompt (Things to exclude)", value="blurry, low quality, static, distorted")
    
    submit_button = st.form_submit_button(label="Generate Video", type="primary")

# 4. Handle form processing when clicked
if submit_button:
    if not prompt:
        st.warning("Please type a descriptive prompt first!")
    else:
        with st.spinner("🤖 The cloud GPU is processing your request... This takes about 30-60 seconds."):
            payload = {
                "inputs": prompt,
                "parameters": {
                    "negative_prompt": negative_prompt,
                    "num_inference_steps": 20,
                    "guidance_scale": 5.0
                }
            }
            
            try:
                # Send the requests to the serverless endpoint
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                
                # If the serverless node is sleeping, wait 15 seconds and trigger again
                if response.status_code == 503:
                    st.info("⏳ Cloud endpoint is waking up on Hugging Face. Automatic retry starting in 15 seconds...")
                    time.sleep(15)
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

                if response.status_code == 200:
                    output_file = "rendered_video.mp4"
                    # Capture raw file stream and write to server memory
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    
                    st.success("🎉 Asset generated successfully!")
                    st.video(output_file)
                    
                    # Provide an immediate download button
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="📥 Download Video",
                            data=file,
                            file_name="ai_video_output.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
