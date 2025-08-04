import cv2
import numpy as np
import os

def nothing(x):
    """
    ฟังก์ชันเปล่าสำหรับ Trackbars
    """
    pass

def test_color_range_with_resize(image_path, scale_percent=50):
    """
    ปรับขนาดภาพก่อนแสดงผล และใช้ Trackbars เพื่อทดลองปรับค่าช่วงสี
    """
    # อ่านภาพ
    image = cv2.imread(image_path)

    # ตรวจสอบว่าภาพถูกโหลดสำเร็จหรือไม่
    if image is None:
        print(f"ไม่สามารถโหลดภาพ: {image_path}")
        return

    # ปรับขนาดภาพให้อยู่ในขนาดที่เหมาะสม
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image_resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    # แปลงภาพเป็น HSV
    hsv_image = cv2.cvtColor(image_resized, cv2.COLOR_BGR2HSV)

    # สร้างหน้าต่างสำหรับ Trackbars
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Lower Hue", "Trackbars", 0, 180, nothing)
    cv2.createTrackbar("Upper Hue", "Trackbars", 110, 180, nothing)
    cv2.createTrackbar("Lower Sat", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("Upper Sat", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("Lower Val", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("Upper Val", "Trackbars", 220, 255, nothing)

    while True:
        # อ่านค่าจาก Trackbars
        l_h = cv2.getTrackbarPos("Lower Hue", "Trackbars")
        u_h = cv2.getTrackbarPos("Upper Hue", "Trackbars")
        l_s = cv2.getTrackbarPos("Lower Sat", "Trackbars")
        u_s = cv2.getTrackbarPos("Upper Sat", "Trackbars")
        l_v = cv2.getTrackbarPos("Lower Val", "Trackbars")
        u_v = cv2.getTrackbarPos("Upper Val", "Trackbars")

        # กำหนดค่าช่วงสี
        lower_bound = np.array([l_h, l_s, l_v])
        upper_bound = np.array([u_h, u_s, u_v])

        # สร้าง Mask
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        result = cv2.bitwise_and(image_resized, image_resized, mask=mask)

        # แสดงภาพต้นฉบับ, แมสก์, และผลลัพธ์
        cv2.imshow("Original Image (Resized)", image_resized)
        cv2.imshow("Mask", mask)
        cv2.imshow("Result", result)

        # กด 'q' เพื่อออก
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()

def test_all_backgrounds(folder_path):
    """
    รันฟังก์ชัน test_color_range_with_resize กับทุกไฟล์ในโฟลเดอร์
    """
    scale_percent = 20  # ลดขนาดลง 20% สำหรับทุกภาพ
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}")
            test_color_range_with_resize(image_path, scale_percent)

# ตั้งค่าเส้นทางโฟลเดอร์พื้นหลัง
background_folder = r"C:\Project\backgrounds"

# เรียกใช้ฟังก์ชัน
test_all_backgrounds(background_folder)

# python test_color_range.py