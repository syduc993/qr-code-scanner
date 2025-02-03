import streamlit as st
import av
import requests
import cv2
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

st.title("📷 Quét QR Code để tra cứu thông tin")

# Bộ xử lý video để quét mã QR từ camera
class QRCodeScanner(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")  # Chuyển đổi frame thành ảnh
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Chuyển sang ảnh xám
        
        # Quét mã QR sử dụng OpenCV
        detector = cv2.QRCodeDetector()
        retval, decoded_info, points, straight_qrcode = detector(img)

        if retval:
            for i in range(len(decoded_info)):
                qr_text = decoded_info[i]
                pts = points[i]
                pts = pts.astype(int)
                cv2.polylines(img, [pts], True, (0, 255, 0), 3)  # Vẽ đường bao quanh mã QR
                cv2.putText(img, qr_text, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # Lưu giá trị QR code vào session state
                st.session_state["qr_result"] = qr_text

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Hiển thị camera và quét QR
webrtc_streamer(key="qr_scan", video_processor_factory=QRCodeScanner)

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
