# นำเข้า library สำหรับจัดการไฟล์และโฟลเดอร์
import os
# นำเข้า OpenCV library สำหรับประมวลผลภาพ
import cv2
# นำเข้า NumPy library สำหรับการคำนวณทางคณิตศาสตร์
import numpy as np
# นำเข้า library สำหรับสุ่มค่า
import random

def detect_water_area(image):
    """
    ตรวจจับพื้นที่น้ำในภาพโดยใช้สี HSV และฟิลเตอร์ทาง Morphological
    คืนค่าเป็น mask (พื้นที่ที่ถือว่าเป็นน้ำ)
    """
    # กำหนดขอบล่างของสี HSV ที่ถือว่าเป็นน้ำ (สีดำเข้มถึงน้ำเงินเข้ม)
    LOWER_BOUND = np.array([0, 0, 0])  # สีดำเข้มถึงน้ำเงินเข้ม (ค่าทดลองจากภาพจริง)
    # กำหนดขอบบนของสี HSV ที่ถือว่าเป็นน้ำ
    UPPER_BOUND = np.array([110, 255, 220])

    # แปลงภาพจาก BGR เป็น HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # สร้าง mask โดยหาพิกเซลที่อยู่ในช่วงสีที่กำหนด
    mask = cv2.inRange(hsv_image, LOWER_BOUND, UPPER_BOUND)

    # ใช้ Morphological Filter เพื่อขจัด noise
    # สร้าง kernel ขนาด 5x5 สำหรับ morphological operations
    kernel = np.ones((5, 5), np.uint8)
    # ใช้ MORPH_CLOSE เพื่อปิดช่องว่างเล็กๆ ในพื้นที่น้ำ
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    # ใช้ MORPH_OPEN เพื่อลบ noise เล็กๆ ออกจากพื้นที่น้ำ
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # ส่งคืน mask ที่แสดงพื้นที่น้ำ
    return mask

def place_feature_on_water(background, feature, water_mask):
    """
    วางภาพฟีเจอร์ลงบนพื้นหลัง โดยสุ่มตำแหน่งที่อยู่ในพื้นที่น้ำเท่านั้น
    คืนค่าภาพฟีเจอร์ที่วางแล้ว + ตำแหน่ง x, y
    """
    # เก็บขนาดของภาพพื้นหลัง (height, width, channels)
    bg_height, bg_width, _ = background.shape
    # เก็บขนาดของภาพฟีเจอร์ (height, width, channels)
    fg_height, fg_width, _ = feature.shape

    # สุ่ม scale ของฟีเจอร์ (ขนาด 40-80% ของขนาดเดิม)
    scale = np.random.uniform(0.4, 0.8)
    # คำนวณความกว้างใหม่ของฟีเจอร์
    new_fg_width = int(fg_width * scale)
    # คำนวณความสูงใหม่ของฟีเจอร์
    new_fg_height = int(fg_height * scale)
    # ปรับขนาดฟีเจอร์ตาม scale ที่สุ่มได้
    feature_resized = cv2.resize(feature, (new_fg_width, new_fg_height), interpolation=cv2.INTER_AREA)

    # หาพิกัดของพื้นที่น้ำใน mask
    # np.where(water_mask > 0) หาพิกัดที่ mask > 0 (มีน้ำ)
    # np.column_stack จัดเรียงพิกัดเป็น array ของ [y, x]
    water_coords = np.column_stack(np.where(water_mask > 0))
    # ถ้าไม่มีพื้นที่น้ำเลย ให้ return None
    if len(water_coords) == 0:
        return None, None, None

    # สุ่มพิกัดวางจนกว่าจะเจอที่เหมาะสม
    attempts = 0  # ตัวนับจำนวนครั้งที่ลอง
    while attempts < 10000:  # ลองสูงสุด 10,000 ครั้ง
        # สุ่มพิกัดจากพื้นที่น้ำ
        y, x = random.choice(water_coords)
        # ตรวจสอบว่าฟีเจอร์ไม่เกินขอบเขตของภาพพื้นหลัง
        if (x + new_fg_width <= bg_width and y + new_fg_height <= bg_height):
            # หาพื้นที่ใน mask ที่จะวางฟีเจอร์
            region = water_mask[y:y + new_fg_height, x:x + new_fg_width]
            # ตรวจสอบว่าพื้นที่น้ำในบริเวณนั้นมากกว่า 50% หรือไม่
            if np.count_nonzero(region) / (new_fg_width * new_fg_height) >= 0.5:
                break  # ถ้าเหมาะสม ให้ออกจากลูป
        attempts += 1  # เพิ่มตัวนับ

    # ถ้าลองเกิน 10,000 ครั้งแล้วยังไม่เจอตำแหน่งที่เหมาะสม
    if attempts >= 10000:
        return None, None, None

    # สุ่มหมุนฟีเจอร์
    # สุ่มมุมการหมุน 0-360 องศา
    angle = np.random.uniform(0, 360)
    # สร้าง transformation matrix สำหรับหมุน
    # จุดศูนย์กลางการหมุนคือกลางภาพฟีเจอร์
    M = cv2.getRotationMatrix2D((new_fg_width // 2, new_fg_height // 2), angle, 1)
    # หมุนฟีเจอร์ตามมุมที่สุ่มได้
    # borderMode=cv2.BORDER_CONSTANT ใช้สีดำสำหรับพื้นที่ที่เกินขอบเขต
    # borderValue=(0, 0, 0, 0) กำหนดสีขอบเป็นโปร่งใส
    rotated_feature = cv2.warpAffine(feature_resized, M, (new_fg_width, new_fg_height), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    # ส่งคืนฟีเจอร์ที่หมุนแล้วและตำแหน่ง x, y
    return rotated_feature, x, y

def overlay_feature(background, feature, x, y):
    """
    วางฟีเจอร์ลงบนภาพพื้นหลัง โดยใช้ alpha channel
    """
    # เก็บขนาดของฟีเจอร์
    fg_height, fg_width, _ = feature.shape
    # สร้างสำเนาของภาพพื้นหลัง
    overlay = background.copy()
    # วนลูปผ่านทุกพิกเซลของฟีเจอร์
    for i in range(fg_height):
        for j in range(fg_width):
            # ตรวจสอบว่า alpha channel > 0 (มีเนื้อหา)
            if feature[i, j, 3] > 0:
                # วางสี RGB ของฟีเจอร์ลงบนภาพพื้นหลัง
                overlay[y + i, x + j] = feature[i, j, :3]
    # ส่งคืนภาพที่วางฟีเจอร์แล้ว
    return overlay

def get_true_bbox_from_alpha(feature_image):
    """
    หา bounding box ที่แท้จริงจาก alpha channel
    """
    # เอา alpha channel (ช่องที่ 4) ของภาพฟีเจอร์
    alpha = feature_image[:, :, 3]
    # หาพิกัดที่ alpha > 0 (มีเนื้อหา)
    coords = cv2.findNonZero(alpha)
    # ถ้าไม่มีพิกัดที่มีเนื้อหา
    if coords is None:
        # ส่งคืน bounding box ของภาพทั้งหมด
        return 0, 0, feature_image.shape[1], feature_image.shape[0]
    # หา bounding box ที่ครอบคลุมพิกัดทั้งหมด
    x, y, w, h = cv2.boundingRect(coords)
    # ส่งคืนตำแหน่งและขนาดของ bounding box
    return x, y, w, h

def save_annotation(annotation_path, x, y, width, height, angle, bg_width, bg_height):
    """
    สร้าง annotation ไฟล์ในรูปแบบ YOLO (normalized)
    """
    # คำนวณจุดศูนย์กลางของ bounding box (normalized)
    x_center = (x + width / 2) / bg_width
    y_center = (y + height / 2) / bg_height
    # คำนวณความกว้างและความสูง (normalized)
    norm_width = width / bg_width
    norm_height = height / bg_height

    # เขียนไฟล์ annotation ในรูปแบบ YOLO
    with open(annotation_path, 'w') as f:
        # รูปแบบ: class x_center y_center width height
        f.write(f"0 {x_center} {y_center} {norm_width} {norm_height}\n")

def generate_synthetic_dataset(backgrounds_path, features_path, output_path, annotations_path, num_images, log_callback=None):
    """
    สร้างภาพ Synthetic โดยการสุ่มนำฟีเจอร์ไปวางบนพื้นที่น้ำของภาพพื้นหลัง
    และบันทึก annotation ประกอบ (แบบ YOLO format)
    """
    # สร้างรายการ path ของภาพพื้นหลังทั้งหมด (เฉพาะไฟล์ .jpg)
    backgrounds = [os.path.join(backgrounds_path, f) for f in sorted(os.listdir(backgrounds_path)) if f.endswith('.jpg')]
    # สร้างรายการ path ของภาพฟีเจอร์ทั้งหมด (เฉพาะไฟล์ .png)
    features = [os.path.join(features_path, f) for f in sorted(os.listdir(features_path)) if f.endswith('.png')]

    # สร้างโฟลเดอร์ output หากยังไม่มี
    os.makedirs(output_path, exist_ok=True)
    # สร้างโฟลเดอร์ annotations หากยังไม่มี
    os.makedirs(annotations_path, exist_ok=True)

    # วนลูปสร้างภาพ synthetic ตามจำนวนที่กำหนด
    for i in range(1, num_images + 1):
        try:
            # สุ่มเลือกภาพพื้นหลังและฟีเจอร์
            bg_path = random.choice(backgrounds)
            feature_path = random.choice(features)

            # โหลดภาพพื้นหลัง
            background = cv2.imread(bg_path)
            # โหลดภาพฟีเจอร์พร้อม alpha channel
            feature = cv2.imread(feature_path, cv2.IMREAD_UNCHANGED)

            # ตรวจสอบว่าโหลดภาพสำเร็จหรือไม่
            if background is None or feature is None:
                msg = f"❌ ไม่สามารถโหลดภาพ: {bg_path} หรือ {feature_path}\n"
                if log_callback: log_callback(msg)
                else: print(msg)
                continue

            # ตรวจจับพื้นที่น้ำในภาพพื้นหลัง
            water_mask = detect_water_area(background)
            # วางฟีเจอร์บนพื้นที่น้ำ
            placed_feature, x, y = place_feature_on_water(background, feature, water_mask)

            # ตรวจสอบว่าวางฟีเจอร์สำเร็จหรือไม่
            if placed_feature is None:
                msg = f"❌ ไม่พบตำแหน่งน้ำที่เหมาะสมสำหรับ {os.path.basename(bg_path)}\n"
                if log_callback: log_callback(msg)
                else: print(msg)
                continue

            # วางฟีเจอร์ลงบนภาพพื้นหลัง
            synthetic_image = overlay_feature(background, placed_feature, x, y)
            # สร้างชื่อไฟล์ภาพและ annotation
            image_name = f"synthetic_image_{i:03d}.jpg"
            annotation_name = f"synthetic_image_{i:03d}.txt"

            # ✅ ตรวจสอบว่าเขียนไฟล์ภาพสำเร็จหรือไม่
            saved = cv2.imwrite(os.path.join(output_path, image_name), synthetic_image)
            if not saved:
                msg = f"❌ ไม่สามารถบันทึกภาพ: {image_name}\n"
                if log_callback: log_callback(msg)
                else: print(msg)
                continue

            # หา bounding box จากฟีเจอร์ที่วางแล้ว
            rel_x, rel_y, rel_w, rel_h = get_true_bbox_from_alpha(placed_feature)
            # บันทึก annotation
            save_annotation(
                os.path.join(annotations_path, annotation_name),
                x + rel_x, y + rel_y, rel_w, rel_h, 0,  # x + rel_x = ตำแหน่ง x สุดท้าย
                background.shape[1], background.shape[0]  # ขนาดภาพพื้นหลัง
            )

            # แสดงข้อความว่าสร้างภาพสำเร็จ
            msg = f"✅ สร้างภาพ: {image_name}\n"
            if log_callback: log_callback(msg)
            else: print(msg)

        except Exception as e:
            # แสดงข้อความ error หากเกิดข้อผิดพลาด
            msg = f"❌ Error at image {i}: {e}\n"
            if log_callback: log_callback(msg)
            else: print(msg)

# หากเรียกใช้งานแบบสคริปต์ จะรันตรงนี้ (เช่น python generate_synthetic_functional.py)
if __name__ == "__main__":
    # เรียกใช้ฟังก์ชันหลักพร้อมกำหนดพารามิเตอร์
    generate_synthetic_dataset(
        backgrounds_path=r"C:\\Project\\backgrounds",  # โฟลเดอร์ภาพพื้นหลัง
        features_path=r"C:\\Project\\features",        # โฟลเดอร์ภาพฟีเจอร์
        output_path=r"C:\\Project\\synthetic_dataset", # โฟลเดอร์ภาพผลลัพธ์
        annotations_path=r"C:\\Project\\annotations",  # โฟลเดอร์ไฟล์ annotation
        num_images=200  # จำนวนภาพที่ต้องการสร้าง
    )