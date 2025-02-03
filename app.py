import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from PIL import Image
import requests

# Kiểm tra xem pyzbar đã được cài đặt chưa
try:
    from pyzbar.pyzbar import decode
except ImportError:
    st.error("⚠️ Chưa cài đặt pyzbar. Vui lòng cài đặt theo hướng dẫn bên dưới.")
    st.code("pip install pyzbar")
    st.stop()

def main():
    st.title("📷 Quét QR Code để tra cứu thông tin")
    
    # Tạo file uploader cho phép upload ảnh
    uploaded_file = st.file_uploader("Tải lên ảnh chứa mã QR", type=['jpg', 'jpeg', 'png'])
    
    # Xử lý camera
    camera_on = st.checkbox('Bật Camera')
    
    if camera_on:
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("Không thể kết nối camera!")
                break
                
            # Chuyển frame thành grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Quét QR code
            qr_codes = decode(gray)
            
            # Vẽ khung và hiển thị mã QR
            for qr in qr_codes:
                # Vẽ đường viền
                points = qr.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    points = hull
                
                points = np.array(points, np.int32)
                points = points.reshape((-1, 1, 2))
                cv2.polylines(frame, [points], True, (0, 255, 0), 3)
                
                # Hiển thị dữ liệu
                qr_data = qr.data.decode('utf-8')
                cv2.putText(frame, qr_data, (qr.rect.left, qr.rect.top - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Lưu kết quả
                st.session_state['qr_result'] = qr_data
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
        qr_codes = decode(image_np)
        
        if qr_codes:
            for qr in qr_codes:
                qr_data = qr.data.decode('utf-8')
                st.session_state['qr_result'] = qr_data
                break
            
            # Hiển thị ảnh với khung QR
            st.image(image, caption='Ảnh đã tải lên')
        else:
            st.warning("Không tìm thấy mã QR trong ảnh!")

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