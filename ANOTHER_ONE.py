import streamlit as st
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image

def detect_barcode(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Detect barcodes in the image
    barcodes = pyzbar.decode(gray)
    return barcodes

def draw_barcode_info(image, barcodes):
    for barcode in barcodes:
        # Get the bounding box of the barcode
        x, y, w, h = barcode.rect
        # Draw a rectangle around the barcode
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Get the barcode data and type
        barcode_info = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        # Put the barcode data and type on the image
        cv2.putText(image, f"{barcode_info} ({barcode_type})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

st.title("Barcode Scanner")

uploaded_file = st.file_uploader("Upload a picture of the barcode", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the uploaded image
    image = Image.open(uploaded_file)
    image = np.array(image)

    # Detect barcodes in the image
    barcodes = detect_barcode(image)

    if barcodes:
        st.success("Barcode detected!")
        # Draw the barcode information on the image
        image = draw_barcode_info(image, barcodes)
        # Display the image with barcode information
        st.image(image, caption='Detected barcodes', use_column_width=True)
        for barcode in barcodes:
            st.write(f"Barcode: {barcode.data.decode('utf-8')}, Type: {barcode.type}")
    else:
        st.warning("No barcode detected. Please try again with a clearer image.")
else:
    st.info("Please upload an image of the barcode.")
