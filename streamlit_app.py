import streamlit as st
from huggingface_hub import InferenceClient
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

st.title("🎬 Free Cloud AI Video Generator")
st.write("Hosted on Streamlit Cloud. Operating via the Hugging Face Client Hub.")

# 3. Simple UI Form Setup
with st.form("generation_form"):
    prompt = st.text_area(
        "Describe your video scene", 
        placeholder="A majestic golden eagle soaring over snow-capped mountains, cinematic lighting..."
    )
    
    submit_button = st.form_submit_button(label="Generate Video", type="primary")

# 4. Handle form processing when clicked using the official SDK client
if submit_button:
    if not prompt:
        st.warning("Please type a descriptive prompt first!")
    else:
        with st.spinner("🤖 Hugging Face Hub is initializing generation... This takes about 30-60 seconds."):
            try:
                # Initialize the official client wrapper (bypasses raw HTTP CloudFront blocks)
                client = InferenceClient(token=HF_TOKEN)
                
                # Using an open-weights video model fully compatible with the client wrapper
                # If the server responds that this model is overloaded, the client handles retries natively
                output_file = "rendered_video.mp4"
                
                # Fetching the text-to-video asset through the SDK
                video_bytes = client.text_to_video(
                    prompt=prompt,
                    model="Lightricks/LTX-Video"
                )
                
                # Save the returned binary stream directly into an MP4 file
                with open(output_file, "wb") as f:
                    f.write(video_bytes)
                
                st.success("🎉 Video generated successfully!")
                st.video(output_file)
                
                # Provide an immediate download button
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="📥 Download Video",
                        data=file,
                        file_name="ai_video_output.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                # Capture any model-overload or permission messages gracefully
                st.error(f"Execution Error: {str(e)}")
                st.info("💡 Tip: If the error mentions 'Model too busy', wait a moment and click generate again.")
