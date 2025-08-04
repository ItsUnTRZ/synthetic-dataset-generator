import os
from PIL import Image
import pillow_heif

# เปิด HEIC format ใน Pillow
pillow_heif.register_heif_opener()

# โฟลเดอร์ที่มีรูป HEIC ทั้งหมด (เปลี่ยนตรงนี้ให้ตรงกับของอั๋น)
folder_path = r"C:\Project\raw_images"

# วนลูปแปลงทุกไฟล์ .heic ในโฟลเดอร์
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".heic"):
        heic_path = os.path.join(folder_path, filename)
        jpg_filename = os.path.splitext(filename)[0] + ".jpg"
        jpg_path = os.path.join(folder_path, jpg_filename)

        try:
            image = Image.open(heic_path)
            image.save(jpg_path, "JPEG")
            os.remove(heic_path)  # ลบไฟล์ .heic เดิม
            print(f"✅ Converted: {filename} → {jpg_filename}")
        except Exception as e:
            print(f"❌ Error converting {filename}: {e}")
