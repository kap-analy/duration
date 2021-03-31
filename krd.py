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


# 샘플데이터 생성
# cash_count: 현금흐름의 갯수
# coupon_rate: 채권 쿠폰이율
# amount: 채권액면가
# interestpaycalmcnt: 이자지급계산월수
# maturity: 채권의 만기(연)

########################################################################
# 데이터 입력 부분                                                       #
########################################################################

cash_count = 5
coupon_rate = 0.03
amount = 10000
interestpaycalmcnt = 6
maturity = 3

cf_raw = [[1, 0.533, 2500000], [2, 1.033, 2500000], [3, 1.533, 2500000], [4, 2.033, 2500000], [5, 2.533, 2500000],
          [6, 3.033, 2500000], [7, 3.533, 2500000], [8, 4.033, 2500000], [9, 4.533, 2500000], [10, 5.033, 2500000],
          [11, 5.533, 2500000], [12, 6.033, 2500000], [13, 6.533, 2500000], [14, 7.033, 2500000], [15, 7.533, 2500000],
          [16, 8.033, 2500000], [17, 8.533, 2500000], [18, 9.033, 2500000], [19, 9.533, 2500000], [20, 10.033, 102500000]]
cf_data = pd.DataFrame(data = cf_raw, columns=['num', 'cash_time', 'cash_amt'])

# spot_curve_raw = [[0.25, 0.449], [0.5, 0.624], [0.75, 0.637], [1, 0.653], [1.5, 0.797], [2, 0.871],
#                   [2.5, 0.935], [3, 0.984], [4, 1.149], [5, 1.307], [7, 1.393], [10, 1.575], [20, 1.712], [30, 1.695]]
# spot_yield_data = pd.DataFrame(data = spot_curve_raw, columns=['key_rate', 'yield'])
logger.debug("key rate duration 산출을 시작합니다.")
print("채권 현금흐름은 다음과 같습니다. !!!!!!")
print(cf_data)

print("spot yield는 다음과 같습니다. !!!!!!")
spot_yield_data = get_spot_yield('20201005', 'C300')

print(spot_yield_data)

# Bond 객체를 생성합니다.
bond1 = Bond(cf_data)

krd = bond1.key_rate_duration(spot_yield_data=spot_yield_data, interestpaycalmcnt=6, delta=0.01)
print("key rate duration은 다음과 같습니다.\n", krd)
