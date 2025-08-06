# นำเข้า library สำหรับจัดการไฟล์และโฟลเดอร์
import os
# นำเข้า rembg library สำหรับลบพื้นหลังภาพด้วย AI model
from rembg import remove  # ใช้ลบพื้นหลังภาพด้วยโมเดล ONNX
# นำเข้า PIL library สำหรับจัดการและปรับแต่งภาพ
from PIL import Image, ImageFilter  # ใช้จัดการและ post-process รูปภาพ

def post_process_image(image_path):
    """
    ทำ Post-processing เช่น blur และ sharpen บนภาพ เพื่อให้ภาพดูนุ่มนวลขึ้น
    ใช้ GaussianBlur และ SHARPEN จาก PIL
    """
    # เปิดภาพจาก path ที่กำหนดและแปลงเป็นรูปแบบ RGBA (มี alpha channel)
    image = Image.open(image_path).convert("RGBA")  # เปิดภาพและแปลงเป็น RGBA
    # ใช้ Gaussian Blur เพื่อเบลอภาพเล็กน้อย (radius=2 = ความเบลอระดับต่ำ)
    image = image.filter(ImageFilter.GaussianBlur(radius=2))  # เบลอเล็กน้อย
    # ใช้ SHARPEN filter เพื่อทำให้ภาพชัดขึ้นอีกครั้งหลังเบลอ
    image = image.filter(ImageFilter.SHARPEN)  # ทำให้ภาพชัดขึ้นอีกครั้ง
    # ส่งคืนภาพที่ผ่าน post-processing แล้ว
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
        # ถ้ามี log_callback function ส่งมา ให้ใช้ log_callback
        if log_callback:
            log_callback(msg + "\n")
        # ถ้าไม่มี ให้ใช้ print() แทน
        else:
            print(msg)

    # สร้างโฟลเดอร์ output หากยังไม่มี
    # ตรวจสอบว่าโฟลเดอร์ output_folder มีอยู่หรือไม่
    if not os.path.exists(output_folder):
        # ถ้าไม่มี ให้สร้างโฟลเดอร์ใหม่
        os.makedirs(output_folder)

    count = 1  # ตัวนับชื่อไฟล์ เริ่มต้นที่ 1
    # วนลูปผ่านไฟล์ทั้งหมดในโฟลเดอร์ input_folder โดยเรียงลำดับตามชื่อไฟล์
    for filename in sorted(os.listdir(input_folder)):
        # ตรวจสอบเฉพาะไฟล์ที่มีนามสกุล .jpg (ไม่สนใจตัวพิมพ์ใหญ่-เล็ก)
        if filename.lower().endswith(".jpg"):  # ตรวจเฉพาะไฟล์ .jpg
            # สร้าง path เต็มของไฟล์ input
            input_path = os.path.join(input_folder, filename)
            # สร้างชื่อไฟล์ output ในรูปแบบ prefix_001.png
            output_filename = f"{prefix}_{count:03d}.png"  # เช่น feature_001.png
            # สร้าง path เต็มของไฟล์ output
            output_path = os.path.join(output_folder, output_filename)
            # สร้าง path ของไฟล์ชั่วคราว (ใช้ระหว่างการประมวลผล)
            temp_output_path = os.path.join(output_folder, f"temp_{output_filename}")

            try:
                # 🔍 ลบพื้นหลังจากภาพต้นฉบับด้วย rembg
                # เปิดไฟล์ input ในโหมด binary read
                with open(input_path, "rb") as input_file:
                    # อ่านข้อมูลทั้งหมดจากไฟล์ input
                    input_data = input_file.read()
                    # ใช้ rembg.remove() เพื่อลบพื้นหลัง
                    output_data = remove(
                        input_data,  # ข้อมูลภาพ input
                        alpha_matting=True,  # เปิดใช้ alpha matting เพื่อผลลัพธ์ที่ดีขึ้น
                        alpha_matting_foreground_threshold=240,  # กำหนด threshold สำหรับแยก foreground
                    )

                # 💾 บันทึกภาพชั่วคราวที่ลบพื้นหลังแล้ว
                # เปิดไฟล์ชั่วคราวในโหมด binary write
                with open(temp_output_path, "wb") as temp_output_file:
                    # เขียนข้อมูลภาพที่ลบพื้นหลังแล้วลงไฟล์ชั่วคราว
                    temp_output_file.write(output_data)

                # ✨ ทำ post-processing แล้วบันทึกผลลัพธ์สุดท้าย
                # เรียกใช้ฟังก์ชัน post_process_image() เพื่อปรับแต่งภาพ
                processed_image = post_process_image(temp_output_path)
                # บันทึกภาพที่ผ่าน post-processing แล้วลงไฟล์ output
                processed_image.save(output_path)

                # 🔄 ลบภาพชั่วคราวออก
                # ลบไฟล์ชั่วคราวเพื่อประหยัดพื้นที่
                os.remove(temp_output_path)

                # ✅ log ว่าทำสำเร็จ
                # แสดงข้อความว่าประมวลผลไฟล์ไหนสำเร็จ
                log(f"✅ Processed: {filename} → {output_filename}")
                # เพิ่มตัวนับเพื่อไปยังไฟล์ถัดไป
                count += 1

            except Exception as e:
                # ❌ log เมื่อเกิดข้อผิดพลาด
                # ถ้าเกิดข้อผิดพลาด ให้แสดงข้อความ error
                log(f"❌ Error processing {filename}: {e}")

# หากเรียกใช้งานแบบสคริปต์ จะรันตรงนี้ (เช่น python extract_features_functional.py)
# ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือไม่
if __name__ == "__main__":
    # เรียกใช้ฟังก์ชัน extract_features() พร้อมกำหนดพารามิเตอร์
    extract_features(
        input_folder=r"C:\\Project\\raw_images",  # โฟลเดอร์ที่เก็บภาพต้นฉบับ
        output_folder=r"C:\\Project\\features"    # โฟลเดอร์ที่เก็บภาพที่ลบพื้นหลังแล้ว
    )