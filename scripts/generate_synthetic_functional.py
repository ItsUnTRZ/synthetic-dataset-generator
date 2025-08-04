import os
import cv2
import numpy as np
import random

def detect_water_area(image):
    """
    ตรวจจับพื้นที่น้ำในภาพโดยใช้สี HSV และฟิลเตอร์ทาง Morphological
    คืนค่าเป็น mask (พื้นที่ที่ถือว่าเป็นน้ำ)
    """
    LOWER_BOUND = np.array([0, 0, 0])  # สีดำเข้มถึงน้ำเงินเข้ม (ค่าทดลองจากภาพจริง)
    UPPER_BOUND = np.array([110, 255, 220])

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, LOWER_BOUND, UPPER_BOUND)

    # ใช้ Morphological Filter เพื่อขจัด noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask

def place_feature_on_water(background, feature, water_mask):
    """
    วางภาพฟีเจอร์ลงบนพื้นหลัง โดยสุ่มตำแหน่งที่อยู่ในพื้นที่น้ำเท่านั้น
    คืนค่าภาพฟีเจอร์ที่วางแล้ว + ตำแหน่ง x, y
    """
    bg_height, bg_width, _ = background.shape
    fg_height, fg_width, _ = feature.shape

    # สุ่ม scale ของฟีเจอร์
    scale = np.random.uniform(0.4, 0.8)
    new_fg_width = int(fg_width * scale)
    new_fg_height = int(fg_height * scale)
    feature_resized = cv2.resize(feature, (new_fg_width, new_fg_height), interpolation=cv2.INTER_AREA)

    # หาพิกัดของพื้นที่น้ำใน mask
    water_coords = np.column_stack(np.where(water_mask > 0))
    if len(water_coords) == 0:
        return None, None, None

    # สุ่มพิกัดวางจนกว่าจะเจอที่เหมาะสม
    attempts = 0
    while attempts < 10000:
        y, x = random.choice(water_coords)
        if (x + new_fg_width <= bg_width and y + new_fg_height <= bg_height):
            region = water_mask[y:y + new_fg_height, x:x + new_fg_width]
            if np.count_nonzero(region) / (new_fg_width * new_fg_height) >= 0.5:
                break
        attempts += 1

    if attempts >= 10000:
        return None, None, None

    # สุ่มหมุน
    angle = np.random.uniform(0, 360)
    M = cv2.getRotationMatrix2D((new_fg_width // 2, new_fg_height // 2), angle, 1)
    rotated_feature = cv2.warpAffine(feature_resized, M, (new_fg_width, new_fg_height), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    return rotated_feature, x, y

def overlay_feature(background, feature, x, y):
    """
    วางฟีเจอร์ลงบนภาพพื้นหลัง โดยใช้ alpha channel
    """
    fg_height, fg_width, _ = feature.shape
    overlay = background.copy()
    for i in range(fg_height):
        for j in range(fg_width):
            if feature[i, j, 3] > 0:
                overlay[y + i, x + j] = feature[i, j, :3]
    return overlay

def get_true_bbox_from_alpha(feature_image):
    """
    หา bounding box ที่แท้จริงจาก alpha channel
    """
    alpha = feature_image[:, :, 3]
    coords = cv2.findNonZero(alpha)
    if coords is None:
        return 0, 0, feature_image.shape[1], feature_image.shape[0]
    x, y, w, h = cv2.boundingRect(coords)
    return x, y, w, h

def save_annotation(annotation_path, x, y, width, height, angle, bg_width, bg_height):
    """
    สร้าง annotation ไฟล์ในรูปแบบ YOLO (normalized)
    """
    x_center = (x + width / 2) / bg_width
    y_center = (y + height / 2) / bg_height
    norm_width = width / bg_width
    norm_height = height / bg_height

    with open(annotation_path, 'w') as f:
        f.write(f"0 {x_center} {y_center} {norm_width} {norm_height}\n")

def generate_synthetic_dataset(backgrounds_path, features_path, output_path, annotations_path, num_images, log_callback=None):
    """
    สร้างภาพ Synthetic โดยการสุ่มนำฟีเจอร์ไปวางบนพื้นที่น้ำของภาพพื้นหลัง
    และบันทึก annotation ประกอบ (แบบ YOLO format)
    """
    backgrounds = [os.path.join(backgrounds_path, f) for f in sorted(os.listdir(backgrounds_path)) if f.endswith('.jpg')]
    features = [os.path.join(features_path, f) for f in sorted(os.listdir(features_path)) if f.endswith('.png')]

    os.makedirs(output_path, exist_ok=True)
    os.makedirs(annotations_path, exist_ok=True)

    for i in range(1, num_images + 1):
        try:
            bg_path = random.choice(backgrounds)
            feature_path = random.choice(features)

            background = cv2.imread(bg_path)
            feature = cv2.imread(feature_path, cv2.IMREAD_UNCHANGED)

            if background is None or feature is None:
                msg = f"❌ ไม่สามารถโหลดภาพ: {bg_path} หรือ {feature_path}\n"
                if log_callback: log_callback(msg)
                else: print(msg)
                continue

            water_mask = detect_water_area(background)
            placed_feature, x, y = place_feature_on_water(background, feature, water_mask)

            if placed_feature is None:
                msg = f"❌ ไม่พบตำแหน่งน้ำที่เหมาะสมสำหรับ {os.path.basename(bg_path)}\n"
                if log_callback: log_callback(msg)
                else: print(msg)
                continue

            synthetic_image = overlay_feature(background, placed_feature, x, y)
            image_name = f"synthetic_image_{i:03d}.jpg"
            annotation_name = f"synthetic_image_{i:03d}.txt"

            # ✅ ตรวจสอบว่าเขียนไฟล์ภาพสำเร็จหรือไม่
            saved = cv2.imwrite(os.path.join(output_path, image_name), synthetic_image)
            if not saved:
                msg = f"❌ ไม่สามารถบันทึกภาพ: {image_name}\n"
                if log_callback: log_callback(msg)
                else: print(msg)
                continue

            rel_x, rel_y, rel_w, rel_h = get_true_bbox_from_alpha(placed_feature)
            save_annotation(
                os.path.join(annotations_path, annotation_name),
                x + rel_x, y + rel_y, rel_w, rel_h, 0,
                background.shape[1], background.shape[0]
            )

            msg = f"✅ สร้างภาพ: {image_name}\n"
            if log_callback: log_callback(msg)
            else: print(msg)

        except Exception as e:
            msg = f"❌ Error at image {i}: {e}\n"
            if log_callback: log_callback(msg)
            else: print(msg)

if __name__ == "__main__":
    generate_synthetic_dataset(
        backgrounds_path=r"C:\\Project\\backgrounds",
        features_path=r"C:\\Project\\features",
        output_path=r"C:\\Project\\synthetic_dataset",
        annotations_path=r"C:\\Project\\annotations",
        num_images=200
    )
