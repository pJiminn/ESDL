from NaverNewsCrawler import save_news_file, fetch_news_over_period
from T5_summary import init, start_all_summary

# 아래의 배열에 키워드를 배열로 저장해두면
search_keyword_list = [
    "카카오뱅크"
]
'''
"한온시스템", "현대모비스", "현대위아", "HL만도", "KG모빌리티",
    "현대차", "기아", "잼백스링크", "한국앤컴퍼니", "삼성전자",
    "토탈소프트", "DH오토웨어", "씨큐브", "소니드", "앤씨앤",
    "디에이테크놀로지", "현대오토에버", "아이윈", "넥스트칩", "파인디지털",
    "동운아나텍", "쏘카", "트루윈", "한국전자홀딩스", "덕우전자", "라이컴",
    "삼성전기"
'''


# 여기 반복문에서 하나씩 꺼내서 기사 여러 개의 요약문 파일을 저장함
for search_keyword in search_keyword_list:
    # 뉴스 데이터 수집
    start_date = '2023-05-25'
    end_date = '2023-05-25'
    news_df = fetch_news_over_period(search_keyword, start_date, end_date)
    news_file_path = save_news_file(search_keyword, news_df)
    print("모든 뉴스 html 수집 완료")

    # 요약 작업 수행
    content_list, id_list, summary_list, date_list, model, tokenizer, device = init(
        news_file_path)
    start_all_summary(news_file_path, content_list, date_list,
                      id_list, summary_list, model, tokenizer, device)
    print("끝")
