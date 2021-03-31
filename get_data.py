
from odbc import *
import math
from dateutil.relativedelta import relativedelta

# 날짜 테이블 정보를 가져옵니다.
# 입력: 시작일, 종료일 (yyyymmdd 형식입니다)
# 출력: 시작일과 종료일 사이에(둘다 포함) 일자 정보를 가져옵니다. 일자, 전영업일, 다음영업일, 전월말날짜, 영업일여부
def get_daily_info(start_td, end_td):
    pass

# 채권 정보를 가져옵니다
# 코드 정보를 입력하면, 종목의 발행일, 만기일, 이자지급계산월수를 가져옵니다.
def get_bond_info(code):
    pass

# spot 금리데이터를 가져옵니다
# 날짜와 섹터코드를 입력하면 key rate별 spot금리를 가져옵니다.
# 입력하는 날짜는 영업일이어야 합니다.
# 출력 형태는 [key_rate, yield] 형태의 pandas dataframe 입니다.

def get_spot_yield(td = '20200904', sector = 'A100'):
    # key_rate 값을 지정해 줍니다.
    #key_rate = [[0.25], [0.5], [0.75], [1], [1.5], [2], [2.5], [3], [4], [5], [7], [10], [20], [30]]
    key_rate = np.array([0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 7, 10, 20, 30])
    # odbc 객체를 생성합니다.
    kapodbc = Kapodbc()
    conn, cursor = kapodbc.connect()
    sql = "Select m3*100 M3, m6*100 M6, m9*100 M9, m12*100 M12, m18*100 M18," + \
               "m24*100 M24,y2_5*100 M30, y3*100 M36, y4*100 M48, y5*100 M60, y7*100 M84," + \
               "y10*100 M120,y20*100 M240, y30*100 M360 from KBPDB.dbo.tbinf_spot_detail A Where A.TradeDay = '" + td + "' and A.ClassId = '"+ sector + "'"

    df = pd.read_sql(sql, conn)
    df = df.transpose().reset_index()
    df.columns = ['index', 'yield']
    df['key_rate'] = key_rate
    spot_yield_data = df[['key_rate', 'yield']]
    return spot_yield_data


issue_date = '20210305'
due_date = '20240304'
amount = 10000
coupon_rate = 0.05
interestpaycalmcnt = 6
td = '20210330'


print(cf)
