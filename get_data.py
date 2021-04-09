
from kap_db_connect import *
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
    sql = "select securitycode = RTRIM(A.표준코드),  " + \
	                "sectorcode = RTRIM(B.SectorCode),  " + \
	                "issue_date = convert(varchar(10), A.발행일, 112), " + \
	                "due_date = convert(varchar(10), A.상환일, 112), " + \
	                "coupon_rate = A.표면이율/100,  " + \
	                "num_of_interest_payment = 12 / A.이자지급계산월수,  " + \
	                "interest_payment_type = A.이자지급방법, " + \
	                "payment_type = A.상환방법," + \
	                "memo = A.특이발행조건," + \
	                "dur = B.Dur " + \
                    "from BOND.dbo.BOND11MASTER A,  " + \
	                     "BPRPA..H_SECURITY_PRICE_YTM_HOLIDAY B  " + \
                    "where A.상환일 > '" + td + "' " + \
	                    "and A.주식관련사채구분 = 1  " + \
	                    "and A.옵션부사채구분 = 0  " + \
	                    "and A.이자지급방법 like '1%'  " + \
	                    "and A.표준코드 = B.SecurityCode  " + \
	                    "and B.StdDate = '" + td + "' order by securitycode"

    bond_info = pd.read_sql(sql, conn)

    return bond_info

# spot 금리데이터를 가져옵니다
# 날짜와 섹터코드를 입력하면 key rate별 spot금리를 가져옵니다.
# 입력하는 날짜는 영업일이어야 합니다.
# 출력 형태는 [key_rate, yield] 형태의 pandas dataframe 입니다.

def get_spot_yield(td):
    # key_rate 값을 지정해 줍니다.
    #key_rate = [[0.25], [0.5], [0.75], [1], [1.5], [2], [2.5], [3], [4], [5], [7], [10], [20], [30]]
    key_rate = np.array([0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 7, 10, 20, 30])
    # odbc 객체를 생성합니다.
    kapodbc = Kapodbc()
    conn, cursor = kapodbc.connect()
    sql = "Select sectorcode = classID, m3*100 M3, m6*100 M6, m9*100 M9, m12*100 M12, m18*100 M18," + \
               "m24*100 M24,y2_5*100 M30, y3*100 M36, y4*100 M48, y5*100 M60, y7*100 M84," + \
               "y10*100 M120,y20*100 M240, y30*100 M360 from KBPDB.dbo.tbinf_spot_detail A Where A.TradeDay = '" + td + "' "

    df = pd.read_sql(sql, conn)
    df.set_index('sectorcode', inplace=True)
    df.columns = key_rate
    return df

def get_one_bond_info(td, securitycode):
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
	                    "and A.CR not in ('BB+', 'BB-', 'BB', 'B+', 'B', 'B-', 'CCC')" + \
                        "and A.SecurityCode = '" + securitycode + "'  order by securitycode"
    bond_info = pd.read_sql(sql, conn)

    return bond_info

def get_amortized_bond():
    # odbc 객체를 생성합니다.
    kapodbc = Kapodbc(server='10.10.10.20,33440')
    conn, cursor = kapodbc.connect()
    sql = "SELECT securitycode = SecurityCode " + \
                ",defered_period = DeferedPeriod " + \
                ",amortized_period = AmortizedPeriod " + \
                ",num_of_amortized_amt = NumOfAmortizedAmt " + \
                ",interest_defered = InterestDeferedYN " + \
        "FROM [BPRPA].[dbo].[M_AMORTIZED_BOND] "
    amortized_bond_info = pd.read_sql(sql, conn)

    return amortized_bond_info
