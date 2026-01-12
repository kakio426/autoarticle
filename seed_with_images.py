import shutil
import os
import uuid
import json
import sqlite3
import pandas as pd
from engines.db_service import DatabaseService

# Configuration
SOURCE_DIR = r"C:\Users\kakio\.gemini\antigravity\brain\107c9fe0-9e36-4216-81a6-ecd557eb4911"
DEST_DIR = r"C:\Users\kakio\autoarticle\uploaded_images"

# Map topics to specific findings
IMAGE_MAP = {
    "100_days": ["celebration_cake_1768217673315.png", "celebration_letters_1768217693714.png"],
    "sports": ["sports_relay_1768217708973.png", "sports_gourd_1768217725220.png"],
    "career": ["career_vr_1768217743918.png", "career_mentor_1768217761155.png"],
    "library": ["library_storytelling_1768217788883.png", "library_bookmark_1768217805404.png"],
    "garden": ["garden_cabbage_1768217821175.png", "garden_radish_1768217837738.png"],
    "invention": ["invention_robot_1768217853199.png", "invention_recycle_1768217870816.png"]
}

def setup_images():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        
    final_paths = {}
    
    for key, filenames in IMAGE_MAP.items():
        doc_paths = []
        for fname in filenames:
            src = os.path.join(SOURCE_DIR, fname)
            dst = os.path.join(DEST_DIR, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                doc_paths.append(dst)
                print(f"Copied {fname}")
            else:
                print(f"WARNING: Source image not found: {src}")
        final_paths[key] = doc_paths
    return final_paths

def seed_db(image_paths):
    # Reset DB
    if os.path.exists("articles.db"):
        os.remove("articles.db")
    
    db = DatabaseService()
    
    samples = [
        {
            "date": "2025/03/10",
            "school": "서울디지털초등학교",
            "grade": "1학년",
            "event_name": "입학 100일 기념 잔치 🎂",
            "location": "교실 및 강당",
            "tone": "따뜻하고 감성적인",
            "keywords": "입학 100일, 축하, 케이크, 편지 쓰기",
            "title": "🎉 우리들이 학교에 온 지 100일! 사랑이 넘치는 100일 잔치",
            "content": "서울디지털초등학교 1학년 교실에서는 웃음꽃이 활짝 피어났습니다. 입학한 지 어느덧 100일이 된 우리 아이들을 축하하는 '100일 기념 잔치'가 열렸기 때문입니다. 처음 학교 문을 두드리던 설렘이 어제 같은데, 벌써 늠름해진 모습으로 선생님과 친구들에게 감사의 편지를 쓰는 아이들의 모습이 무척 대견했습니다. 부모님들의 따뜻한 영상 메시지와 함께 나눠 먹은 백일 떡은 그 무엇보다 달콤했습니다.",
            "images": json.dumps(image_paths.get("100_days", [])),
            "hashtags": json.dumps(["#입학100일", "#축하해", "#감사편지", "#백일떡", "#학교사랑"])
        },
        {
            "date": "2025/05/20",
            "school": "서울디지털초등학교",
            "grade": "전교생",
            "event_name": "가을 한마음 운동회 🏃‍♂️",
            "location": "운동장",
            "tone": "활발하고 생동감 있는",
            "keywords": "운동회, 이어달리기, 박 터뜨리기, 협동",
            "title": "🏃‍♂️ 파란 하늘 아래 펼쳐진 열정의 승부! '가을 한마음 운동회'",
            "content": "높고 푸른 가을 하늘 아래, 서울디지털초등학교의 운동장은 함성 소리로 가득 찼습니다. 전교생이 청군과 백군으로 나뉘어 그동안 갈고닦은 기량을 뽐냈습니다. 손에 땀을 쥐게 하는 이어달리기와 모두가 마음을 모아 진행한 박 터뜨리기는 운동회의 백미였습니다. 승패보다 더 빛났던 것은 서로를 격려하고 응원하는 우리 아이들의 아름다운 스포츠맨십이었습니다.",
            "images": json.dumps(image_paths.get("sports", [])),
            "hashtags": json.dumps(["#가을운동회", "#청군백군", "#이어달리기", "#박터뜨리기", "#스포츠맨십"])
        },
        {
            "date": "2025/06/15",
            "school": "서울디지털초등학교",
            "grade": "6학년",
            "event_name": "진로 체험 대잔치 🔬",
            "location": "각 교실 및 AI실",
            "tone": "격조 있고 정중한",
            "keywords": "진로, 전문가 초청, VR 체험, 미래 설계",
            "title": "🔭 나의 미래를 디자인하다! 6학년 진로 체험 대잔치 개최",
            "content": "6학년 학생들을 대상으로 미래의 꿈을 탐색하는 '진로 체험 대잔치'가 열렸습니다. IT 전문가, 과학자, 예술가 등 각 분야의 멘토들을 초청하여 직업에 대한 생생한 이야기를 듣고 직접 체험해보는 시간을 가졌습니다. 특히 VR 기기를 활용한 미래 도시 탐험은 아이들에게 큰 인기를 끌었습니다. 이번 행사를 통해 우리 아이들이 자신의 소질을 발견하고 미래를 향한 소중한 꿈의 씨앗을 심는 계기가 되었습니다.",
            "images": json.dumps(image_paths.get("career", [])),
            "hashtags": json.dumps(["#진로체험", "#꿈찾기", "#전문가멘토링", "#VR체험", "#미래설계"])
        },
        {
            "date": "2025/09/05",
            "school": "서울디지털초등학교",
            "grade": "3학년",
            "event_name": "찾아가는 도서관 나들이 📚",
            "location": "꿈틀나눔 도서관",
            "tone": "따뜻하고 감성적인",
            "keywords": "독서, 구연동화, 책갈피 만들기",
            "title": "📚 책 속 보물을 찾아서! 3학년 찾아가는 도서관 나들이",
            "content": "3학년 친구들이 학교 도서관으로 아주 특별한 나들이를 떠났습니다. 사서 선생님의 실감 나는 구연동화를 들으며 아이들은 이야기 속 주인공이 되어 모험을 즐겼습니다. 독서 후에는 자신이 좋아하는 문구를 담은 나만의 책갈피를 만들며 책과 한층 더 가까워지는 시간을 가졌습니다. 도서관 가득 퍼진 종이 냄새와 아이들의 호기심 어린 눈빛이 어우러진 행복한 오후였습니다.",
            "images": json.dumps(image_paths.get("library", [])),
            "hashtags": json.dumps(["#도서관", "#독서의계절", "#구연동화", "#책갈피", "#마음의양식"])
        },
        {
            "date": "2025/11/12",
            "school": "서울디지털초등학교",
            "grade": "전교생",
            "event_name": "학교 텃밭 수확의 날 🌽",
            "location": "행복 나눔 텃밭",
            "tone": "간결하고 명확한",
            "keywords": "수확, 배추, 관찰, 자연 사랑",
            "title": "🌽 땀방울이 맺은 결실! '행복 나눔 텃밭' 수확 현장",
            "content": "봄부터 정성껏 가꿔온 학교 텃밭에서 드디어 수확의 기쁨을 맞이했습니다. 아이들은 직접 심고 물을 주며 키운 배추와 무가 어느덧 훌쩍 자란 모습에 놀라움을 감추지 못했습니다. 흙을 묻히며 직접 수확한 채소들을 보며 생명의 소중함과 수확의 정직한 가치를 배우는 뜻깊은 시간이었습니다. 오늘 수확한 농작물은 주변 이웃들과 함께 나누며 따뜻한 정을 전할 예정입니다.",
            "images": json.dumps(image_paths.get("garden", [])),
            "hashtags": json.dumps(["#텃밭수확", "#생태교육", "#배추수확", "#나눔의기쁨", "#자연사랑"])
        },
        {
            "date": "2025/12/20",
            "school": "서울디지털초등학교",
            "grade": "5학년",
            "event_name": "과학의 날 발명 경진대회 🚀",
            "location": "과학실",
            "tone": "활발하고 생동감 있는",
            "keywords": "발명, 아이디어, 코딩, 창의력",
            "title": "🚀 반짝이는 아이디어의 향연! 5학년 발명 경진대회",
            "content": "생활 속 불편함을 해결하기 위한 아이디어들이 한자리에 모였습니다. 5학년 학생들이 참여한 '발명 경진대회'에서는 창의력이 돋보이는 다양한 작품들이 쏟아져 나왔습니다. 코딩을 활용한 자동 화분 물주기 장치부터 재활용품을 이용한 다용도 수납함까지, 아이들의 상상력에는 한계가 없었습니다. 실패를 두려워하지 않고 수없이 시도하며 자신의 아이디어를 구체화한 우리 5학년 과학 꿈나무들에게 아낌없는 박수를 보냅니다.",
            "images": json.dumps(image_paths.get("invention", [])),
            "hashtags": json.dumps(["#발명대회", "#과학의날", "#창의력", "#코딩", "#미래과학자"])
        }
    ]
    
    for s in samples:
        s['id'] = str(uuid.uuid4())
        db.save_article(s)
    
    print("Database seeded successfully with 6 articles and AI images.")

if __name__ == "__main__":
    paths = setup_images()
    seed_db(paths)
