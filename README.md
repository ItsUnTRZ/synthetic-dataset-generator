# โปรเจกต์การสร้าง Synthetic Dataset สำหรับ Object Detection

โปรเจกต์นี้เป็นระบบการสร้าง Synthetic Dataset สำหรับการฝึกฝนโมเดล Object Detection โดยเฉพาะสำหรับการตรวจจับวัตถุในน้ำ

## 🎯 วัตถุประสงค์

- สร้าง Synthetic Dataset จากภาพจริง
- ลบพื้นหลังจากภาพวัตถุ
- สร้างภาพใหม่โดยการวางวัตถุบนพื้นหลังที่แตกต่างกัน
- สร้าง Annotation files สำหรับการฝึกฝน YOLO

## 📁 โครงสร้างโปรเจกต์

```
Project/
├── scripts/                    # โค้ดหลัก
│   ├── main.py                # สคริปต์หลัก
│   ├── main_ui.py             # UI สำหรับ Streamlit
│   ├── extract_features_functional.py  # ลบพื้นหลัง
│   ├── generate_synthetic_functional.py # สร้าง synthetic images
│   └── create_name_functional.py       # จัดการชื่อไฟล์
├── raw_images/                # ภาพต้นฉบับ
├── backgrounds/               # ภาพพื้นหลัง
├── features/                  # ภาพที่ลบพื้นหลังแล้ว
├── synthetic_dataset/         # ภาพ synthetic ที่สร้างขึ้น
├── annotations/               # annotation files
├── models/                    # โมเดลที่ฝึกฝนแล้ว
└── augmented_dataset/         # dataset ที่ augment แล้ว
```

## 🚀 การติดตั้ง

1. **Clone repository**
```bash
git clone <your-repository-url>
cd Project
```

2. **สร้าง Virtual Environment**
```bash
python -m venv .venv
```

3. **เปิดใช้งาน Virtual Environment**
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

4. **ติดตั้ง Dependencies**
```bash
pip install -r requirements.txt
```

## 📖 การใช้งาน

### วิธีที่ 1: ใช้สคริปต์หลัก
```bash
python scripts/main.py
```

### วิธีที่ 2: ใช้ UI (Streamlit)
```bash
streamlit run scripts/main_ui.py
```

### วิธีที่ 3: ใช้แต่ละฟังก์ชันแยกกัน

#### 1. เปลี่ยนชื่อไฟล์
```python
from scripts.create_name_functional import rename_image_files

rename_image_files("path/to/folder", prefix="backgrounds")
```

#### 2. ลบพื้นหลัง
```python
from scripts.extract_features_functional import extract_features

extract_features(
    input_folder="path/to/raw_images",
    output_folder="path/to/features"
)
```

#### 3. สร้าง Synthetic Dataset
```python
from scripts.generate_synthetic_functional import generate_synthetic_dataset

generate_synthetic_dataset(
    backgrounds_path="path/to/backgrounds",
    features_path="path/to/features",
    output_path="path/to/synthetic_dataset",
    annotations_path="path/to/annotations",
    num_images=200
)
```

## 🔧 การตั้งค่า

แก้ไขพาธใน `scripts/main.py` ให้ตรงกับโครงสร้างโฟลเดอร์ของคุณ:

```python
BACKGROUND_FOLDER = "path/to/backgrounds"
RAW_IMAGES_FOLDER = "path/to/raw_images"
FEATURE_OUTPUT_FOLDER = "path/to/features"
SYNTHETIC_OUTPUT_FOLDER = "path/to/synthetic_dataset"
ANNOTATION_OUTPUT_FOLDER = "path/to/annotations"
```

## 📊 ผลลัพธ์

โปรเจกต์จะสร้าง:
- **Features**: ภาพที่ลบพื้นหลังแล้ว
- **Synthetic Images**: ภาพใหม่ที่สร้างขึ้น
- **Annotations**: ไฟล์ annotation ในรูปแบบ YOLO
- **Models**: โมเดลที่ฝึกฝนแล้ว (ถ้ามี)

## 🤝 การมีส่วนร่วม

1. Fork โปรเจกต์
2. สร้าง Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit การเปลี่ยนแปลง (`git commit -m 'Add some AmazingFeature'`)
4. Push ไปยัง Branch (`git push origin feature/AmazingFeature`)
5. เปิด Pull Request

## 📝 License

โปรเจกต์นี้อยู่ภายใต้ MIT License - ดูไฟล์ [LICENSE](LICENSE) สำหรับรายละเอียด

## 📞 ติดต่อ

หากมีคำถามหรือข้อเสนอแนะ กรุณาสร้าง Issue ใน GitHub repository

---

**หมายเหตุ**: โปรเจกต์นี้ถูกออกแบบสำหรับการวิจัยและพัฒนาระบบ Object Detection โดยเฉพาะสำหรับการตรวจจับวัตถุในน้ำ 