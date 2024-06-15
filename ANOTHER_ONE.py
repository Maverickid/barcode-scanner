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
        self.lock = threading.Lock()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        barcodes = pyzbar.decode(img)
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_info = barcode.data.decode('utf-8')
            cv2.putText(img, barcode_info, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            with self.lock:
                self.barcode_val = barcode_info
                self.barcode_detected = True

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
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

    if webrtc_ctx.state.playing:
        # Use a threading event to wait for the barcode detection
        barcode_event = threading.Event()

        def wait_for_barcode():
            while not barcode_detector.barcode_detected:
                barcode_event.wait(0.1)  # Wait for 100ms
            if barcode_detector.barcode_val:
                st.session_state.barcode_val = barcode_detector.barcode_val
                webrtc_ctx.stop()

        # Start a separate thread to wait for barcode detection
        threading.Thread(target=wait_for_barcode, daemon=True).start()

    # Display the detected barcode
    if 'barcode_val' in st.session_state:
        st.write(f"Barcode detected: {st.session_state.barcode_val}")

if __name__ == "__main__":
    main()
