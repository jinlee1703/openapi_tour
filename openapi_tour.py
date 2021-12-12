import os
import sys
import urllib.request
import datetime
import time
import json
import pandas as pd
import key


# getRequestUrl(url) : url 접속을 요청하고 응답을 받아서 반환
def getRequestUrl(url):
    req = urllib.request.Request(url)           # url 접속을 요청하는 객체
    try:
        response = urllib.request.urlopen(req)  # 서버에서 받은 응답을 저장하는 객체
        if response.getcode() == 200:           # 응답 상태가 200일 경우 요청 처리 성공
            print("[%s] Url Request Success" % datetime.datetime.now())     # 성공 메시지 출력
            return response.read().decode('utf-8')                          # 문자열을 utf-8 형식으로 디코딩
    except Exception as e:
        print(e)
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))   # 실패 메시지 출력
        return None                                                         # None 객체를 반환


# getTourismStatsItem(yyyymm, nat_cd, ed_cd) : 출입국관광통계서비스의 오픈 API를 사용하여 데이터요청 url을 만들고 getRequestUrl(url)을 호출해서 받은 응답 데이터를 반환
def getTourismStatsItem(yyyymm, nat_cd, ed_cd):
    service_url = "http://openapi.tour.go.kr/openapi/service/EdrcntTourismStatsService/getEdrcntTourismStatsList"   # 공공데이터에 접속할 앤드 포인트 주소
    parameters = "?_type=json&serviceKey=" + key.ServiceKey     # url에 추가할 매개변수 : 인증키
    parameters += "&YM=" + yyyymm                               #                    : 수집할 연월
    parameters += "&NAT_CD=" + nat_cd                           #                    : 수집대상 국가코드
    parameters += "&ED_CD=" + ed_cd                             #                    : 수집할 데이터 종류

    url = service_url + parameters          # service_url + prameters

    responseDecode = getRequestUrl(url)     # getRequestUrl(url)을 호출하여 반환받은 응답 객체

    if (responseDecode == None):            # 서버에서 None 객체를 반환했을 경우 : None 객체 반환
        return None
    else:                                   # 서버에서 받은 JSON 형태의 응답 객체를 파이썬 객체로 로드하여 반환
        return json.loads(responseDecode)   


# getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear) : 수집 기간 동안 월 단위로 getTourismStatsItem()을 호출해 받은 데이터를 리스트로 묶어 반환
def getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear):
    jsonResult = []                                         # 수집한 데이터를 JSON 저장용으로 구성할 딕셔너리의 리스트 객체
    result = []                                             # 수집한 데이터를 CSV 저장용으로 구성할 리스트 객체
    natName = ''                                            # 수집한 국가 이름 데이터
    dataEND = "{0}{1:0>2}".format(str(nEndYear), str(12))   # 마지막 데이터의 연월 : nEndYear12 ({1:0>2} : 1번째 인수를 앞자리를 0으로 채워서 최대 2칸)
    isDataEnd = 0                                           # 수집할 데이터의 끝인지 확인하기 위한 플래그 (0으로 설정)

    for year in range(nStartYear, nEndYear+1):              # 시작연도~마지막연도를 변수 year에 저장하여 반복문 실행
        for month in range(1, 13):                          # 1월~12월을 변수 month에 저장하여 반복문 실행
            if (isDataEnd == 1): break                      # 수집 데이터가 끝났을 경우 반복문 종료
            yyyymm = "{0}{1:0>2}".format(str(year), str(month))         # 수집할 연도와 월을 여섯자리로 맞추어 저장 ex)202012
            jsonData = getTourismStatsItem(yyyymm, nat_cd, ed_cd)       # 함수를 호출해 받은 월 데이터를 jsonData에 저장
            if (jsonData['response']['header']['resultMsg'] == 'OK'):   # 응답데이터가 정상인지 확인
                if jsonData['response']['body']['items'] == '':         # items 항목에 값이 없으면 데이터가 들어가지 않은 월
                    isDataEnd = 1                                       # 플래그를 1로 설정
                    dataEND = "{0}{1:0>2}".format(str(year), str(month-1))      # 마지막 데이터가 있는 날짜(month-1)를 저장
                    print("데이터 없음.... \n 제공되는 통계 데이터는 %s %s월까지입니다." %(str(year), str(month-1)))
                    break       # 데이터 수집 작업을 중단
                print(json.dumps(jsonData, indent=4, sort_keys=True, ensure_ascii=False))       # 수집한 월 데이터 내용을 확인할 수 있게 출력
                natName = jsonData['response']['body']['items']['item']['natKorNm']             # 수집한 국가 이름 항목의 값에서 띄어쓰기 제거
                natName = natName.replace(' ', '')
                num = jsonData['response']['body']['items']['item']['num']      # 수집한 월의 데이터 수
                ed = jsonData['response']['body']['items']['item']['ed']        # 수집한 출입국 구분 데이터
                print('[ %s_%s : %s ]' % (natName, yyyymm, num))
                print('------------------------------------------------')
                jsonResult.append({'nat_name': natName, 'nat_cd': nat_cd, 'yyyymm': yyyymm, 'visit_cnt': num})      # 수집한 국가 이름, 국가 코드, 날짜, 데이터 수를 딕셔너리 자료형으로 구성하여 jsonResult 리스트에 원소로 추가
                result.append({natName, nat_cd, yyyymm, num})       # 수집한 국가 이름, 국가 코드, 날짜, 데이터 수를 result 리스트에 원소로 추가
    return (jsonResult, result, natName, ed, dataEND)       # 수집하여 정리한 데이터를 반환


# main() : 전체 작업 스토리 구성
def main():
    jsoinResult = []  # 수집한 데이터를 저장할 리스트 객체 (JSON 파일 저장용)
    result = []  # 수집한 데이터를 저장할 리스트 객체 (CSV 파일 저장용)

    print("<< 국내 입국한 외국인의 통계 데이터를 수집합니다. >>")
    nat_cd = input('국가 코드를 입력하세요(중국: 112 / 일본: 130 / 미국: 275) : ')  # 데이터를 수집할 국가 코드를 입력받음
    nStartYear = int(input('데이터를 몇 년부터 수집할까요? : '))  # 데이터 수집 시작 연도
    nEndYear = int(input('데이터를 몇 년까지 수집할까요? : '))  # 데이터 수집 끝 연도
    ed_cd = "E"  # 입국/출국 코드 (E : 방한외래관광객,  D : 해외 출국)

    jsonResult, result, natName, ed, dataEND = getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear)  # 반환받은 수집 데이터를 각 변수에 저장

    # 파일저장 1 : json 파일
    with open('./%s_%s_%d_%s.json' % (natName, ed_cd, nStartYear, dataEND), 'w',
              encoding='utf8') as outfile:  # 'w' 모드, utf8 인코딩으로 파일 쓰기
        jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)  # json.dumps()를 통해 json 객체로 변환
        outfile.write(jsonFile)  # json 객체를 json 파일로 저장

    # 파일저장 2 : csv 파일
    columns = ["입국자국가", "국가코드", "입국연월", "입국자 수"]  # 데이터프레임에 만들 컬럼명을 리스트로 만듦
    result_df = pd.DataFrame(result, columns=columns)  # 수집 데이터를 리스트로 저장한 result를 데이터프레임으로 변환
    result_df.to_csv('./%s_%s_%d_%s.csv' % (natName, ed_cd, nStartYear, dataEND), index=False,
                     encoding='cp949')  # 데이터 프레임 객체를 CSV 파일로 저장

if __name__ == '__main__':
    main()