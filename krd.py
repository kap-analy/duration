########################################################################
# key rate duration                                                    #
########################################################################

# #### 입력
# - 현금흐름 정보가 있는 pandas dataframe
#     - index: 날짜
#     - 컬럼: 발생하는 현금흐름의 양. 원 단위이다. 컬럼명은 cash
# - key rate별 spot curve 금리 데이터 pandas dataframe
#     - index: 날짜
#     - key rate: 3M, 6M, ..., (섹터 정보에 따라 최대 key rate이 5Y, 10Y, 30Y 등으로 다르다)

# #### 출력
# - key rate별 듀레이션이 출력된다.
# - DB 저장을 위해 key rate duration은 14개 구간에 대해 나온다.
# - 이 key rate duration의 합이 종목의 듀레이션 값이 나오게 조정한다.

from bond import *
from get_data import *
from logging_pack import *
import timeit

start_time = timeit.default_timer() #시작 시간 체크

# 샘플데이터 생성
# cash_count: 현금흐름의 갯수
# coupon_rate: 채권 쿠폰이율
# amount: 채권액면가
# interestpaycalmcnt: 이자지급계산월수
# maturity: 채권의 만기(연)

########################################################################
# 데이터 입력 부분                                                       #
########################################################################

# cash_count = 5
# coupon_rate = 0.03
# amount = 10000
# interestpaycalmcnt = 6
# maturity = 3

# cf_raw = [[1, 0.533, 2500000], [2, 1.033, 2500000], [3, 1.533, 2500000], [4, 2.033, 2500000], [5, 2.533, 2500000],
#           [6, 3.033, 2500000], [7, 3.533, 2500000], [8, 4.033, 2500000], [9, 4.533, 2500000], [10, 5.033, 2500000],
#           [11, 5.533, 2500000], [12, 6.033, 2500000], [13, 6.533, 2500000], [14, 7.033, 2500000], [15, 7.533, 2500000],
#           [16, 8.033, 2500000], [17, 8.533, 2500000], [18, 9.033, 2500000], [19, 9.533, 2500000], [20, 10.033, 102500000]]
# cf_data = pd.DataFrame(data = cf_raw, columns=['num', 'cash_time', 'cash_amt'])

# spot_curve_raw = [[0.25, 0.449], [0.5, 0.624], [0.75, 0.637], [1, 0.653], [1.5, 0.797], [2, 0.871],
#                   [2.5, 0.935], [3, 0.984], [4, 1.149], [5, 1.307], [7, 1.393], [10, 1.575], [20, 1.712], [30, 1.695]]
# spot_yield_data = pd.DataFrame(data = spot_curve_raw, columns=['key_rate', 'yield'])
logger.debug("key rate duration 산출을 시작합니다.")

########################################################################
# 데이터를 입력합니다.                                                       #
########################################################################
# td = '20200904' # key rate duration을 구할 날짜입니다.
# issue_date = '20190208' # 채권의 발행일
# due_date  = '20390208' # 채권의 만기일
# amount = 10000
# coupon_rate = 0.02191
# interestpaycalmcnt = 3
# sectorcode = 'F212'
#
# # Bond 객체를 생성합니다.
# bond1 = Bond(td=td, issue_date=issue_date, due_date=due_date,
#              amount=amount, coupon_rate=coupon_rate, interestpaycalmcnt=interestpaycalmcnt)
#
# bond1_cf = bond1.bond_cf()
# print("채권 현금흐름은 다음과 같습니다. !!!!!!")
# print(bond1_cf)
#
# print("spot yield는 다음과 같습니다. !!!!!!")
# spot_yield_data = get_spot_yield(td, sectorcode)
#
# print(spot_yield_data)
#
# krd = bond1.key_rate_duration(spot_yield_data=spot_yield_data, delta=0.01)
# print("key rate duration은 다음과 같습니다.\n", krd)
# print("key rate duration의 합: ", np.sum(krd))

#####################
# 정답
# 0.001142808	0.002275107	0.003420771	0.007383728	0.013606139	0.017979911	0.022392036	0.04212059	0.069864591	0.135734599	0.29874631	8.167940176	1.923042661	0	10.70564943
#################

# 날짜를 입력합니다.
td = '20200901'
amount = 10000
# 해당 날짜의 대상종목을 받아옵니다.
bond_info = get_bond_info(td)

# bond_info는 pandas dataframe으로 다음 정보가 있습니다.
#  securitycode, sectorcode,  issue_date, due_date, coupon_rate, interestpaycalmcnt, dur
# df는 채권 key rate duration을 저장하는 pandas dataframe입니다.
df = pd.DataFrame()
# marks = []
# range(len(bond_info))
for i in range(len(bond_info)):
    info = bond_info.iloc[i]
    # Bond 객체를 생성합니다.
    bond = Bond(td=td, issue_date=info['issue_date'], due_date=info['due_date'],
                amount=amount, coupon_rate=info['coupon_rate'],
                num_of_interest_payment=info['num_of_interest_payment'],
                interest_payment_type=info['interest_payment_type'])

    bond_cf = bond.bond_cf()
    if len(bond_cf) == 0: # 곧 만기가 도래하여 현금흐름이 존재하지 않는 경우
        krd = [0 for _ in range(14)]
    else:
        spot_yield_data = get_spot_yield(td, info['sectorcode'])
        krd = bond.key_rate_duration(cf_data=bond_cf, spot_yield_data=spot_yield_data, delta=0.01)
    krd_df = pd.DataFrame(krd).transpose()
    krd_df.columns = ['M3', 'M6', 'M9', 'Y1', 'Y1.5', 'Y2', 'Y2.5', 'Y3', 'Y4', 'Y5', 'Y7', 'Y10', 'Y20', 'Y30']

    krd_df = krd_df.assign(**{'StdDate': datetime.strptime(td, '%Y%m%d').date(),
                                'SecurityCode': info['securitycode'],
                                'KeySum': np.sum(krd, axis = 0)})
    df = df.append(krd_df)
    print(i, "번째 key rate duration 산출이 완료되었습니다.")
print(df)

terminate_time = timeit.default_timer() #종료 시간 체크
print("%f초 걸렸습니다" %(terminate_time - start_time))