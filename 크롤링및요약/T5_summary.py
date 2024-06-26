import os
import torch
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from transformers import T5ForConditionalGeneration, AutoTokenizer


def load_csv(file_path):
    try:
        # CSV 파일 불러오기
        df = pd.read_csv(file_path)
        # 필요한 열 추출
        urls = df['Link'].tolist()
        titles = df['Title'].tolist()
        contents = df['Description'].tolist()
        dates = df['Date'].tolist()
        return urls, titles, contents, dates
    except Exception as e:
        print("Error occurred while loading the CSV file:", e)
        return None, None, None, None


def generate_summary(input_text, model, tokenizer, device, max_new_tokens):
    # 입력 문장을 문장 단위로 분할
    sentences = input_text.split("\n")
    num_sentences = len(sentences)
    summary_parts = []

    for i in range(0, num_sentences, max_new_tokens):
        part = " ".join(sentences[i: i + max_new_tokens])
        prefix = "summarize: " + part
        token = tokenizer.encode(
            prefix, return_tensors="pt", max_length=max_new_tokens, truncation=True)
        token = token.to(device)  # GPU 사용을 위해 토큰을 디바이스로 이동
        output = model.generate(
            input_ids=token, max_length=max_new_tokens, num_return_sequences=1)
        summary_part = tokenizer.decode(output[0], skip_special_tokens=True)
        summary_parts.append(summary_part)

    # 작은 문장들의 요약을 합쳐서 전체 문장의 요약 생성
    full_summary = " ".join(summary_parts)
    return full_summary


def init(news_file_path):
    # GPU 사용 설정
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 경로는 모델 폴더가 설치된 경로로 설정해야 합니다.
    path = "kimdwan/t5-base-korean-summarize-LOGAN"
    model = T5ForConditionalGeneration.from_pretrained(path)
    tokenizer = AutoTokenizer.from_pretrained(path)

    # 모델을 GPU로 이동
    model.to(device)

    # CSV 파일 경로
    urls, titles, contents, dates = load_csv(news_file_path)

    url_list = []
    title_list = []
    content_list = []
    summary_list = []
    date_list = []
    id_list = []

    if urls and titles and contents and dates:
        # 데이터를 성공적으로 불러왔을 때 수행할 작업
        for url, title, content, date in zip(urls, titles, contents, dates):
            url_list.append(url)
            title_list.append(title)
            content_list.append(content)
            # 날짜 데이터 형식 변환
            date_list.append(datetime.strptime(
                date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d"))
    else:
        print("Failed to load data from CSV file.")

    return content_list, id_list, summary_list, date_list, model, tokenizer, device


def save_summary_file(news_file_path, date, id_list, summary_list):
    news_df = pd.DataFrame({'id': id_list, 'summary': summary_list})
    summary_file_dir = os.path.join("./크롤링및요약", date)
    if not os.path.exists(summary_file_dir):
        os.makedirs(summary_file_dir)

    summary_file_path = os.path.join(
        summary_file_dir, os.path.basename(news_file_path).split('_')[0] + '_summary.csv')
    news_df.to_csv(summary_file_path, index=False, encoding='utf-8-sig')
    print(f"요약 파일이 저장되었습니다: {summary_file_path}")


def start_all_summary(news_file_path, content_list, date_list, id_list, summary_list, model, tokenizer, device):
    # 날짜별로 그룹화
    date_groups = {}
    for content, date in zip(content_list, date_list):
        if date not in date_groups:
            date_groups[date] = []
        date_groups[date].append(content)

    # 날짜별로 요약 생성 및 저장
    for date, contents in date_groups.items():
        id_list = []
        summary_list = []
        for i, text in tqdm(enumerate(contents)):
            max_new_tokens = 2048  # 예시로 2048으로 설정
            summary = generate_summary(
                text, model, tokenizer, device, max_new_tokens)
            id_list.append(i + 1)
            summary_list.append(summary)

        save_summary_file(news_file_path, date, id_list, summary_list)
