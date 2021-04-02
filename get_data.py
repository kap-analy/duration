
from odbc import *
import datetime
import math
from dateutil.relativedelta import relativedelta

# 날짜 테이블 정보를 가져옵니다.
# 입력: 시작일, 종료일 (yyyymmdd 형식입니다)
# 출력: 시작일과 종료일 사이에(둘다 포함) 일자 정보를 가져옵니다. 일자, 전영업일, 다음영업일, 전월말날짜, 영업일여부
def get_daily_info(start_td, end_td):
    pass

# 채권 정보를 가져옵니다
# 코드 정보를 입력하면, 종목의 발행일, 만기일, 이자지급계산월수를 가져옵니다.
def get_bond_info(start_td):
    kapodbc = Kapodbc(server='10.10.10.18,33440', db='KBPDB', user='kapuser', pwd='reada11!')
    conn, cursor = kapodbc.connect()
    sql = "select td = '" + start_td + "'" + \
          ", code = A.표준코드, sector = A.새분류" + \
          ", coupon_rate = B.COUPONRATE" + \
          ", InterestPayCalMCnt = A.이자지급계산월수" + \
          ", due_date = convert(varchar(10), A.발행일, 120)" + \
          ", issue_date = convert(varchar(10), A.상환일, 120)" + \
          ", nextpay_date = convert(varchar(10), B.NEXTPAYDAY, 120)" + \
          "from BOND.DBO.bond11master A inner join SENDDB.dbo.V_BOND_STANDARD B on A.표준코드 = B.BONDID " + \
          "where A.상환일  > '" + start_td + "' and B.TradeDay = '" + start_td + "'" + \
          "and A.옵션부사채구분 = '0' and A.새분류 <> 'F3Z0'" + \
          "and (A.상환방법 not in ('2') or A.지방채구분 not in ('1'))" + \
          "and A.표준코드 in ('KR103101AA84','KR103101AA92','KR103102AA75','KR103102AA83','KR103103AA74','KR103103AA82','KR103104AA73')"
    df = pd.read_sql(sql, conn)
    bond_info = df[:]
    return bond_info

# spot 금리데이터를 가져옵니다
# 날짜와 섹터코드를 입력하면 key rate별 spot금리를 가져옵니다.
# 입력하는 날짜는 영업일이어야 합니다.
# 출력 형태는 [key_rate, yield] 형태의 pandas dataframe 입니다.

def get_spot_yield(td, sector):
    # key_rate 값을 지정해 줍니다.
    #key_rate = [[0.25], [0.5], [0.75], [1], [1.5], [2], [2.5], [3], [4], [5], [7], [10], [20], [30]]
    key_rate = np.array([0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 7, 10, 20, 30])
    # odbc 객체를 생성합니다.
    kapodbc = Kapodbc(server='10.10.10.18,33440', db='BPRPA', user='kap_assetm', pwd='bprpaapp#2018')
    conn, cursor = kapodbc.connect()
    sql = "Select m3*100 M3, m6*100 M6, m9*100 M9, m12*100 M12, m18*100 M18," + \
          "m24*100 M24,y2_5*100 M30, y3*100 M36, y4*100 M48, y5*100 M60, y7*100 M84," + \
          "y10*100 M120,y20*100 M240, y30*100 M360 from KBPDB.dbo.tbinf_spot_detail A Where A.TradeDay = '" + td + "' and A.ClassId = '" + sector + "'"

    df = pd.read_sql(sql, conn)
    df = df.transpose().reset_index()
    df.columns = ['index', 'yield']
    df['key_rate'] = key_rate
    spot_yield_data = df[['key_rate', 'yield']]
    return spot_yield_data


