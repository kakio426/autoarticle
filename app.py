import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from docx import Document
import io
import os
import requests
import datetime
import pandas as pd
import json
import uuid
from PIL import Image

# ==========================================
# 0. 초기 설정 및 디렉토리 관리
# ==========================================
st.set_page_config(layout="wide", page_title="AutoSchoolArticle: 학교 소식지 자동화")

ARCHIVE_DIR = "archive"
IMAGE_DIR = os.path.join(ARCHIVE_DIR, "images")
DATA_FILE = os.path.join(ARCHIVE_DIR, "data.csv")

for folder in [ARCHIVE_DIR, IMAGE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

if not os.path.exists(DATA_FILE):
    df_empty = pd.DataFrame(columns=["id", "date", "school", "grade", "event_name", "location", "tone", "keywords", "title", "content", "images"])
    df_empty.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 한글 폰트 설정
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
FONT_PATH = "NanumGothic-Regular.ttf"

def ensure_font():
    if not os.path.exists(FONT_PATH):
        try:
            response = requests.get(FONT_URL)
            with open(FONT_PATH, "wb") as f:
                f.write(response.content)
        except:
            pass

ensure_font()

# 디자인 테마 (컬러칩 미리보기용 데이터 포함)
THEMES = {
    "웜 & 플레이풀": {"main": (255, 140, 66), "sub": (255, 251, 240), "accent": (6, 214, 160), "hex": "#FF8C42"},
    "꿈꾸는 파랑": {"main": (0, 80, 150), "sub": (230, 240, 255), "accent": (0, 120, 215), "hex": "#005096"},
    "발랄한 노랑": {"main": (255, 180, 0), "sub": (255, 250, 230), "accent": (255, 140, 0), "hex": "#FFB400"},
    "산뜻한 민트": {"main": (0, 168, 107), "sub": (235, 250, 245), "accent": (0, 128, 90), "hex": "#00A86B"}
}

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
        [data-testid="stIcon"], i, svg { font-family: inherit !important; }
        header[data-testid="stHeader"] { background-color: transparent !important; }
        header[data-testid="stHeader"] * { color: transparent !important; }
        header[data-testid="stHeader"] svg { fill: var(--primary) !important; }

        /* 7. 몽글몽글 버튼 */
        .stButton>button {
            border-radius: var(--radius) !important;
            background-color: var(--primary) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 0px #E67E30 !important;
            padding: 0.6rem 2rem !important;
            font-weight: bold !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 0px #E67E30 !important;
        }

        /* 8. 카드 및 사이드바 (색상 복구 중요) */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            background-color: white !important;
            border: 1px solid #FFEBB3 !important;
            border-radius: var(--radius) !important;
            box-shadow: 0 8px 30px rgba(230, 126, 34, 0.03) !important;
        }

        /* 푸른색을 지우고 웜 베이지로 복구 */
        [data-testid="stSidebar"] {
            background-color: #FFF9E6 !important;
            border-right: 2px solid #FFEBB3 !important;
        }
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
def save_to_archive(data, uploaded_files):
    df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
    
    # 이미지 저장
    image_paths = []
    if uploaded_files:
        for file in uploaded_files:
            img_id = str(uuid.uuid4())
            # Handle both Streamlit UploadedFile and potential local paths
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
        "images": json.dumps(image_paths)
    }
    
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    return new_data  # ID 대신 데이터 전체를 반환하여 즉시 활용 가능하게 수정

# ==========================================
# 2. 로직: AI 기사 작성 (Gemini)
# ==========================================
def generate_article_gemini(api_key, topic_data):
    if not api_key:
        return "API 키가 필요합니다.", "사이드바에 API 키를 입력해주세요."
    
    try:
        genai.configure(api_key=api_key)
        # 최신 고성능 Flash 모델 설정 (Gemini 3 Flash Preview - 2025.12 출시)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        prompt = f"""
        당신은 {topic_data['school']}의 전문 학교 소식지 에디터입니다.
        다음 정보를 바탕으로 생동감 있고 따뜻한 어조의 {topic_data['tone']} 기사를 작성해주세요.
        
        학년: {topic_data['grade']}
        행사명: {topic_data['event_name']}
        장소: {topic_data['location']}
        일시: {topic_data['date']}
        주요 키워드: {topic_data['keywords']}
        
        요구사항:
        1. 제목은 매력적으로 뽑아주세요. (첫 줄에 '제목: ' 형식으로)
        2. 본문은 400~600자 내외로 작성하세요.
        3. 문단은 보기 좋게 나누고 이모지를 적절히 사용하여 친근감을 주세요.
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        # 파싱
        title = topic_data['event_name']
        content = text
        for line in text.split('\n'):
            if line.startswith("제목:") or line.startswith("##"):
                title = line.replace("제목:", "").replace("##", "").strip()
                content = text.replace(line, "").split('\n', 1)[-1].strip()
                break
        return title, content
    except Exception as e:
        return f"AI 생성 오류", str(e)

# ==========================================
# 3. 로직: PDF 생성 엔진
# ==========================================
class PDFEngine(FPDF):
    def __init__(self, theme_name, school_name):
        super().__init__()
        self.theme = THEMES[theme_name]
        self.school_name = school_name
        self.add_font("NanumGothic", "", FONT_PATH)
        # 상단 여백을 25mm로 설정하여 헤더(15mm)와 겹침 방지
        self.set_margins(10, 25, 10)
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        # 표지(1페이지)가 아닐 때만 헤더 표시
        if self.page_no() > 1:
            try:
                # 배경 상자 (항상 페이지 최상단 0~15mm 위치)
                self.set_fill_color(*self.theme["main"])
                self.rect(0, 0, 210, 15, 'F')
                
                self.set_font("NanumGothic", "", 10)
                self.set_text_color(255, 255, 255)
                header_text = f"{self.school_name} 소식지"
                self.text(12, 10, header_text)
            except: pass

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("NanumGothic", "", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'- {self.page_no()} -', align='C')

    def draw_cover(self):
        self.add_page()
        # 표지는 상단 여백을 무시하고 전체 배경색 칠함
        self.set_fill_color(*self.theme["sub"])
        self.rect(0, 0, 210, 297, 'F')
        
        self.set_y(100)
        self.set_font("NanumGothic", "", 42)
        self.set_text_color(*self.theme["main"])
        self.cell(190, 30, self.school_name, align='C', ln=True)
        
        self.set_y(130)
        self.set_font("NanumGothic", "", 22)
        self.set_text_color(70, 70, 70)
        now = datetime.datetime.now()
        self.cell(190, 20, f"{now.year}학년도 {now.month}월 뉴스레터", align='C', ln=True)
        
        self.set_draw_color(*self.theme["accent"])
        self.set_line_width(1.5)
        self.line(60, 155, 150, 155)

    def calculate_article_height(self, article):
        """기사의 높이를 합산하여 반환"""
        h = 0
        self.set_font("NanumGothic", "", 16)
        title_lines = len(self.multi_cell(190, 10, str(article['title']), split_only=True))
        h += (title_lines * 10) + 10
        
        imgs_raw = article.get('images', '[]')
        imgs = json.loads(imgs_raw) if isinstance(imgs_raw, str) else imgs_raw
        if imgs:
            cnt = len(imgs)
            if cnt == 1: h += 95
            elif cnt <= 4: h += 140
        
        self.set_font("NanumGothic", "", 11)
        content_lines = len(self.multi_cell(190, 7, str(article['content']), split_only=True))
        h += (content_lines * 7) + 25
        return h

    def add_article(self, article):
        """본문 길이에 따라 사진 크기를 미세 조정하는 스마트 스케일링 적용"""
        h_no_img = self.calculate_article_height({**article, 'images': '[]'})
        imgs_raw = article.get('images', '[]')
        imgs = json.loads(imgs_raw) if isinstance(imgs_raw, str) else imgs_raw
        
        # 텍스트가 너무 길면 이미지를 좀 더 작게 조절 (기본 1.0 -> 0.7)
        scaling = 1.0
        if h_no_img > 150: # 본문이 페이지의 절반 이상을 차지하면
            scaling = 0.8
        
        h_final = self.calculate_article_height(article)
        if self.get_y() + h_final > 275:
            self.add_page()
        
        # 제목
        self.set_x(10)
        self.set_font("NanumGothic", "", 16)
        self.set_text_color(*self.theme["main"])
        self.multi_cell(190, 10, str(article.get('title', '')))
        self.ln(3)
        
        # 이미지 그리드 (스케일링 적용)
        if imgs:
            self.render_image_grid(imgs, scaling=scaling)
            self.ln(5)

        # 본문
        self.set_x(10)
        self.set_font("NanumGothic", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(190, 7, str(article.get('content', '')))
        self.ln(15)

    def render_image_grid(self, imgs, scaling=1.0):
        cnt = len(imgs)
        try:
            if cnt == 1:
                w = 140 * scaling
                x = (210 - w) / 2
                self.image(imgs[0], x=x, w=w)
            elif cnt == 2:
                w = 92 * scaling
                curr_y = self.get_y()
                self.image(imgs[0], x=10, y=curr_y, w=w)
                self.image(imgs[1], x=108, y=curr_y, w=w)
                self.set_y(curr_y + (70 * scaling))
            elif cnt == 3:
                w_big = 110 * scaling
                w_small = 92 * scaling
                self.image(imgs[0], x=(210-w_big)/2, w=w_big)
                self.ln(5)
                curr_y = self.get_y()
                self.image(imgs[1], x=10, y=curr_y, w=w_small)
                self.image(imgs[2], x=108, y=curr_y, w=w_small)
                self.set_y(curr_y + (65 * scaling))
            else:
                w = 92 * scaling
                curr_y = self.get_y()
                self.image(imgs[0], x=10, y=curr_y, w=w)
                self.image(imgs[1], x=108, y=curr_y, w=w)
                self.ln(65 * scaling)
                new_y = self.get_y()
                self.image(imgs[2], x=10, y=new_y, w=w)
                self.image(imgs[3], x=108, y=new_y, w=w)
                self.set_y(new_y + (65 * scaling))
        except: pass

# ==========================================
# 4. 로직: Word 생성 엔진 (통합 본)
# ==========================================
def generate_docx_newsletter(articles, school_name, theme_name):
    from docx.shared import RGBColor
    theme = THEMES[theme_name]
    doc = Document()
    
    # 테마 색상 (제목용)
    main_color = RGBColor(*theme["main"])
    
    # 표지
    title = doc.add_heading(f'{school_name} 뉴스레터', 0)
    title.alignment = 1 
    
    now = datetime.datetime.now()
    p = doc.add_paragraph(f"{now.year}학년도 {now.month}월 소식")
    p.alignment = 1
    
    doc.add_page_break()

    for art in articles:
        # 기사 제목 (테마 색상 적용)
        h = doc.add_heading(str(art.get('title', '제목 없음')), level=1)
        for run in h.runs:
            run.font.color.rgb = main_color
        
        # 이미지 
        imgs_raw = art.get('images', '[]')
        imgs = json.loads(imgs_raw) if isinstance(imgs_raw, str) else imgs_raw
        if imgs:
            for img_p in imgs:
                try:
                    if os.path.exists(img_p):
                        doc.add_picture(img_p, width=doc.sections[0].page_width * 0.7)
                        doc.paragraphs[-1].alignment = 1
                except: pass
        
        # 본문
        doc.add_paragraph(str(art.get('content', '')))
        doc.add_page_break()
        
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

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
        
        try:
            df_archive = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
        except:
            df_archive = pd.DataFrame()

        st.write(f"총 {len(df_archive)}건의 기록이 있습니다.")
        
        tab_search, tab_batch = st.tabs(["🔍 개별 조회", "📰 뉴스레터 제작"])
        
        with tab_search:
            if not df_archive.empty:
                selection = st.selectbox("과거 기록 조회", 
                                       options=df_archive.index,
                                       format_func=lambda x: f"[{df_archive.iloc[x]['date']}] {df_archive.iloc[x]['event_name']}")
                if st.button("기록 보기", key="view_btn"):
                    st.session_state.current_view = df_archive.iloc[selection].to_dict()
            else:
                st.info("기록이 없습니다.")
        
        with tab_batch:
            if not df_archive.empty:
                selected_indices = st.multiselect("뉴스레터로 만들 기사 선택", 
                                            options=df_archive.index,
                                            format_func=lambda x: f"{df_archive.iloc[x]['event_name']}")
                
                if st.button("🚀 뉴스레터(PDF+Word) 통합 생성", use_container_width=True, type="primary"):
                    if selected_indices:
                        with st.spinner("두 가지 형식의 문서를 준비 중입니다..."):
                            articles = df_archive.iloc[selected_indices].to_dict('records')
                            
                            # 1. PDF 생성
                            pdf = PDFEngine(selected_theme, school_name)
                            pdf.draw_cover()
                            pdf.add_page()
                            for art in articles:
                                pdf.add_article(art)
                            pdf_data = bytes(pdf.output(dest='S'))
                            
                            # 2. Word 생성
                            docx_buffer = generate_docx_newsletter(articles, school_name, selected_theme)
                            
                            # 성공 후 세션에 저장하여 표시
                            st.session_state.ready_pdf = pdf_data
                            st.session_state.ready_docx = docx_buffer
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
                    if st.button("🔄 새로 만들기", use_container_width=True):
                        del st.session_state.ready_pdf
                        del st.session_state.ready_docx
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
                cols = st.columns(3)
                for idx, img in enumerate(img_files):
                    with cols[idx % 3]:
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
                title, content = generate_article_gemini(api_key, input_data)
                
                st.session_state.draft_title = title
                st.session_state.draft_content = content
                st.session_state.current_input_data = input_data
                # draft_images는 삭제 (저장 시점에 img_files를 직접 참조하도록 변경)
                st.success("AI 초안이 생성되었습니다! 아래에서 수정 후 보관하세요.")

    # 편집 섹션 (초안이 있을 때만 표시)
    if 'draft_title' in st.session_state:
        st.markdown("---")
        st.subheader("💡 AI 생성 기사 수정하기")
        with st.container(border=True):
            edited_title = st.text_input("📝 기사 제목 수정", value=st.session_state.draft_title)
            edited_content = st.text_area("✍️ 기사 본문 수정", value=st.session_state.draft_content, height=300)
            
            # 사진 미리보기 (수정 섹션 내)
            if st.session_state.get('draft_images'):
                st.write("📸 업로드된 사진")
                imgs = st.session_state.draft_images
                cols = st.columns(min(len(imgs), 4))
                for idx, img in enumerate(imgs[:4]):
                    cols[idx].image(img, use_container_width=True)

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("📥 최종 기사 보관하기", use_container_width=True, type="primary"):
                    final_data = st.session_state.current_input_data
                    final_data.update({"title": edited_title, "content": edited_content})
                    # 수정: 사용자가 체크박스로 선택한 사진들만 저장
                    saved_record = save_to_archive(final_data, selected_imgs) 
                    
                    st.toast("최종 기사가 보관소에 저장되었습니다!")
                    # 상태 초기화 및 즉시 보기 모드 전환
                    del st.session_state.draft_title
                    del st.session_state.draft_content
                    st.session_state.current_view = saved_record # 방금 저장한 기사를 즉시 표시
                    st.rerun()
            with col_btn2:
                if st.button("❌ 취소 및 삭제", use_container_width=True):
                    del st.session_state.draft_title
                    del st.session_state.draft_content
                    st.rerun()

    # 결과물 표시 및 개별 조회 화면
    if 'current_view' in st.session_state:
        st.markdown("---")
        st.subheader(f"🔍 기록 기록 조회: {st.session_state.current_view.get('event_name', '상세 내용')}")
        with st.container(border=True):
            v = st.session_state.current_view
            st.header(v['title'])
            st.write(f"**일시:** {v['date']} | **장소:** {v['location']} | **대상:** {v['grade']}")
            
            # 이미지 표시 로직 개선
            imgs_raw = v.get('images', '[]')
            imgs = json.loads(imgs_raw) if isinstance(imgs_raw, str) else imgs_raw
            if imgs:
                cols = st.columns(min(len(imgs), 3))
                for idx, img_p in enumerate(imgs[:3]):
                    try:
                        cols[idx].image(img_p, use_container_width=True)
                    except: pass
            
            st.write(v['content'])
            if st.button("조회창 닫기"):
                del st.session_state.current_view
                st.rerun()

if __name__ == "__main__":
    main()
