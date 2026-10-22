import streamlit as st
import requests
import time

# 1. Page Configuration
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="centered"
)

# 2. Securely read your token from Streamlit's environment backend
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("🔑 Token missing! Please paste your 'HF_TOKEN' into your Streamlit App Secrets panel.")
    st.stop()

# --- FIXED API ROUTING ---
API_URL = "https://huggingface.co"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
# -------------------------

st.title("🎬 Cloud AI Video Generator")
st.write("Write your code on GitHub, host on Streamlit, and run models on the cloud.")

# 3. Simple UI Form Setup
with st.form("generation_form"):
    prompt = st.text_area(
        "Describe your video scene", 
        placeholder="A majestic whale swimming through a sea of stars and cosmic dust, deep space ambient lighting..."
    )
    negative_prompt = st.text_input("Negative Prompt (Things to exclude)", value="blurry, low quality, static, distorted")
    
    submit_button = st.form_submit_button(label="Generate Video", type="primary")

# 4. Handle form processing when clicked
if submit_button:
    if not prompt:
        st.warning("Please type a descriptive prompt first!")
    else:
        with st.spinner("🤖 The cloud GPU is processing your tensors... This takes about 30-60 seconds."):
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
                    st.info("⏳ Cloud endpoint is waking up. Automatic retry starting in 15 seconds...")
                    time.sleep(15)
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

                if response.status_code == 200:
                    output_file = "rendered_video.mp4"
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    
                    st.success("🎉 Video generated successfully!")
                    st.video(output_file)
                    
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
