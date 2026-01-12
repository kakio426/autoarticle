import google.generativeai as genai
import re

def generate_article_gemini(api_key, topic_data, style_service=None):
    if not api_key:
        return "API 키가 필요합니다.", "사이드바에 API 키를 입력해주세요.", []
    
    # genai.configure is handled globally in main(), but we can re-ensure if needed?
    # For now, we assume main() called it.
    
    try:
        # 최신 고성능 Flash 모델 설정
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
            lines = text.split('\n')
            clean_lines = [l for l in lines if not all(word.startswith('#') for word in l.split())]
            content = '\n'.join(clean_lines).strip()

        for line in text.split('\n'):
            if line.startswith("제목:") or line.startswith("##"):
                title = line.replace("제목:", "").replace("##", "").strip()
                temp_content = content.replace(line, "").strip()
                if temp_content: content = temp_content
                break
                
        return title, content, hashtags
    except Exception as e:
        return f"AI 생성 오류", str(e), []

def summarize_article_for_ppt(content, api_key=None):
    """
    긴 기사 내용을 PPT용 3~5줄 개조식(bullet points)으로 요약합니다.
    """
    if api_key:
        try:
            genai.configure(api_key=api_key)
        except: pass

    # Prioritize Stable Models
    models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-3.0-flash-preview']
    
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
    
    last_error = ""

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            lines = [line.strip().replace('* ', '').replace('- ', '') for line in response.text.split('\n') if line.strip()]
            if lines:
                return lines
        except Exception as e:
            last_error = str(e)
            print(f"⚠️ [PPT AI 요약] 모델 {model_name} 실패: {last_error}")
            continue 

    print(f"❌ [PPT AI 요약] 모든 모델 시도 실패. Last Error: {last_error}")
    
    # Fallback with error hint if possible, or just truncation
    # Return a single line that explains the error cleanly to the user if it's a quota issue
    if "429" in last_error or "Quota" in last_error:
        return [content[:50] + "...", "(⚠️ API 사용량 초과로 요약 불가)"]
        
    return [content[:100] + "... (내용이 길어 요약에 실패했습니다. 원문을 확인해주세요.)"]
