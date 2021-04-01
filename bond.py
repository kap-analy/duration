########################################################################
# 클래스 bond                                                           #
########################################################################
import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

td = '20200901' # key rate duration을 구할 날짜입니다.
issue_date = '20150626' # 채권의 발행일
due_date  = '20300625' # 채권의 만기일
nextpaydate = '20200925'
amount = 10000
coupon_rate = 0.02835
interestpaycalmcnt = 4
Sector = 'B300'
code = 'KR2005041562'

class Bond:

    # 채권 정보: 발행일, 만기일, 쿠폰, 이자계산지급월수
    def __init__(self, td, issue_date, due_date, nextpaydate, amount,
                 coupon_rate, interestpaycalmcnt):
        self.td = td
        self.issue_date = issue_date
        self.due_date = due_date
        self.nextpaydate = nextpaydate
        self.amount = amount
        self.coupon_rate = coupon_rate
        self.interestpaycalmcnt = interestpaycalmcnt

    # 채권 현금흐름을 계산해 주는 함수입니다.
    # 위 채권정보가 입력되고, [cash_time, cash_amt] 정보가 있는 pandas dataframe을 출력합니다.

    def bond_cf(self):
        # 날짜를 datetime 타입으로 변경합니다.
        issue_date = datetime.strptime(self.issue_date, '%Y%m%d').date()
        due_date = datetime.strptime(self.due_date, '%Y%m%d').date()
        nextpaydate = datetime.strptime(self.nextpaydate, '%Y%m%d').date()
        td = datetime.strptime(self.td, '%Y%m%d').date()
        diff = (due_date - td).days / 365  # 날짜 차이
        cf_num = math.ceil(diff * self.interestpaycalmcnt)

        cf = []

        for i in range(cf_num):
            if i == 0:
                cf_td = nextpaydate
            if i == cf_num-1:
                cf_td = due_date
                cash_amt = self.amount + self.amount * self.coupon_rate / self.interestpaycalmcnt
            else:
                cf_td += relativedelta(months=12/ self.interestpaycalmcnt)
                cash_amt = self.amount * self.coupon_rate / self.interestpaycalmcnt
            cash_time = (cf_td - td).days / 365
            cf.append([cf_td, cash_time, cash_amt])
        cf = pd.DataFrame(cf, columns=['cf_td', 'cash_time', 'cash_amt'])
        cf.drop(['cf_td'], axis=1, inplace=True)
        # cf는 pandas dataframe 입니다.
        return cf
    # 채권 현금흐름이 발생하는 시점별로 spot curve 데이터 상에서 어디에 위치하는지 찾아본다
    # 예) 4개월 후의 현금흐름은 spot curve 데이터 상에서 3개월과 6개월 사이에 위치한다

    # cf_data : num, cash_time, cash_amt
    # spot_yield_data : key_rate, yield
    # 채권 가격을 반환해 줍니다.

    def price(self, spot_yield_data):
        cf_data = self.bond_cf()
        apply_yield = []
        for i in range(len(cf_data)):
            chk_value = cf_data.iloc[i]['cash_time']
            chk_data = spot_yield_data.iloc[:]['key_rate'].values
            cash_idx = search_number_in_array(chk_value, chk_data)
            # search_number가 array 데이터 중 숫자 크기상으로 어디에 위치하는지를 반환합니다.
            #         if cash_idx == 0:
            #             apply_yield.append(spot_yield_data.iloc[i]['yield'].values)

            #         elif cash_idx == len(spot_yield_data) - 1 :
            #             apply_yield.append(spot_yield_data.iloc[len(spot_yield_data)]['yield'].values)

            #         else:
            data_diff = spot_yield_data.iloc[cash_idx] - spot_yield_data.iloc[cash_idx - 1]
            apply_yield_value = spot_yield_data.iloc[cash_idx - 1]['yield']
            apply_yield_value += data_diff['yield'] / data_diff['key_rate'] * (
                        cf_data.iloc[i]['cash_time'] - spot_yield_data.iloc[cash_idx - 1]['key_rate'])
            apply_yield.append(apply_yield_value)

        cf_data['apply_yield'] = apply_yield
        cf_data['pv_factor'] = 1 / (1 + cf_data['apply_yield'] / 100 / (12 / self.interestpaycalmcnt)) ** (cf_data.index + 1)
        cf_data['pv_cash_amt'] = cf_data['pv_factor'] * cf_data['cash_amt']

        bond_price = cf_data['pv_cash_amt'].sum()
        return bond_price

    def key_rate_duration(self, spot_yield_data, delta=0.01):

        # delta는 금리변동분입니다. % 단위로 씁니다. 1bp 는 0.01 입니다.

        price = self.price(spot_yield_data)
        key_rate_duration = []
        for i in range(len(spot_yield_data)):
            spot_curve_plus = spot_yield_data.copy()
            spot_curve_minus = spot_yield_data.copy()

            spot_curve_plus.iloc[i]['yield'] += delta
            spot_curve_minus.iloc[i]['yield'] -= delta

            price_plus = self.price(spot_curve_plus)
            price_minus = self.price(spot_curve_minus)
            duration = (price_minus - price_plus) / (2 * price * delta / 100)
            key_rate_duration.append(duration)

        return key_rate_duration





# 채권 가격 연산에 필요한 함수입니다.

def search_number_in_array(search_number, number_array):
    # number_array: 숫자로 이루어진 pandas series 입니다
    # search_number: 숫자입니다.
    # search_number가 array 데이터 중 숫자 크기상으로 어디에 위치하는지를 반환합니다.
    # 숫자가 0.3이고, [0.25, 0.5, 0.75] 배열에서의 위치하는 곳은 두 번째 입니다.
    # 파이썬 인덱싱 상 1을 반환합니다
    data = np.concatenate((number_array, pd.Series(search_number)))
    data = np.sort(data)
    idx = np.where(data == search_number)[0][0]
    return idx