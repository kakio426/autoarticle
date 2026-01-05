import streamlit as st
import google.generativeai as genai
import os
import json
import re
import uuid
import datetime
import pandas as pd
import io
from PIL import Image, ImageDraw, ImageFont

from engines.pdf_engine import PDFEngine
from engines.word_engine import WordEngine
from engines.ppt_engine import PPTEngine
from engines.rag_service import StyleRAGService
from engines.db_service import DatabaseService
from engines.constants import THEMES, FONT_PATH

# 설정값
DATA_FILE = "article_archive.csv"
IMAGE_DIR = "uploaded_images"

# 폴더 생성
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/NanumSquareRound.woff');
        
        :root {
            --primary: #FF8C42;
            --bg: #FFFBF0;
            --text: #4A4A4A;
            --radius: 16px;
            --input-radius: 12px;
        }

        /* 1. 기본 배경 */
        .stApp { background-color: var(--bg) !important; }

        /* 2. 텍스트 요소 통합 관리 */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, .stCaption, 
        .stButton button, .stCheckbox label span, [data-baseweb="select"] * {
            font-family: 'NanumSquareRound', sans-serif !important;
            color: var(--text) !important;
        }

        /* 3. 입력창 찌꺼기 및 '옹졸한 박스' 제거 (근본 해결) */
        /* [data-baseweb] 하위의 모든 입력 필드 잔상 제거 */
        [data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] input {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            padding: 0 !important;
        }

        /* 4. 실제 보이는 박스 디자인 (깔끔한 unit) */
        /* 일반 입력창 및 날짜 입력창: 내부 여백 필요 */
        .stTextInput > div > div, 
        .stTextArea > div > div, 
        .stDateInput > div > div {
            background-color: white !important;
            border: 1.5px solid #FFE0B3 !important;
            border-radius: var(--input-radius) !important;
            padding: 4px 12px !important;
        }
        
        /* 셀렉트박스 (참여 학년 등): 외부 패딩 제거 (잘림 방지) */
        .stSelectbox > div > div {
            background-color: white !important;
            border: 1.5px solid #FFE0B3 !important;
            border-radius: var(--input-radius) !important;
            padding: 0 !important; /* ★ 중요: 외부 패딩 제거 ★ */
        }

        /* 셀렉트박스 내부 텍스트 정렬 및 높이 확보 */
        div[data-baseweb="select"] {
            min-height: 48px !important;
        }
        div[data-baseweb="select"] > div {
            padding: 0 12px !important;
            min-height: 48px !important;
            display: flex !important;
            align-items: center !important; /* 수직 중앙 정렬 */
        }

        /* 5. 포커스 시 테두리 강조 */
        .stTextInput > div > div:focus-within, 
        .stTextArea > div > div:focus-within, 
        .stSelectbox > div > div:focus-within,
        .stDateInput > div > div:focus-within {
            border-color: var(--primary) !important;
            border-width: 2px !important;
        }

        /* 6. 아이콘 보호 및 헤더 클리닝 */
        /* [data-testid="stIcon"], i, svg { font-family: inherit !important; } <- 이 코드를 삭제하거나 아래처럼 수정 */
        [data-testid="stExpander"] svg { font-family: 'Material Icons' !important; } 
        header[data-testid="stHeader"] { background-color: transparent !important; }
        
        /* 7. 몽글몽글 버튼 */
        .stButton>button {
            border-radius: var(--radius) !important;
            background-color: var(--primary) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 0px #E67E30 !important;
            padding: 0.6rem 2rem !important;
            font-weight: bold !important;
            width: 100%; /* 버튼 너비 확보 */
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 0px #E67E30 !important;
            background-color: var(--primary) !important;
            color: white !important;
        }

        /* 8. 카드 및 사이드바 */
        [data-testid="stSidebar"] {
            background-color: #FFF9E6 !important;
            border-right: 2px solid #FFEBB3 !important;
        }
        /* 사이드바 내부 입력창 간격 확보 */
        [data-testid="stSidebar"] .stVerticalBlock {
            gap: 1rem !important;
        }

        /* 9. [NEW] 전문 기사 포맷 전용 스타일 (Compact) */
        .article-card {
            background: white;
            border-radius: 20px;
            padding: 35px;
            border: 1px solid #FFE0B3;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02);
            max-width: 850px; /* 너무 퍼지지 않게 제한 */
            margin: 0 auto;
        }
        .article-header {
            margin-bottom: 25px;
            border-bottom: 2px solid #FFF5E6;
            padding-bottom: 20px;
        }
        .article-title {
            font-size: 1.8rem !important; /* 살짝 축소 */
            font-weight: 800 !important;
            color: #E67E30 !important;
            margin-bottom: 12px !important;
            line-height: 1.3 !important;
        }
        .badge-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .badge {
            background: #FFF2E6;
            color: #FF8C42;
            padding: 4px 12px;
            border-radius: 50px;
            font-size: 0.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 5px;
            border: 1px solid #FFE4CC;
        }
        .article-content {
            font-size: 1.05rem !important;
            line-height: 1.7 !important;
            color: #4A4A4A !important;
            white-space: pre-wrap;
        }
        /* 이미지 그리드 시스템 (크기 최적화) */
        .img-grid {
            display: grid;
            gap: 12px;
            margin: 25px 0;
            max-width: 750px;
            margin-left: auto;
            margin-right: auto;
        }
        .img-item {
            width: 100%;
            height: 220px; /* 이미지 높이 축소 */
            object-fit: cover;
            border-radius: 12px;
            border: 1px solid #FFE0B3;
        }
        .grid-1 { grid-template-columns: 1fr; }
        .grid-1 .img-item { height: 320px; } /* 1장일 때도 너무 크지 않게 */
        .grid-2 { grid-template-columns: 1fr 1fr; }
        .grid-3 { grid-template-areas: "main main" "sub1 sub2"; }
        .grid-3 .img-item:first-child { grid-area: main; height: 300px; }
        .grid-4 { grid-template-columns: 1fr 1fr; }
        </style>
    """, unsafe_allow_html=True)

def show_stepper(step_idx):
    steps = ["1. 정보 입력", "2. AI 초안 생성", "3. 편집 및 보존", "4. 뉴스레터 발행"]
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        is_active = i == step_idx
        color = "#FF8C42" if is_active else "#EBD4BD"
        bg = "#FFF2E6" if is_active else "transparent"
        cols[i].markdown(f"""
            <div style="text-align:center; padding:10px; border-radius:16px; background:{bg}; border: 2px dashed {color if is_active else 'transparent'}">
                <span style="color:{color}; font-weight:{'bold' if is_active else 'normal'}">{step}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. 로직: 아카이브 관리
# ==========================================
# ==========================================
# 1. 로직: 아카이브 관리 (SQLite 기반)
# ==========================================
DB = DatabaseService()
# Initial migration
if os.path.exists(DATA_FILE):
    DB.migrate_from_csv(DATA_FILE)

def save_to_archive(data, uploaded_files):
    # 이미지 저장
    image_paths = []
    if uploaded_files:
        for file in uploaded_files:
            img_id = str(uuid.uuid4())
            ext = file.name.split('.')[-1] if hasattr(file, 'name') else 'png'
            file_path = os.path.join(IMAGE_DIR, f"{img_id}.{ext}")
            with open(file_path, "wb") as f:
                f.write(file.getbuffer() if hasattr(file, 'getbuffer') else file)
            image_paths.append(file_path)
    
    new_data = {
        "id": str(uuid.uuid4()),
        "date": data['date'],
        "school": data['school'],
        "grade": data['grade'],
        "event_name": data['event_name'],
        "location": data['location'],
        "tone": data['tone'],
        "keywords": data['keywords'],
        "title": data['title'],
        "content": data['content'],
        "images": json.dumps(image_paths),
        "hashtags": json.dumps(data.get('hashtags', []))
    }
    
    DB.save_article(new_data)
    return new_data

def update_archive(target_id, updated_title, updated_content):
    return DB.update_article(target_id, updated_title, updated_content)

# ==========================================
# 2. 로직: AI 기사 작성 (Gemini)
# ==========================================
# ==========================================
# 2. 로직: AI 기사 작성 (Gemini) + RAG Style
# ==========================================
def generate_article_gemini(api_key, topic_data, style_service=None):
    if not api_key:
        return "API 키가 필요합니다.", "사이드바에 API 키를 입력해주세요."
    
    try:
        genai.configure(api_key=api_key)
        # 최신 고성능 Flash 모델 설정 (Gemini 3 Flash Preview - 2025.12 출시)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # Style RAG Injection
        style_prompt = ""
        if style_service:
            # Simple query based on tone and event name
            query = f"{topic_data['tone']} {topic_data['event_name']}"
            examples = style_service.retrieve_style_examples(query)
            if examples:
                 style_prompt = "\n\n[학교별 맞춤 스타일 참고 (이전에 사용자가 수정한 내역)]:\n"
                 for i, ex in enumerate(examples):
                     style_prompt += f"예시 {i+1} (교정된 표현):\n{ex['corrected']}\n...\n"
                 style_prompt += "\n위의 예시 '교정된 표현'들에서 느껴지는 어투, 단어 선택, 문장 길이를 적극 반영해주세요.\n"

        prompt = f"""
        당신은 {topic_data['school']}의 전문 학교 소식지 에디터입니다.
        다음 정보를 바탕으로 생동감 있고 따뜻한 어조의 {topic_data['tone']} 기사를 작성해주세요.
        
        학년: {topic_data['grade']}
        행사명: {topic_data['event_name']}
        장소: {topic_data['location']}
        일시: {topic_data['date']}
        주요 키워드: {topic_data['keywords']}
        {style_prompt}
        요구사항:
        1. 제목은 매력적으로 뽑아주세요. (첫 줄에 '제목: ' 형식으로)
        2. 본문은 400~600자 내외로 작성하세요.
        3. 학교 소식에 어울리는 정중하면서도 따뜻한 어투를 유지하세요.
        4. 문단은 보기 좋게 나누고 이모지를 적절히 사용하여 친근감을 주세요.
        5. 기사 끝에 관련 해시태그 5개를 작성해주세요. (형식: #태그1 #태그2 ...)
        6. 선정적이거나 부정적인 표현은 배제하고 긍정적인 교육적 가치를 강조하세요.
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        # 파싱
        title = topic_data['event_name']
        content = text
        hashtags = []
        
        # 해시태그 추출 logic
        found_hashtags = re.findall(r"#(\w+)", text)
        if found_hashtags:
            hashtags = found_hashtags[:5]
            # 텍스트에서 해시태그 부분 제거 (본문에는 깔끔하게만 남기기 위해)
            # 보통 마지막에 있으므로 마지막 줄 근처 처리
            lines = text.split('\n')
            clean_lines = [l for l in lines if not all(word.startswith('#') for word in l.split())]
            content = '\n'.join(clean_lines).strip()

        for line in text.split('\n'):
            if line.startswith("제목:") or line.startswith("##"):
                title = line.replace("제목:", "").replace("##", "").strip()
                # 이미 content를 위에서 hashtag 제거하며 세팅했으므로 다시 체크
                temp_content = content.replace(line, "").strip()
                if temp_content: content = temp_content
                break
                
        return title, content, hashtags
    except Exception as e:
        return f"AI 생성 오류", str(e), []

def summarize_article_for_ppt(content):
    """
    긴 기사 내용을 PPT용 3~5줄 개조식(bullet points)으로 요약합니다.
    여러 모델을 순차적으로 시도하여 성공 확률을 높입니다.
    """
    models_to_try = ['gemini-3.0-flash-preview', 'gemini-2.0-flash-exp', 'gemini-1.5-flash']
    
    prompt = f"""
    다음 학교 소식 기사를 파워포인트 슬라이드에 넣을 수 있도록 3~5개의 핵심 문장으로 요약해주세요.
    
    [규칙]
    1. 각 문장은 명사형으로 끝내거나 '~함', '~임' 등으로 간결하게 끝내주세요.
    2. 이모지를 적절히 사용하여 시각적으로 지루하지 않게 해주세요.
    3. 전체 내용은 5줄을 넘지 않게 해주세요.
    4. 결과는 오직 요약된 문장들만 줄바꿈으로 구분하여 반환하세요. (기타 멘트 생략)
    
    [기사 내용]
    {content}
    """

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            # 텍스트를 줄 단위로 분리하여 리스트로 반환
            lines = [line.strip().replace('* ', '').replace('- ', '') for line in response.text.split('\n') if line.strip()]
            if lines: # 결과가 있으면 반환
                return lines
        except Exception as e:
            print(f"⚠️ [PPT AI 요약] 모델 {model_name} 실패: {str(e)}")
            continue # 다음 모델 시도

    # 모든 모델 실패 시
    print(f"❌ [PPT AI 요약] 모든 모델 시도 실패.")
    return [content[:100] + "... (내용이 길어 요약에 실패했습니다. 원문을 확인해주세요.)"]

# ==========================================
# 3. 로직: 카드뉴스 생성 엔진 (Pillow)
# ==========================================
class CardNewsEngine:
    def __init__(self, theme_name):
        self.theme = THEMES[theme_name]
        self.size = (1080, 1080)
        self.font_path = FONT_PATH
        
    def _get_font(self, size, bold=False):
        # Note: NanumGothic-Regular doesn't have a separate bold file in this setup, 
        # but we use sized fonts for hierarchy.
        return ImageFont.truetype(self.font_path, size)

    def _draw_wrapped_text(self, draw, text, position, font, max_width, fill, max_lines=2):
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
                if len(lines) >= max_lines: break
        
        if len(lines) < max_lines:
            lines.append(current_line)
        
        # If still too long, add ellipsis to the last line
        if len(lines) == max_lines:
            # Simple check if current_line was truncated or still too long
            last_line = lines[-1]
            bbox = draw.textbbox((0, 0), last_line, font=font)
            if bbox[2] - bbox[0] > max_width - 30:
                while last_line and draw.textbbox((0, 0), last_line + "...", font=font)[2] > max_width:
                    last_line = last_line[:-1]
                lines[-1] = last_line + "..."

        y = position[1]
        for line in lines:
            draw.text((position[0], int(y)), line, font=font, fill=fill)
            y += font.size * 1.4
        return int(y)

    def create_card(self, title, date, location, grade, hashtags, images):
        # 1. Canvas Setup (Clean White)
        canvas = Image.new("RGB", self.size, (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        main_rgb = self.theme["main"]
        accent_rgb = self.theme["accent"]
        
        # 2. Top Header (Profile Context)
        # 학년 배지 스타일
        badge_w = 120
        draw.rounded_rectangle((50, 50, 50 + badge_w, 100), radius=25, fill=main_rgb)
        draw.text((50 + 20, 60), grade if grade else "소식", font=self._get_font(22), fill=(255, 255, 255))
        
        # 학교/날짜 정보
        draw.text((50 + badge_w + 20, 55), "학교 소식지", font=self._get_font(24), fill=(30, 30, 30))
        draw.text((50 + badge_w + 20, 85), date, font=self._get_font(18), fill=(150, 150, 150))

        # 3. Main Title
        title_y = 140
        next_y = self._draw_wrapped_text(draw, title, (50, title_y), self._get_font(56), 980, (20, 20, 20), max_lines=2)
        
        # 4. Location Badge (이미지 바로 위에 배치)
        loc_y = next_y + 10
        if location:
            draw.text((50, loc_y), f"📍 {location}", font=self._get_font(28), fill=accent_rgb)
            img_y = loc_y + 60
        else:
            img_y = loc_y + 20

        # 5. Image Section
        img_w = 980 # 1000 -> 980 for better side margins
        img_h = 580 # 650 -> 580 to prevent bottom cutoff
        img_box = (50, int(img_y), 50 + img_w, int(img_y + img_h))
        
        # 박스 테두리 (Shadow 효과 느낌)
        draw.rectangle((48, int(img_y - 2), 52 + img_w, int(img_y + img_h + 2)), fill=(245, 245, 245))
        
        if images:
            self._render_image_grid(canvas, images, img_box)
            
        # 6. Hashtag Section
        # 이미지 바로 아래에 여백을 줄여서 배치
        tag_y = img_y + img_h + 30
        tag_str = " ".join([f"#{t}" for t in hashtags])
        self._draw_wrapped_text(draw, tag_str, (50, tag_y), self._get_font(34), 980, main_rgb, max_lines=2)
        
        # Footer Watermark (더 위로 올림)
        draw.text((820, 1010), "AI School Story", font=self._get_font(20), fill=(220, 220, 220))
        
        return canvas

    def _render_image_grid(self, canvas, image_paths, box):
        x, y, x2, y2 = box
        w, h = x2 - x, y2 - y
        count = len(image_paths)
        
        imgs = []
        for p in image_paths[:4]:
            try:
                # Handle both path strings and file-like objects
                if isinstance(p, str):
                    imgs.append(Image.open(p))
                else:
                    imgs.append(Image.open(io.BytesIO(p.getbuffer()) if hasattr(p, 'getbuffer') else p))
            except: continue
            
        if not imgs: return

        gap = 10
        if len(imgs) == 1:
            self._paste_cover(canvas, imgs[0], (x, y, w, h))
        elif len(imgs) == 2:
            half_w = (w - gap) // 2
            self._paste_cover(canvas, imgs[0], (x, y, half_w, h))
            self._paste_cover(canvas, imgs[1], (x + half_w + gap, y, half_w, h))
        elif len(imgs) == 3:
            big_w = (w * 2) // 3
            small_w = w - big_w - gap
            half_h = (h - gap) // 2
            self._paste_cover(canvas, imgs[0], (x, y, big_w, h))
            self._paste_cover(canvas, imgs[1], (x + big_w + gap, y, small_w, half_h))
            self._paste_cover(canvas, imgs[2], (x + big_w + gap, y + half_h + gap, small_w, half_h))
        else: # 4
            half_w = (w - gap) // 2
            half_h = (h - gap) // 2
            self._paste_cover(canvas, imgs[0], (x, y, half_w, half_h))
            self._paste_cover(canvas, imgs[1], (x + half_w + gap, y, half_w, half_h))
            self._paste_cover(canvas, imgs[2], (x, y + half_h + gap, half_w, half_h))
            self._paste_cover(canvas, imgs[3], (x + half_w + gap, y + half_h + gap, half_w, half_h))

    def _paste_cover(self, canvas, img, rect):
        rx, ry, rw, rh = rect
        iw, ih = img.size
        i_aspect = iw / ih
        r_aspect = rw / rh
        
        if i_aspect > r_aspect:
            new_h = int(rh)
            new_w = int(rh * i_aspect)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - rw) // 2
            img = img.crop((int(left), 0, int(left + rw), int(rh)))
        else:
            new_w = int(rw)
            new_h = int(rw / i_aspect)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            top = (new_h - rh) // 2
            img = img.crop((0, int(top), int(rw), int(top + rh)))
            
        canvas.paste(img, (int(rx), int(ry)))



# ==========================================
# 5. UI (Streamlit)
# ==========================================
def main():
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정 (Settings)")
        api_key = st.text_input("Gemini API Key", type="password")
        if not api_key:
            st.warning("⚠️ API 키를 입력해야 기능을 사용할 수 있습니다.")
            with st.expander("🔑 API 키 발급 및 비용 안내", expanded=False):
                st.markdown("""
                이 시스템은 Google의 **Gemini 3 Flash** AI 모델을 사용하여 기사와 카드뉴스를 생성합니다.
                
                **1. 어디서 가져오나요?**
                - [Google AI Studio](https://aistudio.google.com/app/apikey)에서 누구나 구글 계정으로 즉시 발급 가능합니다.
                
                **2. 비용이 드나요?**
                - **아니오, 무료입니다.** 개인 개발 및 교육 목적의 무료 티어를 사용하면 별도의 결제 없이 무료로 이용할 수 있습니다.
                
                **3. 얼마나 쓸 수 있나요? (한도)**
                - **분당 15회 / 하루 1,500회** 호출이 가능합니다. 
                - 학교 소식지를 수십 번 다시 생성하더라도 **전혀 걱정 없이** 넉넉하게 사용할 수 있는 양입니다.
                
                **4. 발급 방법**
                1. [AI Studio](https://aistudio.google.com/app/apikey) 접속 ➔ 'Create API key' 클릭
                2. 발급된 키를 복사하여 위 칸에 넣어주세요.
                """)
        else:
            st.success("✅ API 키가 설정되었습니다.")
            
        school_name = st.text_input("학교명", value="서울디지털초등학교")
        
        # 테마 미리보기 적용
        st.write("🎨 디자인 테마 선택")
        theme_cols = st.columns([1, 4])
        selected_theme = st.selectbox("테마 목록", list(THEMES.keys()), label_visibility="collapsed")
        with theme_cols[0]:
            st.markdown(f'<div style="width:100%; height:30px; border-radius:5px; background:{THEMES[selected_theme]["hex"]}; border:1px solid #ddd;"></div>', unsafe_allow_html=True)
        with theme_cols[1]:
            st.caption(f"현재 테마: {selected_theme}")
        
        st.markdown("---")
        st.header("📂 기록 보관소")
        
        history_list = DB.get_all_articles()
        df_archive = pd.DataFrame(history_list)

        st.write(f"총 {len(df_archive)}건의 기록이 있습니다.")
        
        tab_search, tab_batch = st.tabs(["🔍 개별 조회", "📰 뉴스레터 제작"])
        
        with tab_search:
            if not df_archive.empty:
                # Option format updated for SQLite dict results
                selection = st.selectbox("과거 기록 조회", 
                                       options=range(len(df_archive)),
                                       format_func=lambda x: f"[{df_archive.iloc[x]['date']}] {df_archive.iloc[x]['event_name']}")
                if st.button("기록 보기", key="view_btn"):
                    st.session_state.current_view = history_list[selection]
            else:
                st.info("기록이 없습니다.")
        
        with tab_batch:
            if not df_archive.empty:
                selected_indices = st.multiselect("뉴스레터로 만들 기사 선택 (신문형은 3~5개 권장)", 
                                            options=range(len(df_archive)),
                                            format_func=lambda x: f"{df_archive.iloc[x]['event_name']}")
                
                format_type = st.radio("📰 발행 스타일", ["Booklet (기사별 1페이지)", "Newspaper (A4 신문 1장)"], horizontal=True)
                
                use_ai_summary = st.checkbox("✨ PPT용 AI 자동 요약 사용 (긴 글을 핵심만 3줄 요약)", value=True)
                
                with st.expander("🔧 수동 생성을 위한 프롬프트 복사 (API 미사용 시)"):
                    if selected_indices:
                        copy_text = "다음 학교 소식들을 파워포인트 슬라이드용 내용을 요약해줘.\n\n"
                        for idx in selected_indices:
                            item = history_list[idx]
                            copy_text += f"[제목: {item['event_name']}]\n내용: {item['content']}\n\n"
                        st.code(copy_text, language="text")
                        st.caption("위 내용을 복사해서 ChatGPT나 Gemini 채팅창에 붙여넣어보세요!")
                    else:
                        st.info("먼저 기사를 선택해주세요.")

                if st.button("🚀 뉴스레터(PDF+Word+PPT) 통합 생성", use_container_width=True, type="primary"):
                    if not selected_indices:
                        st.warning("먼저 기사를 선택해주세요.")
                    else:
                        with st.spinner("문서를 제작하고 있습니다..."):
                            articles = [history_list[i] for i in selected_indices]
                            
                            # 1. PDF 생성
                            pdf = PDFEngine(selected_theme, school_name)
                            if format_type == "Newspaper (A4 신문 1장)":
                                pdf.add_newspaper_page(articles)
                            else:
                                pdf.draw_cover()
                                for art in articles:
                                    pdf.add_article(art, is_booklet=True)
                            pdf_data = bytes(pdf.output(dest='S'))
                            
                            # 2. Word 생성
                            word_engine = WordEngine(selected_theme, school_name)
                            docx_buffer = word_engine.generate(articles)
                            
                            # 3. PPT 생성 (AI 요약 포함)
                            ppt_articles = []
                            for art in articles:
                                art_copy = art.copy()
                                if use_ai_summary:
                                    summary_lines = summarize_article_for_ppt(art_copy.get('content', ''))
                                    art_copy['content'] = summary_lines
                                ppt_articles.append(art_copy)
                                
                            ppt_engine = PPTEngine(selected_theme, school_name)
                            ppt_buffer = ppt_engine.create_presentation(ppt_articles)
                            
                            # 세션 저장
                            st.session_state.ready_pdf = pdf_data
                            st.session_state.ready_docx = docx_buffer
                            st.session_state.ready_ppt = ppt_buffer
                            
                            st.success("문서 생성이 완료되었습니다! 아래에서 다운로드하세요.")

                # 생성된 파일이 있으면 다운로드 버튼 표시
                if 'ready_pdf' in st.session_state:
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.download_button("📥 PDF 다운로드", 
                                         data=st.session_state.ready_pdf, 
                                         file_name="newsletter.pdf", 
                                         mime="application/pdf", 
                                         use_container_width=True)
                    with col_dl2:
                        st.download_button("📥 Word 다운로드", 
                                         data=st.session_state.ready_docx, 
                                         file_name="newsletter.docx", 
                                         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                         use_container_width=True)
                    
                    if 'ready_ppt' in st.session_state:
                         st.download_button("📥 PPT(발표용) 다운로드",
                                          data=st.session_state.ready_ppt,
                                          file_name="presentation.pptx",
                                          mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                          use_container_width=True)

                    if st.button("🔄 새로 만들기", use_container_width=True):
                        del st.session_state.ready_pdf
                        del st.session_state.ready_docx
                        if 'ready_ppt' in st.session_state: del st.session_state.ready_ppt
                        st.rerun()
            else:
                st.info("선택할 기록이 없습니다.")

        st.markdown("---")
        if not df_archive.empty:
            csv = df_archive.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("💾 전체 CSV 데이터 다운로드", data=csv, file_name="article_archive.csv", mime="text/csv")

    apply_custom_style()
    
    # 프로세스 스텝 바
    current_step = 0
    if 'draft_title' in st.session_state: current_step = 2
    elif 'current_view' in st.session_state: current_step = 3
    elif 'ready_pdf' in st.session_state: current_step = 3
    
    show_stepper(current_step)

    st.title("🎨 아이보리(AI-Story)")
    st.markdown("##### 📰 AI 기반 학교 소식지 제작 시스템")
    st.markdown("---")

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("📝 행사 정보 입력")
        with st.container(border=True):
            grade = st.selectbox("📌 참여 학년", ["전교생", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "병설유치원", "기타"])
            event_name = st.text_input("📍 행사명", placeholder="예: 찾아가는 목공 체험")
            location = st.text_input("🏫 장소", placeholder="예: 학교 강당")
            event_date = st.date_input("📅 일시", datetime.date.today())
            tone = st.selectbox("🌈 기사 톤(분위기)", ["따뜻하고 감성적인", "활발하고 생동감 있는", "격조 있고 정중한", "간결하고 명확한"])
            keywords = st.text_area("✍️ 주요 활동 내용 (키워드)", placeholder="아이들이 나무 냄새를 맡으며 즐거워함, 뚝딱뚝딱 망치질 소리...", height=150)

        st.subheader("📸 사진 관리")
        with st.container(border=True):
            img_files = st.file_uploader("행사 사진들을 올려주세요 (여러 장 가능)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            
            selected_imgs = []
            if img_files:
                st.write("✅ 기사에 포함할 사진을 선택하세요")
                cols = st.columns(5) # 5개 컬럼으로 더 작게 표시
                for idx, img in enumerate(img_files):
                    with cols[idx % 5]:
                        st.image(img, use_container_width=True)
                        if st.checkbox(f"사진 {idx+1}", value=True, key=f"img_sel_{idx}"):
                            selected_imgs.append(img)
            else:
                st.info("사진을 올리면 기사와 함께 미리보기가 제공됩니다.")

    if st.button("✨ 기사 초안 생성하기", use_container_width=True, type="primary"):
        if not api_key:
            st.error("API 키가 없습니다. 사이드바에 키를 입력해주세요.")
        elif not event_name or not keywords:
            st.warning("행사명과 주요 내용을 입력해주세요.")
        else:
            with st.spinner("Gemini 3 Flash가 최신 기사를 작성 중입니다..."):
                input_data = {
                    "school": school_name,
                    "grade": grade,
                    "event_name": event_name,
                    "location": location,
                    "date": event_date.strftime("%Y/%m/%d"),
                    "tone": tone,
                    "keywords": keywords
                }
                # Initialize RAG Service if not ready
                if 'check_rag' not in st.session_state:
                     try:
                         # Use a local persistence directory
                         st.session_state.style_rag = StyleRAGService(persist_directory="./chroma_db_school")
                         st.session_state.check_rag = True
                     except:
                         st.session_state.style_rag = None

                title, content, hashtags = generate_article_gemini(api_key, input_data, st.session_state.get('style_rag'))
                
                st.session_state.draft_title = title
                st.session_state.draft_content = content
                st.session_state.draft_hashtags = hashtags
                st.session_state.current_input_data = input_data
                st.session_state.draft_images = selected_imgs
                st.success("AI 초안이 생성되었습니다! 아래에서 수정 후 카드뉴스를 만들어보세요.")

    # 편집 섹션 (초안이 있을 때만 표시)
    if 'draft_title' in st.session_state:
        st.markdown("---")
        st.subheader("💡 AI 생성 기사 수정하기")
        with st.container(border=True):
            edited_title = st.text_input("📝 기사 제목 수정", value=st.session_state.draft_title)
            edited_content = st.text_area("✍️ 기사 본문 수정", value=st.session_state.draft_content, height=300)
            
            # 사진 미리보기 (더 작고 컴팩트하게)
            if st.session_state.get('draft_images'):
                st.write("📸 업로드된 사진")
                imgs = st.session_state.draft_images
                cols = st.columns(5) # 5개 컬럼 고정으로 사진 크기 축소
                for idx, img in enumerate(imgs[:5]):
                    cols[idx % 5].image(img, use_container_width=True)
            
            edited_tags = st.text_input("🏷️ 해시태그 (공백으로 구분)", value=" ".join(st.session_state.get('draft_hashtags', [])))

            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn1:
                if st.button("📥 최종 기사 보관하기", use_container_width=True, type="primary"):
                    final_data = st.session_state.current_input_data
                    final_data.update({
                        "title": edited_title, 
                        "content": edited_content,
                        "hashtags": [t.strip() for t in edited_tags.split() if t.strip()]
                    })
                    # Learn Style from User Edits (RAG)
                    try:
                        rag = st.session_state.get('style_rag')
                        if rag and 'draft_content' in st.session_state:
                            original_ai_content = st.session_state.draft_content
                            # Only learn if meaningful edit happened (simplistic check)
                            if len(edited_content) > 10 and edited_content != original_ai_content:
                                 rag.learn_style(original_ai_content, edited_content, tags=st.session_state.current_input_data['tone'])
                                 st.toast("✨ 선생님의 스타일을 학습했어요!")
                    except Exception as e:
                        pass # Fail silently for user experience

                    save_to_archive(final_data, st.session_state.get('draft_images', []))
                    st.toast("저장되었습니다!")
                    del st.session_state.draft_title
                    st.rerun()
            
            with col_btn2:
                if st.button("🖼️ 카드뉴스 제작", use_container_width=True):
                    with st.spinner("요약 카드 생성 중..."):
                        engine = CardNewsEngine(selected_theme)
                        tags = [t.strip() for t in edited_tags.split() if t.strip()]
                        
                        temp_imgs = []
                        for img_file in st.session_state.get('draft_images', []):
                            tmp_path = f"tmp_{uuid.uuid4()}.png"
                            with open(tmp_path, "wb") as f:
                                f.write(img_file.getbuffer())
                            temp_imgs.append(tmp_path)
                        
                        # date 객체 또는 문자열 대응
                        input_info = st.session_state.current_input_data
                        raw_date = input_info['date']
                        if hasattr(raw_date, 'strftime'):
                            date_str = raw_date.strftime("%Y-%m-%d")
                        else:
                            date_str = str(raw_date)
                            
                        # 모든 메타데이터 포함하여 생성
                        summary_card = engine.create_card(
                            title=edited_title, 
                            date=date_str, 
                            location=input_info.get('location', ''),
                            grade=input_info.get('grade', ''),
                            hashtags=tags, 
                            images=temp_imgs
                        )
                            
                        for p in temp_imgs:
                            if os.path.exists(p): os.remove(p)
                            
                        st.session_state.preview_cards = [summary_card]
                        st.session_state.p_idx = 0
            
            with col_btn3:
                if st.button("❌ 취소 및 삭제", use_container_width=True):
                    del st.session_state.draft_title
                    st.rerun()

        # 카드뉴스 미리보기 UI (컬럼으로 크기 제한)
        if 'preview_cards' in st.session_state:
            st.markdown("---")
            st.subheader("🖼️ 카드뉴스 요약 카드")
            
            # 중앙 배치를 위해 3개 컬럼 사용 (좌우 여백 확보)
            _, col_mid, _ = st.columns([0.5, 1, 0.5])
            with col_mid:
                p_cards = st.session_state.preview_cards
                # Single Card Display
                st.image(p_cards[0], use_container_width=True)
                
                c_dl, c_close = st.columns(2)
                with c_dl:
                    img_io = io.BytesIO()
                    p_cards[0].save(img_io, format='PNG')
                    st.download_button("📥 PNG 다운로드", img_io.getvalue(), "card_news.png", "image/png", use_container_width=True)
                with c_close:
                    if st.button("✖️ 미리보기 닫기", use_container_width=True, key="close_preview_edit"):
                        del st.session_state.preview_cards
                        st.rerun()

    # 결과물 표시 및 개별 조회 화면
    if 'current_view' in st.session_state:
        st.markdown("---")
        v = st.session_state.current_view
        is_editing = st.session_state.get('is_editing', False)
        
        if is_editing:
            st.subheader(f"📝 기사 수정하기: {v.get('event_name', '')}")
            with st.container(border=True):
                new_title = st.text_input("📝 제목 수정", value=v['title'])
                st.write(f"**일시:** {v['date']} | **장소:** {v['location']} | **대상:** {v['grade']}")
                new_content = st.text_area("✍️ 본문 수정", value=v['content'], height=400)
                
                c1, c2 = st.columns(2)
                if c1.button("💾 변경사항 저장", use_container_width=True, type="primary"):
                    if update_archive(v['id'], new_title, new_content):
                        st.session_state.current_view['title'] = new_title
                        st.session_state.current_view['content'] = new_content
                        st.session_state.is_editing = False
                        st.success("수정사항이 저장되었습니다.")
                        st.rerun()
                if c2.button("🔙 취소", use_container_width=True):
                    st.session_state.is_editing = False
                    st.rerun()
        else:
            # 전문 매거진 스타일 레이아웃 (HTML/CSS 사용)
            import base64
            import textwrap

            def get_base64_img(path):
                try:
                    with open(path, "rb") as f:
                        data = base64.b64encode(f.read()).decode()
                        return f"data:image/png;base64,{data}"
                except: return ""

            imgs_raw = v.get('images', '[]')
            imgs = json.loads(imgs_raw) if isinstance(imgs_raw, str) else imgs_raw
            
            # 메타데이터 배지 HTML 생성
            badges_html = textwrap.dedent(f"""
                <div class="badge-container">
                    <div class="badge">📅 {v['date']}</div>
                    <div class="badge">🏫 {v['location']}</div>
                    <div class="badge">🎓 {v['grade']}</div>
                </div>
            """).strip()
            
            # 이미지 그리드 HTML 생성
            img_html = ""
            if imgs:
                img_count = min(len(imgs), 4)
                grid_class = f"grid-{img_count}"
                img_items_html = ""
                for i in range(img_count):
                    b64 = get_base64_img(imgs[i])
                    if b64:
                        img_items_html += f'<img src="{b64}" class="img-item">'
                
                img_html = f'<div class="img-grid {grid_class}">{img_items_html}</div>'

            # 기사 전체 렌더링 (인덴트 제거하여 마크다운 코드블록 방지)
            article_card_html = textwrap.dedent(f"""
                <div class="article-card">
                    <div class="article-header">
                        <div class="article-title">{v['title']}</div>
                        {badges_html}
                    </div>
                    {img_html}
                    <div class="article-content">{v['content']}</div>
                </div>
            """).strip()
            
            st.markdown(article_card_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- 카드뉴스 및 공유/다운로드 영역 ---
            with st.container(border=True):
                st.markdown("### 🛠️ 추가 도구")
                col_tool1, col_tool2, col_tool3 = st.columns(3)
                
                with col_tool1:
                    if st.button("🖼️ 이 기사로 카드뉴스 만들기", use_container_width=True, type="primary"):
                        with st.spinner("요약 카드 생성 중..."):
                            engine = CardNewsEngine(selected_theme)
                            # 안전한 해시태그 파싱
                            tags_raw = v.get('hashtags', '[]')
                            try:
                                tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
                            except:
                                tags = []
                            
                            if not isinstance(tags, list): tags = []
                            
                            # 모든 메타데이터 포함하여 생성
                            summary_card = engine.create_card(
                                title=v['title'], 
                                date=v['date'], 
                                location=v.get('location', ''),
                                grade=v.get('grade', ''),
                                hashtags=tags, 
                                images=imgs
                            )
                            
                            st.session_state.preview_cards = [summary_card]
                            st.session_state.p_idx = 0
                
                with col_tool2:
                    # 공유용 텍스트 (안전하게 해시태그 처리)
                    tags_raw_v = v.get('hashtags', '[]')
                    try:
                        tags_v = json.loads(tags_raw_v) if isinstance(tags_raw_v, str) else tags_raw_v
                    except:
                        tags_v = []
                    if not isinstance(tags_v, list): tags_v = []
                    
                    tag_line = ' '.join([f'#{t}' for t in tags_v])
                    share_text = f"[{v['school']}] {v['title']}\n📅 일시: {v['date']}\n🏫 장소: {v['location']}\n\n{v['content'][:150]}...\n\n{tag_line}"
                    st.text_area("🔗 공유용 텍스트 (복사 가능)", value=share_text, height=100)
                
                with col_tool3:
                    # 개별 기사 PDF 다운로드 (임시 지원)
                    pdf_single = PDFEngine(selected_theme, school_name)
                    pdf_single.add_page()
                    pdf_single.add_article(v)
                    pdf_bytes = bytes(pdf_single.output(dest='S'))
                    st.download_button("📥 기사 PDF 다운로드", pdf_bytes, f"article_{v['id'][:8]}.pdf", "application/pdf", use_container_width=True)

            # 카드뉴스 미리보기 UI (컬럼으로 크기 제한)
            if 'preview_cards' in st.session_state:
                st.markdown("---")
                st.subheader("🖼️ 생성된 카드뉴스")
                
                _, col_mid_v, _ = st.columns([0.5, 1, 0.5])
                with col_mid_v:
                    p_cards = st.session_state.preview_cards
                    st.image(p_cards[0], use_container_width=True)
                    
                    c_zip, c_cls = st.columns(2)
                    with c_zip:
                        img_io = io.BytesIO()
                        p_cards[0].save(img_io, format='PNG')
                        st.download_button("📥 PNG 다운로드", img_io.getvalue(), "card_news.png", "image/png", use_container_width=True)
                    with c_cls:
                        if st.button("✖️ 카드뉴스 닫기", use_container_width=True, key="close_preview_view"):
                            del st.session_state.preview_cards
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            col_ctrl1, col_ctrl2 = st.columns(2)
            if col_ctrl1.button("✏️ 기사 수정하기", use_container_width=True):
                st.session_state.is_editing = True
                st.rerun()
            if col_ctrl2.button("✖️ 조회창 닫기", use_container_width=True):
                del st.session_state.current_view
                if 'is_editing' in st.session_state: del st.session_state.is_editing
                if 'preview_cards' in st.session_state: del st.session_state.preview_cards
                st.rerun()

if __name__ == "__main__":
    main()
