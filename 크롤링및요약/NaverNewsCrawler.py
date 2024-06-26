from datetime import datetime, timedelta
import urllib.request
import pandas as pd
import json
import re
import os
import time
from datetime import datetime


def fetch_news_in_date_range(search_keyword, start_date, end_date, display=100):
    client_id = "URXThHSmPkIbWGbXsu2f"  # 실제 client_id로 교체
    client_secret = "BT4SdQkoOm"  # 실제 client_secret으로 교체
    query = urllib.parse.quote(search_keyword)
    idx = 0

    news_df = pd.DataFrame(columns=("Title", "Date", "Link", "Description"))

    for date in pd.date_range(start_date, end_date):
        for start_index in range(1, 1001, display):
            date_str = date.strftime('%Y-%m-%d')
            url = (
                f"https://openapi.naver.com/v1/search/news?query={query}"
                f"&display={display}&start={start_index}&sort=sim&"
                f"start_date={date_str}&end_date={date_str}"
            )
            print(f"Request URL: {url}")  # 디버깅을 위해 URL을 출력
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", client_id)
            request.add_header("X-Naver-Client-Secret", client_secret)
            try:
                response = urllib.request.urlopen(request)
                rescode = response.getcode()
                if rescode == 200:
                    response_body = response.read()
                    response_dict = json.loads(response_body.decode('utf-8'))
                    items = response_dict['items']
                    for item_index in range(len(items)):
                        remove_tag = re.compile('<.*?>')
                        title = re.sub(
                            remove_tag, '', items[item_index]['title'])
                        pubDate = items[item_index]['pubDate']
                        link = items[item_index]['link']
                        description = re.sub(
                            remove_tag, '', items[item_index]['description'])
                        news_df.loc[idx] = [title, pubDate, link, description]
                        idx += 1
                else:
                    print("Error Code:" + str(rescode))
            except urllib.error.HTTPError as e:
                print(f"HTTPError: {e.code}, {e.reason}")
            except urllib.error.URLError as e:
                print(f"URLError: {e.reason}")
            except Exception as e:
                print("Exception:", e)

            # 요청 사이에 지연 추가
            time.sleep(1)

    return news_df


def fetch_news_over_period(search_keyword, start_date, end_date):
    all_news_df = pd.DataFrame(
        columns=("Title", "Date", "Link", "Description"))

    for single_date in pd.date_range(start_date, end_date):
        date_str = single_date.strftime('%Y-%m-%d')
        print(f"Fetching news for date: {date_str}")
        batch_news_df = fetch_news_in_date_range(
            search_keyword, date_str, date_str)
        all_news_df = pd.concat(
            [all_news_df, batch_news_df], ignore_index=True)
        print(f"Fetched {len(batch_news_df)} articles for date: {date_str}")

        # 요청 후에 지연 추가
        print("Waiting for 60 seconds to prevent rate limit...")
        time.sleep(60)

        # 오늘 날짜까지 수집했다면 수집 종료
        if single_date >= pd.Timestamp(datetime.now().date()):
            print("Reached today's date. Stopping data collection.")
            break

    return all_news_df


def save_news_file(search_keyword, news_df):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"NaverNews_{search_keyword}_{formatted_datetime}.csv"
    folder_path = "./result"

    # 폴더가 존재하지 않으면 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, filename)
    news_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"CSV 파일이 저장되었습니다: {file_path}")
    return file_path
