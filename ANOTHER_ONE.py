import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import cv2
from pyzbar import pyzbar

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

class BarcodeDetector:
    def __init__(self):
        self.barcode_val = None
        self.barcode_detected = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect barcode
        barcodes = pyzbar.decode(gray_frame)
        if barcodes:
            barcode_info = barcodes[0].data.decode('utf-8')
            self.barcode_val = barcode_info
            self.barcode_detected = True
            print("Barcode detected:", self.barcode_val)
            st.stop()

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("Barcode Scanner")
    
    # Create WebRTC streamer
    webrtc_ctx = webrtc_streamer(
        key="barcode-scanner",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        video_processor_factory=BarcodeDetector,
        async_processing=True,
    )

    if webrtc_ctx.video_processor.barcode_detected:
        st.write(f"Barcode detected: {webrtc_ctx.video_processor.barcode_val}")

if __name__ == "__main__":
    main()
