import streamlit as st
import google.generativeai as genai
import os
import json
import re
import uuid
import datetime
import pandas as pd
import io
import textwrap
import base64
from PIL import Image

from engines.pdf_engine import PDFEngine
from engines.word_engine import WordEngine
from engines.ppt_engine import PPTEngine
from engines.rag_service import StyleRAGService
from engines.db_service import DatabaseService
from engines.constants import THEMES
from engines.card_engine import CardNewsEngine
from engines.ai_service import generate_article_gemini, summarize_article_for_ppt
from engines.utils import save_article_with_images, IMAGE_DIR

# Database Service Instance (Singleton-like usage)
DB = DatabaseService()

def render_write_mode(api_key, school_name, selected_theme):
    """
    Renders the Article Writing Mode (Form -> Draft -> Edit).
    """
    # Initialize RAG if needed
    if 'check_rag' not in st.session_state:
            try:
                st.session_state.style_rag = StyleRAGService(persist_directory="./chroma_db_school")
                st.session_state.check_rag = True
            except:
                st.session_state.style_rag = None

    # Stepper Logic
    current_step = 0
    if 'draft_title' in st.session_state: current_step = 2
    
    # Custom Stepper UI
    steps = ["1. 정보 입력", "2. AI 초안 생성", "3. 편집 및 보존"]
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        is_active = i == current_step
        color = "#FF8C42" if is_active else "#EBD4BD"
        bg = "#FFF2E6" if is_active else "transparent"
        cols[i].markdown(f"""
            <div style="text-align:center; padding:10px; border-radius:16px; background:{bg}; border: 2px dashed {color if is_active else 'transparent'}">
                <span style="color:{color}; font-weight:{'bold' if is_active else 'normal'}">{step}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.title("📝 새로운 학교 소식 작성")
    
    # Input Section
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("📝 행사 정보 입력")
        with st.container(border=True):
            grade = st.selectbox("📌 참여 학년", ["전교생", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "병설유치원", "기타"], key="w_grade")
            event_name = st.text_input("📍 행사명", placeholder="예: 찾아가는 목공 체험", key="w_name")
            location = st.text_input("🏫 장소", placeholder="예: 학교 강당", key="w_loc")
            event_date = st.date_input("📅 일시", datetime.date.today(), key="w_date")
            tone = st.selectbox("🌈 기사 톤(분위기)", ["따뜻하고 감성적인", "활발하고 생동감 있는", "격조 있고 정중한", "간결하고 명확한"], key="w_tone")
            keywords = st.text_area("✍️ 주요 활동 내용 (키워드)", placeholder="아이들이 나무 냄새를 맡으며 즐거워함, 뚝딱뚝딱 망치질 소리...", height=150, key="w_key")

    with col2:
        st.subheader("📸 사진 관리")
        with st.container(border=True):
            img_files = st.file_uploader("행사 사진들을 올려주세요 (여러 장 가능)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, key="w_imgs")
            
            selected_imgs = []
            if img_files:
                st.write("✅ 기사에 포함할 사진을 선택하세요")
                cols = st.columns(3) # Compact view
                for idx, img in enumerate(img_files):
                    with cols[idx % 3]:
                        st.image(img, use_container_width=True)
                        if st.checkbox(f"선택 {idx+1}", value=True, key=f"img_sel_{idx}"):
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
                
                title, content, hashtags = generate_article_gemini(api_key, input_data, st.session_state.get('style_rag'))
                
                st.session_state.draft_title = title
                st.session_state.draft_content = content
                st.session_state.draft_hashtags = hashtags
                st.session_state.current_input_data = input_data
                st.session_state.draft_images = selected_imgs
                st.success("AI 초안이 생성되었습니다! 아래에서 수정 후 카드뉴스를 만들어보세요.")
                st.rerun()

    # Draft Edit Section
    if 'draft_title' in st.session_state:
        st.markdown("---")
        st.subheader("💡 AI 생성 기사 수정하기")
        with st.container(border=True):
            edited_title = st.text_input("📝 기사 제목 수정", value=st.session_state.draft_title, key="edt_title")
            edited_content = st.text_area("✍️ 기사 본문 수정", value=st.session_state.draft_content, height=300, key="edt_content")
            
            if st.session_state.get('draft_images'):
                st.write("📸 업로드된 사진")
                imgs = st.session_state.draft_images
                cols = st.columns(6) 
                for idx, img in enumerate(imgs[:6]):
                    cols[idx % 6].image(img, use_container_width=True)
            
            edited_tags = st.text_input("🏷️ 해시태그 (공백으로 구분)", value=" ".join(st.session_state.get('draft_hashtags', [])), key="edt_tags")

            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn1:
                if st.button("📥 최종 기사 보관하기", use_container_width=True, type="primary"):
                    final_data = st.session_state.current_input_data
                    final_data.update({
                        "title": edited_title, 
                        "content": edited_content,
                        "hashtags": [t.strip() for t in edited_tags.split() if t.strip()]
                    })
                    
                    # RAG Learning (Simplified)
                    try:
                        rag = st.session_state.get('style_rag')
                        if rag and 'draft_content' in st.session_state:
                            original = st.session_state.draft_content
                            if len(edited_content) > 10 and edited_content != original:
                                 rag.learn_style(original, edited_content, tags=st.session_state.current_input_data['tone'])
                    except: pass

                    save_article_with_images(DB, final_data, st.session_state.get('draft_images', []))
                    st.toast("저장되었습니다! '발행' 메뉴에서 확인하세요.")
                    del st.session_state.draft_title
                    st.rerun()
            
            with col_btn2:
                if st.button("🖼️ 카드뉴스 즉시 제작", use_container_width=True):
                    _generate_card_preview(selected_theme, edited_title, edited_tags, st.session_state.current_input_data, images=st.session_state.get('draft_images', []))

            with col_btn3:
                if st.button("❌ 작성 취소", use_container_width=True):
                    del st.session_state.draft_title
                    st.rerun()

        _render_card_preview_area()


def render_publish_mode(school_name, selected_theme):
    """
    Renders the Publish Mode (Archive List -> Batch Generation).
    """
    # If viewing a specific article, show detail view
    if 'current_view' in st.session_state:
        _render_detail_view(school_name, selected_theme)
        return

    st.title("🗂️ 기사 보관함 및 뉴스레터 발행")
    
    history_list = DB.get_all_articles()
    if not history_list:
        st.info("아직 저장된 기사가 없습니다. '기사 작성' 메뉴에서 새로운 소식을 작성해보세요.")
        return

    df = pd.DataFrame(history_list)
    # Sort by date desc
    if 'date' in df.columns:
        df = df.sort_values(by='date', ascending=False)

    col_list, col_action = st.columns([2, 1])
    
    with col_list:
        st.subheader("📋 보관된 기사 목록")
        # Display simplified DF
        st.dataframe(
            df[['date', 'event_name', 'grade', 'tone']], 
            use_container_width=True,
            hide_index=True
        )

    with col_action:
        st.subheader("📰 뉴스레터 제작 작업")
        st.info("왼쪽 목록에 있는 기사 중, 이번 뉴스레터에 실을 기사들을 아래에서 선택해주세요.")
        
        # Multi-select for generation
        options_map = {i: f"[{row['date']}] {row['event_name']}" for i, row in df.iterrows()}
        selected_indices = st.multiselect(
            "기사 선택",
            options=options_map.keys(),
            format_func=lambda x: options_map[x]
        )
        
        st.markdown("---")
        format_type = st.radio("발행 스타일", ["Booklet (책자형)", "Newspaper (A4 신문 1장)"])
        use_ai_summary = st.checkbox("PPT용 AI 요약 포함", value=True)
        
        if st.button("🚀 통합 문서(PDF/Word/PPT) 생성", type="primary", use_container_width=True):
            if not selected_indices:
                st.warning("선택된 기사가 없습니다.")
            else:
                _generate_newsletters(selected_indices, history_list, selected_theme, school_name, format_type, use_ai_summary)

    # Allow clicking to view details
    st.markdown("---")
    with st.expander("🔍 기사 상세 조회 및 수정", expanded=False):
        view_idx = st.selectbox("상세 내용을 확인하거나 수정할 기사를 선택하세요:", 
                              options=df.index, 
                              format_func=lambda x: f"[{df.loc[x]['date']}] {df.loc[x]['event_name']}")
        if st.button("기사 상세 보기"):
            target_id = df.loc[view_idx]['id']
            target_item = next((item for item in history_list if item['id'] == target_id), None)
            if target_item:
                st.session_state.current_view = target_item
                st.rerun()

    # Download Section for Batch keys
    if 'ready_pdf' in st.session_state:
        st.success("문서 생성이 완료되었습니다!")
        c1, c2, c3 = st.columns(3)
        c1.download_button("📥 PDF 다운로드", st.session_state.ready_pdf, "newsletter.pdf", "application/pdf", use_container_width=True)
        c2.download_button("📥 Word 다운로드", st.session_state.ready_docx, "newsletter.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        if 'ready_ppt' in st.session_state:
            c3.download_button("📥 PPT 다운로드", st.session_state.ready_ppt, "presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", use_container_width=True)


def _generate_newsletters(selected_indices, history_list, selected_theme, school_name, format_type, use_ai_summary):
    with st.spinner("문서를 제작하고 있습니다..."):
        # indices are from df.iterrows(), so they match history_list index IF history_list same order.
        # But df was Sorted Descending!
        # selected_indices comes from df iteration order keys.
        # history_list in DB service is typically chronological.
        # But `df = pd.DataFrame(history_list).sort_values(...)` changes order.
        # `df.iterrows()` returns (index, row). 'index' is original index if preservation holds.
        # Let's verify: `options_map`. `i` is the index of the dataframe.
        # If I use `df = df.sort_values(...)`, the index *label* is preserved, but `iterrows` iterates in sorted order.
        # So `i` is the original index.
        # `history_list` is a list of dicts. `pd.DataFrame(history_list)` assigns 0..N index.
        # So `i` corresponds to initial `history_list` index.
        # Safe to use `history_list[i]`.
        
        articles = [history_list[i] for i in selected_indices]
        
        # 1. PDF
        pdf = PDFEngine(selected_theme, school_name)
        if format_type == "Newspaper (A4 신문 1장)":
            pdf.add_newspaper_page(articles)
        else:
            pdf.draw_cover()
            for art in articles:
                pdf.add_article(art, is_booklet=True)
        pdf_data = bytes(pdf.output(dest='S'))
        
        # 2. Word
        word_engine = WordEngine(selected_theme, school_name)
        docx_buffer = word_engine.generate(articles)
        
        # 3. PPT
        ppt_articles = []
        for art in articles:
            art_copy = art.copy()
            if use_ai_summary:
                summary_lines = summarize_article_for_ppt(art_copy.get('content', ''))
                art_copy['content'] = summary_lines
            ppt_articles.append(art_copy)
            
        ppt_engine = PPTEngine(selected_theme, school_name)
        ppt_buffer = ppt_engine.create_presentation(ppt_articles)
        
        st.session_state.ready_pdf = pdf_data
        st.session_state.ready_docx = docx_buffer
        st.session_state.ready_ppt = ppt_buffer


def _generate_card_preview(theme, title, tags_str, input_info, images=None):
    with st.spinner("요약 카드 생성 중..."):
        engine = CardNewsEngine(theme)
        tags = [t.strip() for t in tags_str.split() if t.strip()]
        
        final_images = []
        temp_files_to_cleanup = []

        if images:
            for img in images:
                if isinstance(img, str): # Path (Already saved)
                    final_images.append(img)
                else: # UploadedFile (Buffer)
                    tmp_path = f"tmp_{uuid.uuid4()}.png"
                    with open(tmp_path, "wb") as f: f.write(img.getbuffer())
                    final_images.append(tmp_path)
                    temp_files_to_cleanup.append(tmp_path)
        
        raw_date = input_info['date']
        date_str = raw_date.strftime("%Y-%m-%d") if hasattr(raw_date, 'strftime') else str(raw_date)
            
        summary_card = engine.create_card(
            title=title, 
            date=date_str, 
            location=input_info.get('location', ''),
            grade=input_info.get('grade', ''),
            hashtags=tags, 
            images=final_images
        )
            
        for p in temp_files_to_cleanup:
            if os.path.exists(p): os.remove(p)
            
        st.session_state.preview_cards = [summary_card]
        st.session_state.p_idx = 0


def _render_card_preview_area():
    if 'preview_cards' in st.session_state:
        st.markdown("---")
        st.subheader("🖼️ 카드뉴스 요약 카드")
        _, col_mid, _ = st.columns([0.5, 1, 0.5])
        with col_mid:
            p_cards = st.session_state.preview_cards
            st.image(p_cards[0], use_container_width=True)
            
            c_dl, c_close = st.columns(2)
            with c_dl:
                img_io = io.BytesIO()
                p_cards[0].save(img_io, format='PNG')
                st.download_button("📥 PNG 다운로드", img_io.getvalue(), "card_news.png", "image/png", use_container_width=True)
            with c_close:
                if st.button("✖️ 미리보기 닫기"):
                    del st.session_state.preview_cards
                    st.rerun()

def _render_detail_view(school_name, selected_theme):
    v = st.session_state.current_view
    is_editing = st.session_state.get('is_editing', False)
    
    st.button("🔙 목록으로 돌아가기", on_click=lambda: st.session_state.pop('current_view'))
    st.markdown("---")

    if is_editing:
        st.subheader(f"📝 기사 수정하기: {v.get('event_name', '')}")
        with st.container(border=True):
            new_title = st.text_input("📝 제목 수정", value=v['title'])
            new_content = st.text_area("✍️ 본문 수정", value=v['content'], height=400)
            
            c1, c2 = st.columns(2)
            if c1.button("💾 변경사항 저장", type="primary", use_container_width=True):
                # Using singleton DB
                if DB.update_article(v['id'], new_title, new_content):
                    st.session_state.current_view['title'] = new_title
                    st.session_state.current_view['content'] = new_content
                    st.session_state.is_editing = False
                    st.success("수정사항이 저장되었습니다.")
                    st.rerun()
            if c2.button("취소", use_container_width=True):
                st.session_state.is_editing = False
                st.rerun()
    else:
        _render_article_html(v)
        
        with st.container(border=True):
            st.markdown("### 🛠️ 추가 도구")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🖼️ 카드뉴스 만들기", use_container_width=True):
                    # Load hashtag string safely
                    try:
                        tags = json.loads(v.get('hashtags', '[]'))
                        tags_str = ' '.join(tags)
                    except:
                        tags_str = ""
                        
                    # Load images safely
                    try:
                        imgs = json.loads(v.get('images', '[]'))
                    except:
                        imgs = []

                    _generate_card_preview(selected_theme, v['title'], tags_str, 
                                         {'date': v['date'], 'location': v['location'], 'grade': v['grade']},
                                         images=imgs)
            with c3:
                 if st.button("✏️ 수정하기", use_container_width=True):
                     st.session_state.is_editing = True
                     st.rerun()
        
        _render_card_preview_area()


def get_base64_img(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{data}"
    except: return ""

def _render_article_html(v):
    imgs_raw = v.get('images', '[]')
    imgs = json.loads(imgs_raw) if isinstance(imgs_raw, str) else imgs_raw
    
    img_html = ""
    if imgs:
        img_items_html = ""
        for i in range(min(len(imgs), 4)):
             b64 = get_base64_img(imgs[i])
             if b64: img_items_html += f'<img src="{b64}" class="img-item">'
        img_html = f'<div class="img-grid grid-{len(imgs)}">{img_items_html}</div>'

    html = f"""
    <div class="article-card">
        <div class="article-header">
            <div class="article-title">{v['title']}</div>
            <div class="badge-container">
                <div class="badge">📅 {v['date']}</div>
                <div class="badge">🏫 {v['location']}</div>
                <div class="badge">🎓 {v.get('grade','')}</div>
            </div>
        </div>
        {img_html}
        <div class="article-content">{v['content']}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
