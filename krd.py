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

logger.debug("key rate duration 산출을 시작합니다.")

# 날짜를 입력합니다.
td = '20200904'
amount = 10000
# 해당 날짜의 대상종목을 받아옵니다.
bond_info = get_bond_info(td)

# 해당 날짜의 spot yield를 받아옵니다.
spot_yield_data = get_spot_yield(td)
# bond_info는 pandas dataframe으로 다음 정보가 있습니다.
#  securitycode, sectorcode,  issue_date, due_date, coupon_rate, interestpaycalmcnt, dur
# df는 채권 key rate duration을 저장하는 pandas dataframe입니다.
# 날짜를 변환합니다.
td = datetime.strptime(td, '%Y%m%d').date()

df = pd.DataFrame()
# marks = []
# range(len(bond_info))
for i in range(600):
    info = bond_info.iloc[i]
    # 날짜를 datetime 타입으로 변경합니다.
    issue_date = datetime.strptime(info['issue_date'], '%Y%m%d').date()
    due_date = datetime.strptime(info['due_date'], '%Y%m%d').date()

    # Bond 객체를 생성합니다.
    bond = Bond(td=td, issue_date=issue_date, due_date=due_date,
                amount=amount, coupon_rate=info['coupon_rate'],
                num_of_interest_payment=info['num_of_interest_payment'],
                interest_payment_type=info['interest_payment_type'])

    bond_cf = bond.bond_cf()
    if len(bond_cf) == 0: # 곧 만기가 도래하여 현금흐름이 존재하지 않는 경우
        krd = [0 for _ in range(14)]
    else:
        yield_data = spot_yield_data.loc[info['sectorcode']]
        yield_data = pd.DataFrame(yield_data).reset_index()
        yield_data.columns=['key_rate', 'yield']
        krd = bond.key_rate_duration(cf_data=bond_cf, spot_yield_data=yield_data, delta=0.01)
    krd_df = pd.DataFrame(krd).transpose()
    krd_df.columns = ['M3', 'M6', 'M9', 'Y1', 'Y1.5', 'Y2', 'Y2.5', 'Y3', 'Y4', 'Y5', 'Y7', 'Y10', 'Y20', 'Y30']

    krd_df = krd_df.assign(**{'StdDate': td,
                                'SecurityCode': info['securitycode'],
                                'KeySum': np.sum(krd, axis = 0)})
    df = df.append(krd_df)
    print(i, "번째 key rate duration 산출이 완료되었습니다.")
print(df)

terminate_time = timeit.default_timer() #종료 시간 체크
print("%f초 걸렸습니다" %(terminate_time - start_time))

