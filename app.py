import streamlit as st
import av
import requests
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from pyzbar.pyzbar import decode

st.title("📷 Quét QR Code để tra cứu thông tin")

# Bộ xử lý video để quét mã QR từ camera
class QRCodeScanner(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")  # Chuyển đổi frame thành ảnh
        qr_codes = decode(img)  # Quét mã QR trong ảnh

        for qr in qr_codes:
            x, y, w, h = qr.rect
            qr_text = qr.data.decode("utf-8")  # Lấy nội dung mã QR
            
            # Vẽ hình chữ nhật xung quanh mã QR
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(img, qr_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Lưu giá trị QR code vào session state
            st.session_state["qr_result"] = qr_text

        return img

# Hiển thị camera và quét QR
webrtc_streamer(key="qr_scan", video_transformer_factory=QRCodeScanner)

# Hiển thị mã QR đã quét
if "qr_result" in st.session_state:
    qr_text = st.session_state["qr_result"]
    st.success(f"✅ Đã quét mã QR: `{qr_text}`")

    # Gửi API để lấy dữ liệu từ server
    API_URL = f"https://your-api.com/search/?qr_code={qr_text}"
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        result = response.json()
        st.write("🔹 **Kết quả tra cứu:**")
        st.json(result)
    else:
        st.error("Không tìm thấy dữ liệu!")

