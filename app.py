import streamlit as st
import cv2
from qreader import QReader
import numpy as np
from PIL import Image
import requests

def main():
    st.title("📷 Quét QR Code để tra cứu thông tin")
    
    # Khởi tạo QReader
    qreader = QReader()

    # Tạo file uploader để người dùng có thể tải lên ảnh
    uploaded_file = st.file_uploader("Tải lên ảnh chứa mã QR", type=['jpg', 'jpeg', 'png'])
    
    # Tạo camera capture
    if st.button("Sử dụng Camera"):
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()
        stop_button_pressed = st.button("Dừng Camera")
        
        while cap.isOpened() and not stop_button_pressed:
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
                            cv2.putText(frame, decoded_text[0], (points[0][0], points[0][1] - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Lưu kết quả và dừng camera
                    st.session_state['qr_result'] = decoded_text[0]
                    cap.release()
                    return
                
                # Hiển thị frame
                frame_placeholder.image(frame, channels="BGR")
        
        cap.release()

    # Xử lý ảnh được tải lên
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image_np = np.array(image)
        
        # Quét QR code từ ảnh
        decoded_text = qreader.detect_and_decode(image=image_np)
        
        if decoded_text:
            st.session_state['qr_result'] = decoded_text[0]
        
        # Hiển thị ảnh
        st.image(image, caption='Ảnh đã tải lên')

    # Hiển thị kết quả quét
    if 'qr_result' in st.session_state:
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