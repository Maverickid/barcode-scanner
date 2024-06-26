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

        barcodes = pyzbar.decode(img)
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_info = barcode.data.decode('utf-8')
            cv2.putText(img, barcode_info, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            self.barcode_val = barcode_info
            self.barcode_detected = True
            st.session_state.barcode_val = barcode_info  # Update the session state
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("Barcode Scanner")

    if 'barcode_val' not in st.session_state:
        st.session_state.barcode_val = None

    barcode_detector = BarcodeDetector()

    webrtc_ctx = webrtc_streamer(
        key="barcode-scanner",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        video_processor_factory=lambda: barcode_detector,
        async_processing=True,
    )

    if st.session_state.barcode_val:
        st.write(f"Barcode detected: {st.session_state.barcode_val}")
        if webrtc_ctx.state.playing:
            webrtc_ctx.stop()

if __name__ == "__main__":
    main()
