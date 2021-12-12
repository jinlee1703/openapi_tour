# openapi_tour

## 프로그램 설명

공공데이터 포털 사이트인 공공데이터포털의 API를 이용하여 출입국관광통계서비스 데이터를 크롤링하는 프로그램입니다.

## 작업 설계

1. 데이터를 수집할 국가코드와 연도 입력하기 : national_code, nStartYear, nEndYear
2. 데이터 수집 요청하기 : getTourismStatsService()
    1. url 구성하여 데이터 요청하기 : getTourismStatsItem()
    2. url 접속하고 요청하기 : getRequestUrl()
    3. 응답 데이터를 리스트로 구성하기 : jsonResult, result
3. 데이터를 JSON 파일과 CSV 파일로 저장하기 : json.dumps(), to_csv()

[코드 출처]

데이터 과학 기반의 파이썬 빅데이터 분석 - 저)이지영 / 출)한빛아카데미
