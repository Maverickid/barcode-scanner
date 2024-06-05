import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode, RTCConfiguration
import cv2
from pyzbar import pyzbar

class BarcodeDetector(VideoProcessorBase):
    def __init__(self):
        super().__init__()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        barcodes = pyzbar.decode(img)
        
        for barcode in barcodes:
            barcode_info = barcode.data.decode('utf-8')
            st.write(f"Barcode detected: {barcode_info}")
            webrtc_ctx.stop()
            return

        return frame

st.title("Barcode Scanner")

webrtc_ctx = webrtc_streamer(
    key="barcode-scanner",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
    media_stream_constraints={"video": True, "audio": False},
    video_processor_factory=BarcodeDetector,
    async_processing=True,
)

