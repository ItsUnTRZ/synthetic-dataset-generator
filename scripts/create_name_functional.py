import os

def rename_image_files(folder_path, prefix="backgrounds", extensions=None):
    """
    เปลี่ยนชื่อไฟล์ภาพในโฟลเดอร์ให้เป็นรูปแบบ prefix_001.jpg, prefix_002.jpg, ...
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.heic']  # นามสกุลไฟล์ภาพที่รองรับ

    count = 1
    for filename in sorted(os.listdir(folder_path)):
        name, ext = os.path.splitext(filename)
        if ext.lower() in extensions:
            # สร้างชื่อใหม่แบบมีเลข 3 หลัก เช่น backgrounds_001.jpg
            new_name = f"{prefix}_{count:03d}{ext.lower()}"
            src_path = os.path.join(folder_path, filename)
            dst_path = os.path.join(folder_path, new_name)

            # เปลี่ยนชื่อถ้าไม่ซ้ำ
            if not os.path.exists(dst_path):
                os.rename(src_path, dst_path)
                print(f"✅ Renamed: {filename} → {new_name}")
                count += 1
            else:
                print(f"⚠️ Skipped (duplicate name): {new_name}")

if __name__ == "__main__":
    # 🔄 เปลี่ยนชื่อภาพพื้นหลังให้เป็น backgrounds_001.jpg, ...
    rename_image_files(r"C:\\Project\\backgrounds", prefix="backgrounds")

    # 🔄 เปลี่ยนชื่อภาพ raw images ให้เป็น raw_image_001.jpg, ...
    rename_image_files(r"C:\\Project\\raw_images", prefix="raw_images")