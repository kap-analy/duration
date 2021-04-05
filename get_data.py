
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
def get_bond_info(td):
    # odbc 객체를 생성합니다.
    kapodbc = Kapodbc()
    conn, cursor = kapodbc.connect()
    sql = "select securitycode = A.SecurityCode, " + \
	                "sectorcode = A.SectorCode, " + \
	                "issue_date = convert(varchar(10), A.PublicDate, 112)," + \
	                "due_date = convert(varchar(10), A.DueDate, 112)," + \
	                "coupon_rate = A.CouponRate/100, " + \
	                "num_of_interest_payment = 12 / A.InterestPayCalMCnt, " + \
                    "interest_payment_type = A.InterestPayFlag, " + \
	                "dur = B.Dur " + \
                    "from BPRPA..M_BOND_INFO A, " + \
	                    "BPRPA..H_SECURITY_PRICE_YTM_HOLIDAY B " + \
                    "where A.DueDate > '" + td + "' " + \
	                    "and A.AssetCode = 'BOND'" + \
	                    "and A.CBFlag = 1 " + \
	                    "and A.OBFlag = 0 " + \
	                    "and A.InterestPayFlag like '1%' " + \
	                    "and A.SecurityCode = B.SecurityCode " + \
	                    "and B.StdDate = '" + td + "' " + \
	                    "and A.CR not in ('BB+', 'BB-', 'BB', 'B+', 'B', 'B-', 'CCC') and A.SecurityCode = 'KRC0350C3338'"
    bond_info = pd.read_sql(sql, conn)

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



def get_spot_yield_int(td, sector):
    # key_rate 값을 지정해 줍니다.
    # interpolation에 사용되는 실측값의 밀도를 높여, 추정의 정확성을 높이기 위함입니다.
    #key_rate = [[0.25], [0.5], [0.75], [1], [1.5], [2], [2.5], [3], [4], [5], [7], [10], [20], [30]]
    key_rate = np.array([0.25, 0.333333333, 0.416666667, 0.5, 0.583333333, 0.666666667, 0.75, 0.833333333, 0.916666667, 1, 1.083333333, 1.166666667,
                         1.25, 1.333333333, 1.416666667, 1.5, 1.583333333, 1.666666667, 1.75, 1.833333333, 1.916666667, 2,
                         2.25, 2.5, 2.75, 3, 3.5, 4, 5, 6, 7, 9, 10, 15, 17, 20, 25, 30])
    # odbc 객체를 생성합니다.
    kapodbc = Kapodbc()
    conn, cursor = kapodbc.connect()
    sql = "Select m3*100 M3, m4*100 M4, m5*100 M5, m6*100 M6, m7*100 M7, m8*100 M8, m9*100 M9, m10*100 M10, m11*100 M11, m12*100 M12," + \
          "m13*100 M13, m14*100 M14, m15*100 M15, m16*100 M16, m17*100 M17, m18*100 M18, m19*100 M19, m20*100 M20, m21*100 M21, m22*100 M22, m23*100 M23, m24*100 M24," + \
          "y2_25*100 M27, y2_5*100 M30, y2_75*100 M33, y3*100 M36, y3_5*100 M42, y4*100 M48, y5*100 M60, y6*100 M72 ,y7*100 M84, y9*100 M108, y10*100 M120," + \
          "y15*100 M180, y17*100 M204 ,y20*100 M240, y25*100 M300, y30*100 M360 from KBPDB.dbo.tbinf_spot_detail A Where A.TradeDay = '" + td + "' and A.ClassId = '"+ sector + "'"

    df = pd.read_sql(sql, conn)
    df = df.transpose().reset_index()
    df.columns = ['index', 'yield']
    df['key_rate'] = key_rate
    spot_yield_data_int = df[['key_rate', 'yield']]
    return spot_yield_data_int

