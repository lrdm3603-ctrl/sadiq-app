import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد شكل صفحة الويب لتكون لذيذة وبسيطة
st.set_page_config(page_title="برنامج صَدِيق", page_icon="🤝", layout="centered")

st.title("🤝 برنامج صَدِيق")
st.subheader("مساعدك الوفي لتصنيف الألوان لدعم المصابين بعمى الألوان")
st.write("صفحة بسيطة ومجانية تماماً لمساعدتك؛ التقط صورة للغرض واعرف لونه فوراً.")

# 1. موسوعة وعجلة الألوان الكاملة والموزونة رياضياً لمنع تداخل الأبيض والرمادي
COLOR_WHEEL = {
    "أبيض صريح": (255, 255, 255), "أسود": (0, 0, 0),
    "كريمي / أوف وايت": (255, 253, 208), "بيج فاتح": (245, 245, 220), "بيج دافئ": (225, 198, 153),
    "رمادي فاتح": (200, 200, 200), "رمادي عادي": (128, 128, 128), "رمادي غامق (فحمي)": (70, 70, 70),
    "رمادي دافئ": (155, 150, 140), "رمادي بارد": (140, 150, 155),
    "أحمر فاتح": (255, 51, 51), "أحمر صريح": (255, 0, 0), "أحمر غامق (عنابي/ماروني)": (128, 0, 32),
    "وردي فاتح": (255, 192, 203), "وردي (بينك)": (255, 105, 180), "وردي غامق (فوشي)": (255, 20, 147),
    "برتقالي": (255, 165, 0), "برتقالي غامق": (255, 69, 0),
    "أسمر داكن": (65, 43, 21), "أسمر طبيعي": (115, 78, 48),
    "بني حنطي غامق": (160, 114, 82), "بني حنطي": (197, 140, 105), "بني حنطي فاتح": (224, 172, 105), "أبيض عاجي": (255, 224, 189),
    "أصفر فاتح": (255, 255, 153), "أصفر صريح": (255, 255, 0), "أصفر خردلي": (218, 165, 32),
    "أخضر فاتح (ليموني)": (144, 238, 144), "أخضر صريح": (0, 255, 0), "أخضر فستقي": (147, 197, 114), "أخضر زيتي / عسكري": (85, 107, 47), "أخضر غامق": (0, 100, 0),
    "تركوازي / فيروزي": (64, 224, 208), "سماوي / أزرق فاتح": (135, 206, 235), "أزرق صريح": (0, 0, 255), "كحلي": (0, 0, 128), "نيلي": (75, 0, 130),
    "بنفسجي فاتح (لافندر)": (230, 230, 250), "بنفسجي صريح": (128, 0, 128), "أرجواني غامق": (75, 0, 130)
}

def get_closest_color(r, g, b):
    if r < 20 and g < 20 and b < 20: return "إضاءة ضعيفة جداً"
    
    # حماية صارمة لمنع خلط الأحمر بالبني الحنطي بسبب الظلال
    if r > g + 25 and r > b + 25:
        red_wheel = {k: v for k, v in COLOR_WHEEL.items() if "أحمر" in k or "عنابي" in k or "وردي" in k or "برتقالي" in k}
        min_distance = float('inf')
        closest_name = "غير محدد"
        for color_name, color_rgb in red_wheel.items():
            cr, cg, cb = color_rgb
            distance = np.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
            if distance < min_distance:
                min_distance = distance
                closest_name = color_name
        if min_distance > 42: return f"تقريباً {closest_name}"
        return closest_name

    min_distance = float('inf')
    closest_name = "غير محدد"
    for color_name, color_rgb in COLOR_WHEEL.items():
        cr, cg, cb = color_rgb
        distance = np.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        if distance < min_distance:
            min_distance = distance
            closest_name = color_name
            
    if min_distance > 42 and closest_name not in ["أبيض صريح", "أسود", "إضاءة ضعيفة جداً"]:
        return f"تقريباً {closest_name}"
    return closest_name

def draw_arabic_text(img, text, position, text_color=(255, 255, 255), font_size=18):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    try: font = ImageFont.truetype("arial.ttf", font_size)
    except: font = ImageFont.load_default()
    draw.text(position, bidi_text, font=font, fill=text_color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# أداة فتح الكاميرا المدمجة في المتصفحات لصفحات الويب
img_file = st.camera_input("التقط صورة للشيء المراد معرفة لونه:")

if img_file is not None:
    bytes_data = img_file.read()
    cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    height, width, _ = cv_img.shape
    cx, cy = int(width / 2), int(height / 2)
    
    roi_small = cv_img[max(0, cy-5):min(height, cy+5), max(0, cx-5):min(width, cx+5)]
    pixel_color = cv2.mean(roi_small)[:3] if roi_small.size > 0 else cv_img[cy, cx]
    
    b, g, r = int(pixel_color[0]), int(pixel_color[1]), int(pixel_color[2])
    current_bgr_color = (b, g, r)
    
    color_name = get_closest_color(r, g, b)
    
    box_size = 100
    x1, y1 = cx - int(box_size/2), cy - int(box_size/2)
    x2, y2 = cx + int(box_size/2), cy + int(box_size/2)
    cv2.rectangle(cv_img, (x1, y1), (x2, y2), current_bgr_color, 4)
    cv2.rectangle(cv_img, (x1, y1 - 40), (x1 + 250, y1), (0, 0, 0), -1)
    cv_img = draw_arabic_text(cv_img, color_name, (x1 + 10, y1 - 35), font_size=20)
    
    st.image(cv_img, channels="BGR", caption="تم رصد اللون بسلام 🤝")
