import streamlit as st
import requests
import time

# 1. Page Layout Customization
st.set_page_config(
    page_title="Cloud Video Generator",
    page_icon="🎬",
    layout="centered"
)

# 2. Fetch the Secret Token securely from the Streamlit Cloud Settings
# (We will set this up in Step 3 via the web dashboard)
if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    st.error("🔑 Hugging Face Token missing! Please add 'HF_TOKEN' to your Streamlit App Secrets.")
    st.stop()

# Targeting a high-fidelity video model via the Hugging Face Serverless API
MODEL_ID = "Lightricks/LTX-Video"
API_URL = f"https://huggingface.co{MODEL_ID}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.title("🎬 Open-Source Cloud Video Generator")
st.write("Powered by LTX-Video & hosted completely free on Streamlit Cloud.")

# 3. User Interface Form Setup
with st.form("video_form"):
    prompt = st.text_area(
        "Describe your video", 
        placeholder="A majestic golden eagle soaring over snow-capped mountains, cinematic lighting..."
    )
    negative_prompt = st.text_input("Negative Prompt (Items to avoid)", value="blurry, low quality, static")
    
    submit_btn = st.form_submit_button("Generate Video", type="primary")

# 4. API Request and Processing Flow
if submit_btn:
    if not prompt:
        st.warning("Please type a video description prompt first!")
    else:
        with st.spinner("🤖 The cloud GPU is generating your video. Please wait..."):
            payload = {
                "inputs": prompt,
                "parameters": {
                    "negative_prompt": negative_prompt,
                    "num_inference_steps": 20,
                    "guidance_scale": 5.0
                }
            }
            
            try:
                # Send the data payload directly to the Hugging Face inference node
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                
                # If the API model is asleep on the server, wait 10 seconds and try again
                if response.status_code == 503:
                    st.info("⏳ Cloud model is waking up. Retrying generation in 10 seconds...")
                    time.sleep(10)
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

                if response.status_code == 200:
                    video_path = "generated_clip.mp4"
                    # Write the returned raw video stream into a temporary video file
                    with open(video_path, "wb") as f:
                        f.write(response.content)
                    
                    st.success("🎉 Video successfully rendered!")
                    st.video(video_path)
                    
                    # Provide a simple download utility for the end-user
                    with open(video_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Video File",
                            data=file,
                            file_name="ai_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
