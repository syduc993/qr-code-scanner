import streamlit as st
import cv2
from qreader import QReader
import numpy as np
from PIL import Image
import requests

# Cấu hình page
st.set_page_config(
    page_title="QR Code Scanner",
    page_icon="📷",
    layout="centered"
)

def main():
    st.title("📷 Quét QR Code để tra cứu thông tin")
    
    # Khởi tạo QReader
    qreader = QReader()

    # Tạo tabs để phân chia chức năng
    tab1, tab2 = st.tabs(["📸 Camera", "📤 Upload Ảnh"])
    
    with tab1:
        # Camera section
        if 'camera_running' not in st.session_state:
            st.session_state.camera_running = False
            
        col1, col2 = st.columns([3, 1])
        with col1:
            start_button = st.button("Bật Camera" if not st.session_state.camera_running else "Tắt Camera")
        
        if start_button:
            st.session_state.camera_running = not st.session_state.camera_running
            
        if st.session_state.camera_running:
            cap = cv2.VideoCapture(0)
            frame_placeholder = st.empty()
            
            while cap.isOpened() and st.session_state.camera_running:
                ret, frame = cap.read()
                if ret:
                    # Quét QR code
                    decoded_text = qreader.detect_and_decode(image=frame)
                    
                    if decoded_text:
                        # Vẽ khung xung quanh QR code
                        bboxes = qreader.detect(frame)
                        if bboxes is not None:
                            for bbox in bboxes:
                                points = bbox.astype(np.int32)
                                cv2.polylines(frame, [points], True, (0, 255, 0), 3)
                                
                                # Hiển thị dữ liệu
                                cv2.putText(frame, decoded_text[0], 
                                          (points[0][0], points[0][1] - 10),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        # Lưu kết quả và dừng camera
                        st.session_state['qr_result'] = decoded_text[0]
                        cap.release()
                        st.session_state.camera_running = False
                        st.experimental_rerun()
                        break
                    
                    # Hiển thị frame
                    frame_placeholder.image(frame, channels="BGR")
            
            if not st.session_state.camera_running:
                cap.release()

    with tab2:
        # Upload section
        uploaded_file = st.file_uploader("Tải lên ảnh chứa mã QR", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_np = np.array(image)
            
            # Quét QR code từ ảnh
            decoded_text = qreader.detect_and_decode(image=image_np)
            
            if decoded_text:
                st.session_state['qr_result'] = decoded_text[0]
            
            # Hiển thị ảnh
            st.image(image, caption='Ảnh đã tải lên')

    # Hiển thị kết quả quét trong một container
    if 'qr_result' in st.session_state:
        with st.container():
            st.markdown("---")
            qr_text = st.session_state['qr_result']
            st.success(f"✅ Đã quét mã QR: {qr_text}")
            
            # Gọi API với mã QR (thay thế URL API thật của bạn)
            try:
                API_URL = f"https://your-api.com/search/?qr_code={qr_text}"
                response = requests.get(API_URL)
                
                if response.status_code == 200:
                    result = response.json()
                    st.write("🔹 Kết quả tra cứu:")
                    st.json(result)
                else:
                    st.error("❌ Không tìm thấy dữ liệu!")
            except requests.RequestException:
                st.error("❌ Lỗi kết nối API!")

if __name__ == "__main__":
    main()