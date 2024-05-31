import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import cv2
from pyzbar import pyzbar

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

class BarcodeDetector:
    def __init__(self):
        self.barcode_detected = False
        self.detector = cv2.QRCodeDetector()  # For QR codes; adapt for other barcode types if needed

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        if not self.barcode_detected:
            # Autofocus and enhance image quality
            img = cv2.GaussianBlur(img, (5, 5), 0)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            barcodes = pyzbar.decode(img)
            for barcode in barcodes:
                x, y, w, h = barcode.rect
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                barcode_info = barcode.data.decode('utf-8')
                cv2.putText(img, barcode_info, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                self.barcode_detected = True
                st.session_state["barcode"] = barcode_info

        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("Barcode Scanner")

if "barcode" not in st.session_state:
    st.session_state["barcode"] = None

barcode_detector = BarcodeDetector()

webrtc_ctx = webrtc_streamer(
    key="barcode-scanner",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 2048},
            "height": {"ideal": 1536},
            "frameRate": {"ideal": 20},
        },
        "audio": False
    },
    video_processor_factory=lambda: barcode_detector,
    async_processing=True,
)

if st.session_state["barcode"]:
    st.write(f"Barcode detected: {st.session_state['barcode']}")
    webrtc_ctx.stop()
