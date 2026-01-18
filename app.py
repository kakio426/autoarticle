import streamlit as st
import google.generativeai as genai
import os
from engines.constants import THEMES
from engines.db_service import DatabaseService
from ui_logic import render_write_mode, render_publish_mode
from demo_tour import init_demo_mode, render_sidebar_demo_button, render_demo_guide_banner, is_demo_active

# Initial Setup / Migration
DATA_FILE = "article_archive.csv"
if os.path.exists(DATA_FILE):
    DatabaseService().migrate_from_csv(DATA_FILE)

def apply_custom_style():
    st.markdown("""
        <style>
        /* 1. 기본 배경 및 시스템 폰트 설정 */
        :root {
            --primary: #FF8C42;
            --bg: #FFFBF0;
            --text: #4A4A4A;
            --radius: 16px;
            --input-radius: 12px;
            --font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', 'sans-serif';
        }

        .stApp { 
            background-color: var(--bg) !important; 
            font-family: var(--font-family) !important;
        }

        /* 2. 텍스트 요소 통합 관리 */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, .stCaption, 
        .stButton button, .stCheckbox label span, [data-baseweb="select"] * {
            font-family: var(--font-family) !important;
            color: var(--text) !important;
        }

        /* 3. 입력창 찌꺼기 및 '옹졸한 박스' 제거 (근본 해결) */
        [data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] input {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            padding: 0 !important;
        }

        /* 4. 실제 보이는 박스 디자인 (깔끔한 unit) */
        .stTextInput > div > div, 
        .stTextArea > div > div, 
        .stDateInput > div > div {
            background-color: white !important;
            border: 1.5px solid #FFE0B3 !important;
            border-radius: var(--input-radius) !important;
            padding: 4px 12px !important;
        }
        
        .stSelectbox > div > div {
            background-color: white !important;
            border: 1.5px solid #FFE0B3 !important;
            border-radius: var(--input-radius) !important;
            padding: 0 !important; 
        }

        div[data-baseweb="select"] {
            min-height: 48px !important;
        }
        div[data-baseweb="select"] > div {
            padding: 0 12px !important;
            min-height: 48px !important;
            display: flex !important;
            align-items: center !important; 
        }

        /* 5. 포커스 시 강조 */
        .stTextInput > div > div:focus-within, 
        .stTextArea > div > div:focus-within, 
        .stSelectbox > div > div:focus-within,
        .stDateInput > div > div:focus-within {
            border-color: var(--primary) !important;
            border-width: 2px !important;
        }

        /* 6. 아이콘 및 헤더 */
        [data-testid="stExpander"] svg { font-family: 'Material Icons' !important; } 
        header[data-testid="stHeader"] { background-color: transparent !important; }
        
        /* 7. 버튼 */
        .stButton>button {
            border-radius: var(--radius) !important;
            background-color: var(--primary) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 0px #E67E30 !important;
            padding: 0.6rem 2rem !important;
            font-weight: bold !important;
            width: 100%; 
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 0px #E67E30 !important;
            background-color: var(--primary) !important;
            color: white !important;
        }

        /* 8. 사이드바 */
        [data-testid="stSidebar"] {
            background-color: #FFF9E6 !important;
            border-right: 2px solid #FFEBB3 !important;
        }
        [data-testid="stSidebar"] .stVerticalBlock {
            gap: 1rem !important;
        }

        /* 9. 전문 기사 포맷 (Compact) */
        .article-card {
            background: white;
            border-radius: 20px;
            padding: 35px;
            border: 1px solid #FFE0B3;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02);
            max-width: 850px; 
            margin: 0 auto;
        }
        .article-header {
            margin-bottom: 25px;
            border-bottom: 2px solid #FFF5E6;
            padding-bottom: 20px;
        }
        .article-title {
            font-size: 1.8rem !important; 
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
            height: 220px; 
            object-fit: cover;
            border-radius: 12px;
            border: 1px solid #FFE0B3;
        }
        .grid-1 { grid-template-columns: 1fr; }
        .grid-1 .img-item { height: 320px; } 
        .grid-2 { grid-template-columns: 1fr 1fr; }
        .grid-3 { grid-template-areas: "main main" "sub1 sub2"; }
        .grid-3 .img-item:first-child { grid-area: main; height: 300px; }
        .grid-4 { grid-template-columns: 1fr 1fr; }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(layout="wide", page_title="AI School Story", page_icon="🎨")
    
    # Initialize demo mode
    init_demo_mode()
    
    with st.sidebar:
        # Demo button at the top
        render_sidebar_demo_button()
        
        st.header("⚙️ 설정 (Settings)")
        api_key = st.text_input("Gemini API Key", type="password")
        
        # [Fix] Global API Configuration to prevent crash on PPT generation
        if api_key:
            try:
                genai.configure(api_key=api_key)
            except Exception as e:
                st.error(f"API 키 설정 오류: {e}")
        else:
            st.warning("⚠️ API 키를 입력해야 기능을 사용할 수 있습니다.")
            with st.expander("🔑 API 키 발급 방법 (클릭해서 펼치기)", expanded=False):
                st.markdown("""
                ### 📌 Gemini API 키란?
                이 시스템은 Google의 **Gemini AI**를 사용합니다.  
                API 키는 AI 서비스를 사용하기 위한 **비밀번호** 같은 것입니다.
                
                ---
                
                ### ✅ 발급 방법 (3분 소요)
                
                **1단계: Google AI Studio 접속**
                - 👉 [aistudio.google.com/apikey](https://aistudio.google.com/app/apikey) 클릭
                - 구글 계정으로 로그인
                
                **2단계: API 키 생성**
                - "Create API Key" 버튼 클릭
                - 프로젝트가 없으면 "Create API key in new project" 선택
                
                **3단계: 키 복사**
                - 생성된 키 (AIza로 시작)를 **복사**
                - 위의 입력창에 **붙여넣기**
                
                ---
                
                ### 💰 비용 안내
                - ✅ **완전 무료** (교육/개인 용도)
                - 📊 하루 1,500회까지 사용 가능
                - 🔒 키는 본인만 사용하세요
                """)

        school_name = st.text_input("학교명", value="서울디지털초등학교")
        
        st.write("🎨 디자인 테마 선택")
        theme_cols = st.columns([1, 4])
        selected_theme = st.selectbox("테마 목록", list(THEMES.keys()), label_visibility="collapsed")
        with theme_cols[0]:
            st.markdown(f'<div style="width:100%; height:30px; border-radius:5px; background:{THEMES[selected_theme]["hex"]}; border:1px solid #ddd;"></div>', unsafe_allow_html=True)
        with theme_cols[1]:
            st.caption(f"현재 테마: {selected_theme}")
            
        st.markdown("---")
        mode = st.radio("메뉴 선택", ["📝 기사 작성", "🗂️ 보관함 및 뉴스레터"])
        
        if st.checkbox("고급 설정"):
            if st.button("DB 리셋"):
                 # Simple Reset Logic
                 try:
                     os.remove("articles.db")
                     from engines.db_service import DatabaseService
                     DatabaseService() # Re-init
                     st.warning("데이터가 초기화되었습니다.")
                     st.rerun()
                 except: pass

    apply_custom_style()
    
    # Render demo guide banner at the top of main content
    render_demo_guide_banner()

    if mode == "📝 기사 작성":
        render_write_mode(api_key, school_name, selected_theme)
    else:
        render_publish_mode(school_name, selected_theme, api_key)

if __name__ == "__main__":
    main()

