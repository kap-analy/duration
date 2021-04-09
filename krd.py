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
from kap_db_connect import *
from logging_pack import *
import timeit

start_time = timeit.default_timer() #시작 시간 체크

# 샘플데이터 생성
# cash_count: 현금흐름의 갯수
# coupon_rate: 채권 쿠폰이율
# amt: 채권액면가
# interestpaycalmcnt: 이자지급계산월수
# maturity: 채권의 만기(연)

logger.debug("key rate duration 산출을 시작합니다.")

# 날짜를 입력합니다.
td = '20210302'
amt = 10000
modelid = 'KAP030AL2'
key_rate_columns = ['M3', 'M6', 'M9', 'Y1', 'Y1.5', 'Y2', 'Y2.5', 'Y3', 'Y4', 'Y5', 'Y7', 'Y10', 'Y20', 'Y30']
# 해당 날짜의 대상종목을 받아옵니다.
bond_info = get_bond_info(td)
amortized_bond_info = get_amortized_bond()

# 해당 날짜의 spot yield를 받아옵니다.
spot_yield_data = get_spot_yield(td)
# bond_info는 pandas dataframe으로 다음 정보가 있습니다.
#  securitycode, sectorcode,  issue_date, due_date, coupon_rate, interestpaycalmcnt, dur
# df는 채권 key rate duration을 저장하는 pandas dataframe입니다.
# 날짜를 변환합니다.
td = datetime.strptime(td, '%Y%m%d').date()

df = pd.DataFrame()
# marks = [5926, 489 ]
# range(len(bond_info))
for i in np.arange(8400, len(bond_info)):
    info = bond_info.iloc[i]
    # 날짜를 datetime 타입으로 변경합니다.
    issue_date = datetime.strptime(info['issue_date'], '%Y%m%d').date()
    due_date = datetime.strptime(info['due_date'], '%Y%m%d').date()

    # Bond 객체를 생성합니다.
    bond = Bond(td=td, issue_date=issue_date, due_date=due_date,
                amt=amt, coupon_rate=info['coupon_rate'],
                num_of_interest_payment=info['num_of_interest_payment'],
                interest_payment_type=info['interest_payment_type'],
                payment_type=info['payment_type'])

    if info['payment_type'] == '2': #분할상환채인 경우 별도의 함수로 현금흐름 계산한다.
        amor_info = amortized_bond_info[amortized_bond_info.securitycode == info['securitycode']]
        if len(amor_info) == 0:
            continue # 분할상환채 정보가 없는 경우 패스한다. (신용등급이 낮거나 KAP평가 대상 종목이 아닌 경우)
        else:
            amor_info = amor_info.squeeze() # convert a dataframe into a series
            bond_cf = bond.amortized_bond_cf(defered_period=amor_info['defered_period'],
                                         amortized_period=amor_info['amortized_period'],
                                         num_of_amortized_amt=amor_info['num_of_amortized_amt'],
                                         interest_defered=amor_info['interest_defered'])
    else:
        bond_cf = bond.bond_cf()
    if len(bond_cf) == 0: # 곧 만기가 도래하여 현금흐름이 존재하지 않는 경우
        krd = [0 for _ in range(14)]
    else:
        yield_data = spot_yield_data.loc[info['sectorcode']]
        yield_data = pd.DataFrame(yield_data).reset_index()
        yield_data.columns=['key_rate', 'yield']
        krd = bond.key_rate_duration(cf_data=bond_cf, spot_yield_data=yield_data, delta=0.01)
    krd_df = pd.DataFrame(krd).transpose()
    krd_df.columns = key_rate_columns

    krd_df = krd_df.assign(**{'StdDate': td,
                                'SecurityCode': info['securitycode'],
                                'KeySum': np.sum(krd, axis = 0)})
    df = df.append(krd_df)
    #print('{}번째 데이터를 산출하였습니다.'.format(i))
    if i % 500 == 0:
        # db에 입력하기 위해 dataframe을 정리합니다.
        df['ModelID'] = modelid
        df['InputDateTime'] = datetime.now()
        df = pd.concat([df[['StdDate', 'ModelID', 'SecurityCode']], df[key_rate_columns], df[['KeySum', 'InputDateTime']]], axis=1)
        kapdb = Kapsqlalchemy(dns='kap_assetms')
        engine = kapdb.create_engine()
        df.to_sql(name='H_SECURITY_KEYRATE_DUR_PY', con=engine, if_exists='append', index=False)
        terminate_time = timeit.default_timer()  # 종료 시간 체크
        print("{i}까지의 데이터 입력하는 데 {min}분 걸렸습니다".format(i = i, min = round((terminate_time - start_time) / 60, 2)))
        # 메모리 상의 dataframe을 초기화합니다.
        df = pd.DataFrame()

# 나머지 데이터 입력하기 위해 dataframe을 정리합니다.
if len(df) > 0:
    df['ModelID'] = modelid
    df['InputDateTime'] = datetime.now()
    df = pd.concat([df[['StdDate', 'ModelID', 'SecurityCode']], df[key_rate_columns], df[['KeySum', 'InputDateTime']]], axis = 1)

    # 나머지 데이터 입력을 위해 sqlalchemy 객체를 생성합니다.
    kapdb = Kapsqlalchemy(dns='kap_assetms')
    engine = kapdb.create_engine()
    df.to_sql(name='H_SECURITY_KEYRATE_DUR_PY', con = engine, if_exists='append', index=False)
    logger.debug("나머지 데이터가 업로드되었습니다.")
terminate_time = timeit.default_timer() #종료 시간 체크
print("%f초 걸렸습니다" %(terminate_time - start_time))

