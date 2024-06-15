import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import cv2
from pyzbar import pyzbar
import threading

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
            print("Barcode detected:", self.barcode_val)
            # Stop the WebRTC stream
            webrtc_ctx.stop()
            break  # Exit the loop once a barcode is detected

        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("Barcode Scanner")

barcode_detector = BarcodeDetector()

webrtc_ctx = webrtc_streamer(
    key="barcode-scanner",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_processor_factory=lambda: barcode_detector,
    async_processing=True,
)

# Use a threading event to wait for the barcode detection
barcode_event = threading.Event()

def wait_for_barcode():
    while not barcode_detector.barcode_detected:
        barcode_event.wait(0.1)  # Wait for 100ms
    if barcode_detector.barcode_val:
        print("Barcode detected:", barcode_detector.barcode_val)
        st.write(f"Barcode detected: {barcode_detector.barcode_val}")

# Start a separate thread to wait for barcode detection
threading.Thread(target=wait_for_barcode, daemon=True).start()
