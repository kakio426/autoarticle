
import json
import os
from engines.pdf_engine import PDFEngine
from engines.db_service import DatabaseService

def verify_layout():
    print("🔍 [Layout Verification] Starting...")
    
    # 1. DB에서 테스트 데이터 가져오기
    db = DatabaseService()
    articles = db.get_all_articles()
    if not articles:
        print("❌ No articles found. Please run seed_data.py first.")
        return
    
    # 상위 5개만 테스트
    test_set = articles[:5]
    
    # 2. PDF 생성 시뮬레이션
    pdf = PDFEngine("웜 & 플레이풀", "검증용 초등학교")
    pdf.draw_cover()
    
    page_logs = []
    
    for i, art in enumerate(test_set):
        pdf.add_article(art, is_booklet=True)
        # 현재 기사가 시작된 페이지 번호 기록
        page_logs.append({
            "title": art['title'][:15],
            "start_page": pdf.page_no(),
            "final_y": pdf.get_y()
        })
        print(f"✅ Processed Article {i+1}: Start Page {pdf.page_no()}, Y={pdf.get_y():.1f}mm")

    # 3. 검증 로직
    # Booklet 모드에서는 각 기사가 서로 다른 페이지에서 시작해야 함
    pages = [log['start_page'] for log in page_logs]
    is_unique = len(set(pages)) == len(pages)
    
    if is_unique:
        print("\n✨ [SUCCESS] Every article started on a NEW page.")
    else:
        print("\n❌ [FAILURE] Some articles shared the same page.")
        for log in page_logs:
            print(f"  - {log['title']}... : Page {log['start_page']}")

    # 실제 파일 저장은 생략 (검증용)
    print("🚀 [Verification Complete]")

if __name__ == "__main__":
    verify_layout()
