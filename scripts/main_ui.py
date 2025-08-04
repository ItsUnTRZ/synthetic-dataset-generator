import streamlit as st
import os
import random
from PIL import Image
from pathlib import Path
from create_name_functional import rename_image_files
from extract_features_functional import extract_features
from generate_synthetic_functional import generate_synthetic_dataset
import io
import contextlib
import time

# === PAGE CONFIG === (ต้องอยู่ที่จุดเริ่มต้น)
st.set_page_config(
    page_title="Synthetic Dataset Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# === CUSTOM CSS ===
st.markdown("""
<style>
    /* Global Font Settings */
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #ffffff;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: #ffffff;
        border: none;
        box-shadow: 0 10px 30px rgba(26, 71, 42, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    .main-header h1 {
        color: #ffffff;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    .main-header p {
        color: #ffffff;
        font-size: 1.2rem;
        margin: 0;
        font-weight: 300;
    }
    
    /* Step Headers */
    .step-header {
        background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: #ffffff;
        border: none;
        box-shadow: 0 8px 25px rgba(26, 71, 42, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .step-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    .step-header h2 {
        color: #ffffff;
        font-weight: 700;
        margin: 0;
        font-size: 1.8rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Upload Sections */
    .upload-section {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #4CAF50;
        margin: 1.5rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(76, 175, 80, 0.2);
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        border-left-color: #66BB6A;
    }
    
    .upload-section h3 {
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    /* Success Box */
    .success-box {
        background: linear-gradient(135deg, #2E7D32 0%, #388E3C 100%);
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #ffffff;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(46, 125, 50, 0.4);
    }
    
    /* Warning Box */
    .warning-box {
        background: linear-gradient(135deg, #F57C00 0%, #FF8F00 100%);
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #ffffff;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(245, 124, 0, 0.4);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #ffffff;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(25, 118, 210, 0.4);
    }
    
    /* Stats Cards */
    .stats-card {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        margin: 1rem 0;
        border: 1px solid rgba(76, 175, 80, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stats-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4CAF50 0%, #66BB6A 100%);
    }
    
    .stats-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border-color: rgba(76, 175, 80, 0.4);
    }
    
    .stats-card h4 {
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .stats-card p {
        color: #e0e0e0;
        font-weight: 500;
        margin: 0;
        font-size: 1.2rem;
    }
    
    .stats-card strong {
        color: #4CAF50;
        font-weight: 800;
        font-size: 1.4rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
        color: #ffffff;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #66BB6A 0%, #4CAF50 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
    }
    
    /* File Uploader */
    .stFileUploader {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        border: 3px dashed #4CAF50;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #66BB6A;
        background: linear-gradient(135deg, #2f2f2f 0%, #242424 100%);
    }
    
    /* Number Input */
    .stNumberInput > div > div > input {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        border: 2px solid #4CAF50;
        border-radius: 10px;
        color: #ffffff;
        font-weight: 600;
        padding: 0.8rem;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #66BB6A;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }
    
    /* Text Area */
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
        border: 2px solid #4CAF50;
        border-radius: 10px;
        color: #ffffff;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        font-weight: 500;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #66BB6A;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4CAF50 0%, #66BB6A 100%);
        border-radius: 10px;
        height: 8px;
    }
    
    /* Spinner */
    .stSpinner > div {
        color: #4CAF50;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a472a 0%, #2d5a3d 100%);
    }
    
    /* Main Content */
    .main .block-container {
        background: rgba(26, 26, 26, 0.95);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        font-weight: 700;
    }
    
    /* Text */
    p, span, div {
        color: #e0e0e0;
    }
    
    /* Links */
    a {
        color: #4CAF50;
        text-decoration: none;
        font-weight: 600;
    }
    
    a:hover {
        color: #66BB6A;
        text-decoration: underline;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%);
        padding: 3rem;
        text-align: center;
        color: #ffffff;
        border-radius: 20px;
        margin-top: 3rem;
        box-shadow: 0 10px 30px rgba(26, 71, 42, 0.4);
    }
    
    /* Image Captions */
    .caption {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #66BB6A 0%, #81C784 100%);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.2rem;
        }
        
        .step-header h2 {
            font-size: 1.5rem;
        }
        
        .stats-card {
            padding: 1.2rem;
        }
        
        .main .block-container {
            margin: 0.5rem;
            padding: 1rem;
        }
    }
    
    /* Animation for loading states */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
    
    /* Glass morphism effect */
    .glass {
        background: rgba(26, 71, 42, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(76, 175, 80, 0.18);
    }
    
    /* Dark theme overrides */
    .stMarkdown {
        color: #e0e0e0;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #ffffff;
    }
    
    /* Streamlit specific dark theme */
    .stApp > header {
        background-color: #1a1a1a;
    }
    
    .stApp > footer {
        background-color: #1a1a1a;
    }
    
    /* Sidebar dark theme */
    .css-1d391kg, .css-1d391kg > div {
        background: linear-gradient(180deg, #1a472a 0%, #2d5a3d 100%);
    }
    
    /* Text input dark theme */
    .stTextInput > div > div > input {
        background: #2a2a2a;
        border: 2px solid #4CAF50;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #66BB6A;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }
    
    /* Selectbox dark theme */
    .stSelectbox > div > div > div {
        background: #2a2a2a;
        border: 2px solid #4CAF50;
        color: #ffffff;
    }
    
    /* Checkbox dark theme */
    .stCheckbox > div > div {
        background: #2a2a2a;
        border: 2px solid #4CAF50;
    }
    
    /* Radio dark theme */
    .stRadio > div > div {
        background: #2a2a2a;
        border: 2px solid #4CAF50;
    }
    
    /* Streamlit text elements */
    .stText, .stMarkdown, .stCaption {
        color: #ffffff !important;
    }
    
    /* Streamlit labels */
    .stLabel {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Streamlit help text */
    .stHelp {
        color: #e0e0e0 !important;
    }
    
    /* Streamlit sidebar text */
    .css-1d391kg .stMarkdown, .css-1d391kg .stText {
        color: #ffffff !important;
    }
    
    /* Streamlit file uploader text */
    .stFileUploader .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Streamlit number input label */
    .stNumberInput .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Streamlit text area label */
    .stTextArea .stMarkdown {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)



# === MAIN HEADER ===
st.markdown("""
<div class="main-header">
    <h1>🧪 Synthetic Dataset Generator</h1>
    <p>สร้างชุดข้อมูลจำลองสำหรับ Object Detection ด้วย AI</p>
</div>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### 📊 สถานะโปรเจกต์")
    
    # Count files in each directory
    raw_count = len([f for f in os.listdir(RAW_IMAGE_DIR) if f.lower().endswith(VALID_EXT)])
    bg_count = len([f for f in os.listdir(BG_IMAGE_DIR) if f.lower().endswith(VALID_EXT)])
    feature_count = len([f for f in os.listdir(FEATURE_DIR) if f.lower().endswith(".png")])
    syn_count = len([f for f in os.listdir(SYN_IMAGE_DIR) if f.lower().endswith(VALID_EXT)])
    anno_count = len([f for f in os.listdir(ANNOTATIONS_DIR) if f.lower().endswith(".txt")])
    
    # Raw Images Card
    st.markdown(f"""
    <div class="stats-card" style="cursor: pointer; margin: 0; padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid rgba(76, 175, 80, 0.2); transition: all 0.3s ease;">
        <h4 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1rem;">📁 Raw Images</h4>
        <p style="color: #e0e0e0; margin: 0; font-size: 1.1rem;"><strong style="color: #4CAF50; font-size: 1.3rem;">{raw_count}</strong> ไฟล์</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📁 Raw Images", key="open_raw_folder", help="คลิกเพื่อเปิดโฟลเดอร์ raw_images"):
        os.startfile(RAW_IMAGE_DIR)
    
    # Backgrounds Card
    st.markdown(f"""
    <div class="stats-card" style="cursor: pointer; margin: 0; padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid rgba(76, 175, 80, 0.2); transition: all 0.3s ease;">
        <h4 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1rem;">🖼️ Backgrounds</h4>
        <p style="color: #e0e0e0; margin: 0; font-size: 1.1rem;"><strong style="color: #4CAF50; font-size: 1.3rem;">{bg_count}</strong> ไฟล์</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🖼️ Backgrounds", key="open_bg_folder", help="คลิกเพื่อเปิดโฟลเดอร์ backgrounds"):
        os.startfile(BG_IMAGE_DIR)
    
    # Features Card
    st.markdown(f"""
    <div class="stats-card" style="cursor: pointer; margin: 0; padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid rgba(76, 175, 80, 0.2); transition: all 0.3s ease;">
        <h4 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1rem;">✂️ Features</h4>
        <p style="color: #e0e0e0; margin: 0; font-size: 1.1rem;"><strong style="color: #4CAF50; font-size: 1.3rem;">{feature_count}</strong> ไฟล์</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✂️ Features", key="open_features_folder", help="คลิกเพื่อเปิดโฟลเดอร์ features"):
        os.startfile(FEATURE_DIR)
    
    # Synthetic Card
    st.markdown(f"""
    <div class="stats-card" style="cursor: pointer; margin: 0; padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid rgba(76, 175, 80, 0.2); transition: all 0.3s ease;">
        <h4 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1rem;">🧠 Synthetic</h4>
        <p style="color: #e0e0e0; margin: 0; font-size: 1.1rem;"><strong style="color: #4CAF50; font-size: 1.3rem;">{syn_count}</strong> ไฟล์</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🧠 Synthetic", key="open_synthetic_folder", help="คลิกเพื่อเปิดโฟลเดอร์ synthetic_dataset"):
        os.startfile(SYN_IMAGE_DIR)
    
    # Annotations Card
    st.markdown(f"""
    <div class="stats-card" style="cursor: pointer; margin: 0; padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid rgba(76, 175, 80, 0.2); transition: all 0.3s ease;">
        <h4 style="color: #ffffff; margin: 0 0 0.5rem 0; font-size: 1rem;">📝 Annotations</h4>
        <p style="color: #e0e0e0; margin: 0; font-size: 1.1rem;"><strong style="color: #4CAF50; font-size: 1.3rem;">{anno_count}</strong> ไฟล์</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📝 Annotations", key="open_annotations_folder", help="คลิกเพื่อเปิดโฟลเดอร์ annotations"):
        os.startfile(ANNOTATIONS_DIR)
    
    st.markdown("---")
    st.markdown("### 🚀 การใช้งาน")
    st.markdown("""
    1. **อัปโหลดภาพ** - เพิ่มภาพต้นฉบับและพื้นหลัง
    2. **เปลี่ยนชื่อไฟล์** - จัดระเบียบชื่อไฟล์
    3. **แยกฟีเจอร์** - ลบพื้นหลังจากภาพ
    4. **สร้างชุดข้อมูล** - สร้างภาพจำลอง
    """)

# === STEP 1: Upload Images ===
st.markdown("""
<div class="step-header">
    <h2>📤 Step 1: อัปโหลดภาพ</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="upload-section">
        <h3>🖼️ อัปโหลดภาพต้นฉบับ</h3>
    </div>
    """, unsafe_allow_html=True)
    
    raw_files = st.file_uploader(
        "เลือกไฟล์ภาพ (.jpg, .jpeg, .png)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="raw",
        help="อัปโหลดภาพวัตถุที่ต้องการลบพื้นหลัง"
    )
    
    if raw_files:
        progress_bar = st.progress(0)
        for i, file in enumerate(raw_files):
            file_path = os.path.join(RAW_IMAGE_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
            progress_bar.progress((i + 1) / len(raw_files))
        
        st.markdown(f"""
        <div class="success-box">
            ✅ อัปโหลดสำเร็จ {len(raw_files)} ไฟล์
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔍 ดูภาพใน raw_images", key="view_raw"):
        image_files = [f for f in os.listdir(RAW_IMAGE_DIR) if f.lower().endswith(VALID_EXT)]
        if image_files:
            st.markdown(f"<h4>พบ {len(image_files)} รูปใน raw_images</h4>", unsafe_allow_html=True)
            cols = st.columns(min(5, len(image_files)))
            for i, img_name in enumerate(image_files):
                img_path = os.path.join(RAW_IMAGE_DIR, img_name)
                with cols[i % 5]:
                    try:
                        image = Image.open(img_path)
                        st.image(image, caption=img_name)
                    except Exception as e:
                        st.error(f"ไม่สามารถโหลดภาพ {img_name}: {str(e)}")
        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ ยังไม่มีภาพใน raw_images
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="upload-section">
        <h3>🖼️ อัปโหลดภาพพื้นหลัง</h3>
    </div>
    """, unsafe_allow_html=True)
    
    bg_files = st.file_uploader(
        "เลือกไฟล์ภาพ (.jpg, .jpeg, .png)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="bg",
        help="อัปโหลดภาพพื้นหลังสำหรับสร้างภาพจำลอง"
    )
    
    if bg_files:
        progress_bar = st.progress(0)
        for i, file in enumerate(bg_files):
            file_path = os.path.join(BG_IMAGE_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
            progress_bar.progress((i + 1) / len(bg_files))
        
        st.markdown(f"""
        <div class="success-box">
            ✅ อัปโหลดสำเร็จ {len(bg_files)} ไฟล์
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔍 ดูภาพใน backgrounds", key="view_bg"):
        image_files = [f for f in os.listdir(BG_IMAGE_DIR) if f.lower().endswith(VALID_EXT)]
        if image_files:
            st.markdown(f"<h4>พบ {len(image_files)} รูปใน backgrounds</h4>", unsafe_allow_html=True)
            cols = st.columns(min(5, len(image_files)))
            for i, img_name in enumerate(image_files):
                img_path = os.path.join(BG_IMAGE_DIR, img_name)
                with cols[i % 5]:
                    try:
                        image = Image.open(img_path)
                        st.image(image, caption=img_name)
                    except Exception as e:
                        st.error(f"ไม่สามารถโหลดภาพ {img_name}: {str(e)}")
        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ ยังไม่มีภาพใน backgrounds
            </div>
            """, unsafe_allow_html=True)

# === STEP 2: Rename Files ===
st.markdown("""
<div class="step-header">
    <h2>✏️ Step 2: เปลี่ยนชื่อไฟล์</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    💡 การเปลี่ยนชื่อไฟล์จะช่วยจัดระเบียบและทำให้การประมวลผลง่ายขึ้น
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📁 Raw Images")
    if st.button("⚙️ เปลี่ยนชื่อ Raw Images", key="rename_raw"):
        log_output = io.StringIO()
        with contextlib.redirect_stdout(log_output):
            rename_image_files(RAW_IMAGE_DIR, prefix="raw_images")
        st.markdown("""
        <div class="success-box">
            ✅ เปลี่ยนชื่อ Raw Images เสร็จแล้ว
        </div>
        """, unsafe_allow_html=True)
        st.text_area("📄 รายชื่อไฟล์หลังเปลี่ยน", value=log_output.getvalue(), height=150)

with col2:
    st.markdown("### 🖼️ Background Images")
    if st.button("⚙️ เปลี่ยนชื่อ Backgrounds", key="rename_bg"):
        log_output = io.StringIO()
        with contextlib.redirect_stdout(log_output):
            rename_image_files(BG_IMAGE_DIR, prefix="background")
        st.markdown("""
        <div class="success-box">
            ✅ เปลี่ยนชื่อ Backgrounds เสร็จแล้ว
        </div>
        """, unsafe_allow_html=True)
        st.text_area("📄 รายชื่อไฟล์หลังเปลี่ยน", value=log_output.getvalue(), height=150)

# === STEP 3: Extract Features ===
st.markdown("""
<div class="step-header">
    <h2>✂️ Step 3: แยกฟีเจอร์ (ลบพื้นหลัง)</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    🔍 ระบบจะลบพื้นหลังจากภาพต้นฉบับและสร้างภาพฟีเจอร์ที่พร้อมใช้งาน
</div>
""", unsafe_allow_html=True)

if "log_lines" not in st.session_state:
    st.session_state["log_lines"] = ""

status_placeholder = st.empty()
log_placeholder = st.empty()

def stream_log(msg):
    st.session_state["log_lines"] += msg
    log_placeholder.text_area("📄 Log จากการแยกฟีเจอร์", value=st.session_state["log_lines"], height=200)

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("⚙️ แยกฟีเจอร์จาก raw_images → features", key="extract_features"):
        st.session_state["log_lines"] = ""
        with st.spinner("⏳ กำลังแยกฟีเจอร์จากภาพ... โปรดรอสักครู่"):
            extract_features(
                input_folder=RAW_IMAGE_DIR,
                output_folder=FEATURE_DIR,
                log_callback=stream_log
            )
        status_placeholder.markdown("""
        <div class="success-box">
            ✅ ดึงฟีเจอร์เสร็จเรียบร้อยแล้ว
        </div>
        """, unsafe_allow_html=True)

with col2:
    if st.button("🔍 ดูภาพฟีเจอร์", key="view_features"):
        feature_files = [f for f in os.listdir(FEATURE_DIR) if f.lower().endswith(".png")]
        if feature_files:
            st.markdown(f"<h4>พบ {len(feature_files)} รูปใน features</h4>", unsafe_allow_html=True)
            cols = st.columns(min(3, len(feature_files)))
            for i, img_name in enumerate(feature_files):
                img_path = os.path.join(FEATURE_DIR, img_name)
                with cols[i % 3]:
                    try:
                        image = Image.open(img_path)
                        st.image(image, caption=img_name)
                    except Exception as e:
                        st.error(f"ไม่สามารถโหลดภาพ {img_name}: {str(e)}")
        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ ยังไม่มีภาพใน features
            </div>
            """, unsafe_allow_html=True)

# === STEP 4: Generate Synthetic Dataset ===
st.markdown("""
<div class="step-header">
    <h2>🧠 Step 4: สร้างชุดข้อมูลจำลอง</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    🎯 ระบบจะสร้างภาพจำลองโดยการวางฟีเจอร์บนพื้นหลังที่แตกต่างกัน พร้อมสร้าง annotation files
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    num_images = st.number_input(
        "📌 จำนวนภาพจำลองที่ต้องการสร้าง",
        min_value=1,
        max_value=1000,
        value=200,
        step=1,
        help="จำนวนภาพที่ต้องการสร้าง"
    )
    
    fixed_image_size = "640x640"
    st.markdown(f"""
    <div class="info-box">
        📐 ขนาดภาพ: {fixed_image_size} (กำหนดไว้)
    </div>
    """, unsafe_allow_html=True)

# เตรียมแสดง log
syn_log_placeholder = st.empty()
st.session_state.setdefault("syn_log", "")

def log_syn(msg):
    st.session_state["syn_log"] += msg
    syn_log_placeholder.text_area("📄 Log การสร้าง Synthetic Dataset", value=st.session_state["syn_log"], height=200)

with col2:
    if st.button("⚙️ สร้าง Synthetic Dataset", key="generate_synthetic"):
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
        st.markdown(f"""
        <div class="success-box">
            ✅ สร้างภาพจำลองเสร็จแล้ว {num_images} ภาพ
        </div>
        """, unsafe_allow_html=True)

# === RESULTS SECTION ===
st.markdown("""
<div class="step-header">
    <h2>📊 ผลลัพธ์</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📂 เปิดโฟลเดอร์ synthetic_dataset", key="open_syn"):
        os.startfile(SYN_IMAGE_DIR)

with col2:
    if st.button("📂 เปิดโฟลเดอร์ annotations", key="open_anno"):
        os.startfile(ANNOTATIONS_DIR)

with col3:
    if st.button("🖼️ แสดงตัวอย่างภาพจำลอง", key="view_synthetic"):
        image_files = [f for f in os.listdir(SYN_IMAGE_DIR) if f.lower().endswith(VALID_EXT)]
        if image_files:
            sample_images = random.sample(image_files, min(3, len(image_files)))
            st.markdown(f"<h4>🔎 ตัวอย่างภาพ {len(sample_images)} ภาพ</h4>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, img_name in enumerate(sample_images):
                img_path = os.path.join(SYN_IMAGE_DIR, img_name)
                with cols[i % 3]:
                    try:
                        image = Image.open(img_path)
                        st.image(image, caption=img_name)
                    except Exception as e:
                        st.error(f"ไม่สามารถโหลดภาพ {img_name}: {str(e)}")
        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ ยังไม่มีภาพใน synthetic_dataset
            </div>
            """, unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="font-weight: 800; color: white; margin-bottom: 1rem; font-size: 1.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🧪 Synthetic Dataset Generator</p>
    <p style="color: rgba(255,255,255,0.9); margin-bottom: 1rem; font-size: 1.1rem; font-weight: 300;">สร้างโดย AI สำหรับการวิจัย Object Detection</p>
    <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; font-weight: 400;">📧 หากมีปัญหา กรุณาติดต่อผู้พัฒนา</p>
</div>
""", unsafe_allow_html=True)
