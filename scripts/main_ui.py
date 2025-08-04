import streamlit as st
import os
import random  # ✅ สำหรับสุ่มภาพตัวอย่าง
from PIL import Image
from pathlib import Path
from create_name_functional import rename_image_files  # ⬅️ ฟังก์ชัน rename สำหรับเปลี่ยนชื่อไฟล์ภาพ
from extract_features_functional import extract_features  # ⬅️ ฟังก์ชันแยกฟีเจอร์จากภาพ
from generate_synthetic_functional import generate_synthetic_dataset  # ⬅️ ฟังก์ชันสร้างชุดข้อมูลจำลอง
import io
import contextlib
import time

# === CONFIGURATION ===
RAW_IMAGE_DIR = r"C:\\Project\\raw_images"
BG_IMAGE_DIR = r"C:\\Project\\backgrounds"
FEATURE_DIR = r"C:\\Project\\features"
SYN_IMAGE_DIR = r"C:\\Project\\synthetic_dataset"
ANNOTATIONS_DIR = r"C:\\Project\\annotations"
VALID_EXT = (".jpg", ".jpeg", ".png")

os.makedirs(RAW_IMAGE_DIR, exist_ok=True)
os.makedirs(BG_IMAGE_DIR, exist_ok=True)
os.makedirs(FEATURE_DIR, exist_ok=True)
os.makedirs(SYN_IMAGE_DIR, exist_ok=True)
os.makedirs(ANNOTATIONS_DIR, exist_ok=True)

st.set_page_config(page_title="Synthetic Dataset Generator", layout="centered")
st.title("🧪 Synthetic Dataset Generator")

# === STEP 1: Upload Raw & Background Images ===
st.header("📤 Step 1: Upload Images")

# Upload Raw Images
st.subheader("🖼️ Upload Raw Images")
raw_files = st.file_uploader("Upload .jpg or .png files", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="raw")
if raw_files:
    for file in raw_files:
        file_path = os.path.join(RAW_IMAGE_DIR, file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())
    st.success(f"✅ Uploaded {len(raw_files)} raw image(s) to {RAW_IMAGE_DIR}")

if st.button("🔍 ดูภาพใน raw_images"):
    image_files = [f for f in os.listdir(RAW_IMAGE_DIR) if f.lower().endswith(VALID_EXT)]
    if image_files:
        st.text(f"พบ {len(image_files)} รูปใน raw_images")
        cols = st.columns(5)
        for i, img_name in enumerate(image_files):
            img_path = os.path.join(RAW_IMAGE_DIR, img_name)
            with cols[i % 5]:
                st.image(img_path, caption=img_name, use_container_width=True)
    else:
        st.warning("ยังไม่มีภาพใน raw_images")

if st.button("📂 เปิดโฟลเดอร์ raw_images ใน Windows"):
    os.startfile(RAW_IMAGE_DIR)

# Upload Background Images
st.subheader("🖼️ Upload Background Images")
bg_files = st.file_uploader("Upload .jpg or .png files", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="bg")
if bg_files:
    for file in bg_files:
        file_path = os.path.join(BG_IMAGE_DIR, file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())
    st.success(f"✅ Uploaded {len(bg_files)} background image(s) to {BG_IMAGE_DIR}")

if st.button("🔍 ดูภาพใน backgrounds"):
    image_files = [f for f in os.listdir(BG_IMAGE_DIR) if f.lower().endswith(VALID_EXT)]
    if image_files:
        st.text(f"พบ {len(image_files)} รูปใน backgrounds")
        cols = st.columns(5)
        for i, img_name in enumerate(image_files):
            img_path = os.path.join(BG_IMAGE_DIR, img_name)
            with cols[i % 5]:
                st.image(img_path, caption=img_name, use_container_width=True)
    else:
        st.warning("ยังไม่มีภาพใน backgrounds")

if st.button("📂 เปิดโฟลเดอร์ backgrounds ใน Windows"):
    os.startfile(BG_IMAGE_DIR)

# === STEP 2: Rename Files ===
st.header("✏️ Step 2: Rename Files")

col1, col2 = st.columns(2)
with col1:
    if st.button("⚙️ เปลี่ยนชื่อ Raw Images"):
        log_output = io.StringIO()
        with contextlib.redirect_stdout(log_output):
            rename_image_files(RAW_IMAGE_DIR, prefix="raw_images")
        st.success("✅ เปลี่ยนชื่อ Raw Images เสร็จแล้ว")
        st.text_area("📄 รายชื่อไฟล์หลังเปลี่ยน (raw_images)", value=log_output.getvalue(), height=200)
    if st.button("📂 เปิดโฟลเดอร์ raw_images หลัง rename"):
        os.startfile(RAW_IMAGE_DIR)

with col2:
    if st.button("⚙️ เปลี่ยนชื่อ Backgrounds"):
        log_output = io.StringIO()
        with contextlib.redirect_stdout(log_output):
            rename_image_files(BG_IMAGE_DIR, prefix="background")
        st.success("✅ เปลี่ยนชื่อ Backgrounds เสร็จแล้ว")
        st.text_area("📄 รายชื่อไฟล์หลังเปลี่ยน (backgrounds)", value=log_output.getvalue(), height=200)
    if st.button("📂 เปิดโฟลเดอร์ backgrounds หลัง rename"):
        os.startfile(BG_IMAGE_DIR)

# === STEP 3: Extract Features ===
st.header("✂️ Step 3: Extract Features (Remove Background)")

if "log_lines" not in st.session_state:
    st.session_state["log_lines"] = ""

status_placeholder = st.empty()
log_placeholder = st.empty()

def stream_log(msg):
    st.session_state["log_lines"] += msg
    log_placeholder.text_area("📄 Log จากการแยกฟีเจอร์ (สด)", value=st.session_state["log_lines"], height=300)

if st.button("⚙️ แยกฟีเจอร์จาก raw_images → features"):
    st.session_state["log_lines"] = ""
    with st.spinner("⏳ กำลังแยกฟีเจอร์จากภาพ... โปรดรอสักครู่"):
        extract_features(
            input_folder=RAW_IMAGE_DIR,
            output_folder=FEATURE_DIR,
            log_callback=stream_log
        )
    status_placeholder.success("✅ ดึงฟีเจอร์เสร็จเรียบร้อยแล้ว")

if st.button("🖼️ ดูภาพฟีเจอร์ใน features"):
    feature_files = [f for f in os.listdir(FEATURE_DIR) if f.lower().endswith(".png")]
    if feature_files:
        st.text(f"พบ {len(feature_files)} รูปใน features")
        cols = st.columns(5)
        for i, img_name in enumerate(feature_files):
            img_path = os.path.join(FEATURE_DIR, img_name)
            with cols[i % 5]:
                st.image(img_path, caption=img_name, use_container_width=True)
    else:
        st.warning("ยังไม่มีภาพใน features")

if st.button("📂 เปิดโฟลเดอร์ features ใน Windows"):
    os.startfile(FEATURE_DIR)

# === STEP 4: Generate Synthetic Dataset ===
st.header("🧠 Step 4: Generate Synthetic Dataset")

num_images = st.number_input("📌 จำนวนภาพจำลองที่ต้องการสร้าง", min_value=1, max_value=1000, value=200, step=1)
fixed_image_size = "640x640"
st.markdown(f"<span style='color: gray;'>📐 ขนาดภาพ: {fixed_image_size} (กำหนดไว้)</span>", unsafe_allow_html=True)

# เตรียมแสดง log
syn_log_placeholder = st.empty()
st.session_state.setdefault("syn_log", "")

def log_syn(msg):
    st.session_state["syn_log"] += msg
    syn_log_placeholder.text_area("📄 Log การสร้าง Synthetic Dataset", value=st.session_state["syn_log"], height=300)

if st.button("⚙️ สร้าง Synthetic Dataset"):
    st.session_state["syn_log"] = ""
    width, height = map(int, fixed_image_size.split("x"))
    with st.spinner("⏳ กำลังสร้างภาพจำลอง... โปรดรอสักครู่"):
        generate_synthetic_dataset(
            features_path=FEATURE_DIR,
            backgrounds_path=BG_IMAGE_DIR,
            output_path=SYN_IMAGE_DIR,
            annotations_path=ANNOTATIONS_DIR,
            num_images=num_images,
            log_callback=log_syn
        )
    st.success(f"✅ สร้างภาพจำลองเสร็จแล้ว {num_images} ภาพ")

if st.button("📂 เปิดโฟลเดอร์ synthetic_dataset"):
    os.startfile(SYN_IMAGE_DIR)

if st.button("📂 เปิดโฟลเดอร์ annotations"):
    os.startfile(ANNOTATIONS_DIR)

if st.button("🖼️ แสดงตัวอย่างภาพจำลองที่สร้างแล้ว"):
    image_files = [f for f in os.listdir(SYN_IMAGE_DIR) if f.lower().endswith(VALID_EXT)]
    if image_files:
        sample_images = random.sample(image_files, min(3, len(image_files)))
        st.text(f"🔎 ตัวอย่างภาพ {len(sample_images)} ภาพจาก synthetic_dataset")
        cols = st.columns(3)
        for i, img_name in enumerate(sample_images):
            img_path = os.path.join(SYN_IMAGE_DIR, img_name)
            with cols[i % 3]:
                st.image(img_path, caption=img_name, use_container_width=True)
    else:
        st.warning("ยังไม่มีภาพใน synthetic_dataset")
