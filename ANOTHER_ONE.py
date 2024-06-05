import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import cv2
from pyzbar import pyzbar
import time

RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})


class BarcodeDetector:
    def __init__(self):
        self.barcode_detected = False
        self.last_detection_time = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        current_time = time.time()

        if not self.barcode_detected or (current_time - self.last_detection_time > 0.5):  # 0.5-second delay
            barcodes = pyzbar.decode(img)
            for barcode in barcodes:
                x, y, w, h = barcode.rect
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                barcode_info = barcode.data.decode('utf-8')
                cv2.putText(img, barcode_info, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                self.barcode_detected = True
                self.last_detection_time = current_time
                st.session_state["barcode"] = barcode_info

        return av.VideoFrame.from_ndarray(img, format="bgr24")


def main():
    st.title("Barcode Scanner")

    if "barcode" not in st.session_state:
        st.session_state["barcode"] = None

    barcode_detector = BarcodeDetector()

    webrtc_ctx = webrtc_streamer(
        key="barcode-scanner",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        video_processor_factory=lambda: barcode_detector,
        async_processing=True,
    )

    if st.session_state["barcode"]:
        st.write(f"Barcode detected: {st.session_state['barcode']}")
        webrtc_ctx.stop()


if __name__ == "__main__":
    main()
