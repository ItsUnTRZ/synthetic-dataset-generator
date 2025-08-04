import os
from rembg import remove  # ใช้ลบพื้นหลังภาพด้วยโมเดล ONNX
from PIL import Image, ImageFilter  # ใช้จัดการและ post-process รูปภาพ

def post_process_image(image_path):
    """
    ทำ Post-processing เช่น blur และ sharpen บนภาพ เพื่อให้ภาพดูนุ่มนวลขึ้น
    ใช้ GaussianBlur และ SHARPEN จาก PIL
    """
    image = Image.open(image_path).convert("RGBA")  # เปิดภาพและแปลงเป็น RGBA
    image = image.filter(ImageFilter.GaussianBlur(radius=2))  # เบลอเล็กน้อย
    image = image.filter(ImageFilter.SHARPEN)  # ทำให้ภาพชัดขึ้นอีกครั้ง
    return image

def extract_features(input_folder, output_folder, prefix="feature", log_callback=None):
    """
    ลบพื้นหลังจาก raw images และบันทึกภาพ feature ที่ post-processed แล้ว
    โดยตั้งชื่อเป็น feature_001.png, feature_002.png, ...

    Parameters:
    - input_folder (str): โฟลเดอร์ที่เก็บภาพต้นฉบับ .jpg
    - output_folder (str): โฟลเดอร์ปลายทางสำหรับภาพที่ลบพื้นหลังแล้วและทำ post-process
    - prefix (str): คำนำหน้าสำหรับชื่อไฟล์ที่บันทึกผลลัพธ์
    - log_callback (function, optional): ฟังก์ชันสำหรับรับข้อความ log แบบเรียลไทม์ เช่น ในแอป Streamlit
      หากไม่ส่งเข้ามา จะใช้ print() แสดง log แทน
    """
    def log(msg):
        # ฟังก์ชันย่อยไว้ใช้ log โดยจะเลือกใช้ print หรือส่งไป UI
        if log_callback:
            log_callback(msg + "\n")
        else:
            print(msg)

    # สร้างโฟลเดอร์ output หากยังไม่มี
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    count = 1  # ตัวนับชื่อไฟล์
    for filename in sorted(os.listdir(input_folder)):
        if filename.lower().endswith(".jpg"):  # ตรวจเฉพาะไฟล์ .jpg
            input_path = os.path.join(input_folder, filename)
            output_filename = f"{prefix}_{count:03d}.png"  # เช่น feature_001.png
            output_path = os.path.join(output_folder, output_filename)
            temp_output_path = os.path.join(output_folder, f"temp_{output_filename}")

            try:
                # 🔍 ลบพื้นหลังจากภาพต้นฉบับด้วย rembg
                with open(input_path, "rb") as input_file:
                    input_data = input_file.read()
                    output_data = remove(
                        input_data,
                        alpha_matting=True,
                        alpha_matting_foreground_threshold=240,
                    )

                # 💾 บันทึกภาพชั่วคราวที่ลบพื้นหลังแล้ว
                with open(temp_output_path, "wb") as temp_output_file:
                    temp_output_file.write(output_data)

                # ✨ ทำ post-processing แล้วบันทึกผลลัพธ์สุดท้าย
                processed_image = post_process_image(temp_output_path)
                processed_image.save(output_path)

                # 🔄 ลบภาพชั่วคราวออก
                os.remove(temp_output_path)

                # ✅ log ว่าทำสำเร็จ
                log(f"✅ Processed: {filename} → {output_filename}")
                count += 1

            except Exception as e:
                # ❌ log เมื่อเกิดข้อผิดพลาด
                log(f"❌ Error processing {filename}: {e}")

# หากเรียกใช้งานแบบสคริปต์ จะรันตรงนี้ (เช่น python extract_features_functional.py)
if __name__ == "__main__":
    extract_features(
        input_folder=r"C:\\Project\\raw_images",
        output_folder=r"C:\\Project\\features"
    )
