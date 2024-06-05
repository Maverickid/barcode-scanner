import threading
import cv2
import streamlit as st
from pyzbar import pyzbar

from streamlit_webrtc import webrtc_streamer

lock = threading.Lock()
img_container = {"img": None}

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    with lock:
        img_container["img"] = img

    return frame

def detect_barcode():
    while True:
        with lock:
            img = img_container["img"]
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            barcodes = pyzbar.decode(gray)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                print("Barcode detected:", barcode_data)
                st.write(f"Barcode detected: {barcode_data}")
                # Stop the video stream
                webrtc_streamer.stop()
                break

# Start barcode detection thread
barcode_thread = threading.Thread(target=detect_barcode)
barcode_thread.start()

webrtc_streamer(key="example", video_frame_callback=video_frame_callback)
