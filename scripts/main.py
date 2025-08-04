from create_name_functional import rename_image_files
from extract_features_functional import extract_features
from generate_synthetic_functional import generate_synthetic_dataset

#  กำหนดโฟลเดอร์หลัก
BACKGROUND_FOLDER = r"C:\\Project\\backgrounds"
RAW_IMAGES_FOLDER = r"C:\\Project\\raw_images"
FEATURE_OUTPUT_FOLDER = r"C:\\Project\\features"
SYNTHETIC_OUTPUT_FOLDER = r"C:\\Project\\synthetic_dataset"
ANNOTATION_OUTPUT_FOLDER = r"C:\\Project\\annotations"

#  1. เปลี่ยนชื่อไฟล์ให้เป็นฟอร์แมต xxx_###.ext
rename_image_files(BACKGROUND_FOLDER, prefix="backgrounds")
rename_image_files(RAW_IMAGES_FOLDER, prefix="raw_image")

#  2. ลบพื้นหลังและสร้างฟีเจอร์จาก raw images
extract_features(
    input_folder=RAW_IMAGES_FOLDER,
    output_folder=FEATURE_OUTPUT_FOLDER
)

#  3. สร้าง synthetic dataset พร้อม annotation
generate_synthetic_dataset(
    backgrounds_path=BACKGROUND_FOLDER,
    features_path=FEATURE_OUTPUT_FOLDER,
    output_path=SYNTHETIC_OUTPUT_FOLDER,
    annotations_path=ANNOTATION_OUTPUT_FOLDER,
    num_images=200  # ปรับจำนวนตามต้องการ
)

print("\n เสร็จสมบูรณ์ ")
