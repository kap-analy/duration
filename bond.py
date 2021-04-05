########################################################################
# 클래스 bond                                                           #
########################################################################
import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

td = '20200901' # key rate duration을 구할 날짜입니다.
issue_date = '20151013' # 채권의 발행일
due_date  = '20330310' # 채권의 만기일
amount = 10000
coupon_rate = 0.0184
num_of_interest_payment = 1 # num_of_interest_payment = 12 / interestpaycalmcnt
interest_payment_type = '11'
sectorcode = 'A102'


class Bond:

    # 채권 정보: 발행일, 만기일, 쿠폰, 이자계산지급월수
    def __init__(self, td, issue_date, due_date, amount,
                 coupon_rate, num_of_interest_payment, interest_payment_type):
        self.td = td
        self.issue_date = issue_date
        self.due_date = due_date
        self.amount = amount
        self.coupon_rate = coupon_rate
        self.num_of_interest_payment = num_of_interest_payment
        self.interest_payment_type = interest_payment_type
    # 채권 현금흐름을 계산해 주는 함수입니다.
    # 위 채권정보가 입력되고, [cash_time, cash_amt] 정보가 있는 pandas dataframe을 출력합니다.

    def bond_cf(self):
        # 날짜를 datetime 타입으로 변경합니다.
        issue_date = datetime.strptime(self.issue_date, '%Y%m%d').date()
        due_date = datetime.strptime(self.due_date, '%Y%m%d').date()
        maturity = math.ceil((due_date - issue_date).days / 365)
        td = datetime.strptime(self.td, '%Y%m%d').date()
        # 이자지급구분에 따라 계산식을 달리합니다.
        cf_td_data = []
        if self.interest_payment_type == '11': # 할인채인 경우
            cf_td = due_date
            cash_time = (cf_td - td).days / 365
            cash_amt = self.amount
            cf_td_data.append([cf_td, cash_time, cash_amt])

        elif self.interest_payment_type == '12': # 복리채인 경우
            cf_td = due_date
            cash_time = (cf_td - td).days / 365
            cash_amt = self.amount*((1+self.coupon_rate/self.num_of_interest_payment)**(self.num_of_interest_payment*maturity))
            cf_td_data.append([cf_td, cash_time, cash_amt])

        elif self.interest_payment_type == '14': # 단리채인 경우
            cf_td = due_date
            cash_time = (cf_td - td).days / 365
            cash_amt = self.amount * (1 + coupon_rate * maturity)
            cf_td_data.append([cf_td, cash_time, cash_amt])

        elif self.interest_payment_type == '15': #복5단2인 경우
            cf_td = due_date
            cash_time = (cf_td - td).days / 365
            cash_amt = self.amount * ((1 + self.coupon_rate / self.num_of_interest_payment) ** (self.num_of_interest_payment * 5))
            cash_amt += self.amount * self.coupon_rate * 2
            cf_td_data.append([cf_td, cash_time, cash_amt])

        else:  # 이표채인 경우
            diff = (due_date - issue_date).days / 365 # 날짜 차이
            cf_num = math.ceil(diff * self.num_of_interest_payment)
            interest_amount = self.amount * self.coupon_rate * 1 / self.num_of_interest_payment

            cf_td = issue_date
            # 발행일부터 만기일까지의 현금흐름 발생일을 만들어 낸다.
            i = 1
            while i <= cf_num:
                cf_td += relativedelta(months=12/self.num_of_interest_payment)
                if (cf_td - td).days > 0:
                    cash_amt = interest_amount
                    if i == cf_num:  # 마지막 현금흐름의 경우
                        if cf_td == due_date:
                            cash_amt = amount + interest_amount
                        else:
                            cf_td = due_date
                            cash_amt = amount
                            if len(cf_td_data) == 0:
                                cash_amt += interest_amount * ((due_date - td).days / 365) * self.num_of_interest_payment
                            else:
                                cash_amt += interest_amount * ((due_date - prev_cf_td).days / 365) * self.num_of_interest_payment
                    cash_time = (cf_td - td).days / 365
                    cf_td_data.append([cf_td, cash_time, cash_amt])
                    prev_cf_td = cf_td
                i += 1
        cf = pd.DataFrame(cf_td_data, columns=['cf_td', 'cash_time', 'cash_amt'])
        # cf.drop(['cf_td'], axis=1, inplace=True)
        return cf
        # for i in range(cf_num):
        #     if i == 0:
        #         cf_td = issue_date
        #     elif i == (cf_num - 1):
        #         cf_td = due_date
        #         cash_amt = self.amount
        #         # 잔존만기까지의 남은 기간만큼의 이자를 계산해서 더해 줍니다
        #         # 원래 이자금액 = (self.amount * self.coupon_rate * self.interestpaycalmcnt / 12)
        #         # 잔존만기까지의 남은 기간 (cf_td - cf[i-1][0]).days
        #         chk_td = lambda x: x if x in locals() else td
        #         cash_amt += (self.amount * self.coupon_rate * self.interestpaycalmcnt / 12) * ((cf_td - chk_td(prev_cf_td)).days / 365)/(self.interestpaycalmcnt/12)
        #     else:
        #         cf_td += relativedelta(months=self.interestpaycalmcnt)
        #         cash_amt = self.amount * self.coupon_rate * self.interestpaycalmcnt / 12
        #     # 듀레이션 산출 시점 기준으로 예전 현금흐름이면 버린다.
        #     if (cf_td - td).days < 0:
        #         next
        #     else:
        #         cash_time = (cf_td - td).days / 365
        #         cf.append([cf_td, cash_time, cash_amt])
        #         # 현금흐름이 발생했던 날을 저장해 둔다. (잔존만기까지의 이자 계산에 필요)
        #         prev_cf_td = cf_td

        # cf는 pandas dataframe 입니다.

    # 채권 현금흐름이 발생하는 시점별로 spot curve 데이터 상에서 어디에 위치하는지 찾아본다
    # 예) 4개월 후의 현금흐름은 spot curve 데이터 상에서 3개월과 6개월 사이에 위치한다

    # cf_data : num, cash_time, cash_amt
    # spot_yield_data : key_rate, yield
    # 채권 가격을 반환해 줍니다.

    def price(self, cf_data, spot_yield_data):
        apply_yield = []
        for i in range(len(cf_data)):
            chk_value = cf_data.iloc[i]['cash_time']
            chk_data = spot_yield_data.iloc[:]['key_rate'].values
            cash_idx = search_number_in_array(chk_value, chk_data)
            # search_number가 array 데이터 중 숫자 크기상으로 어디에 위치하는지를 반환합니다.
            if cash_idx == 0:
                # 다음 현금흐름 발생시점이 3개월 미만인 경우 3M spot yield를 쓴다
                apply_yield_value = spot_yield_data.iloc[0]['yield']
            elif cash_idx == len(spot_yield_data):
                # 현금흐름 발생시점이 30년을 초과하는 경우 30Y의 spot yield를 쓴다.
                apply_yield_value = spot_yield_data.iloc[len(spot_yield_data)-1]['yield']
            else:
                apply_yield_value= interpolate(cf_data.iloc[i]['cash_time'], spot_yield_data, 'key_rate', 'yield')
                # data_diff = spot_yield_data.iloc[cash_idx] - spot_yield_data.iloc[cash_idx - 1]
                # apply_yield_value = spot_yield_data.iloc[cash_idx - 1]['yield']
                # apply_yield_value += data_diff['yield'] / data_diff['key_rate'] * (cf_data.iloc[i]['cash_time'] - spot_yield_data.iloc[cash_idx - 1]['key_rate'])
            apply_yield.append(apply_yield_value)
        cf_data['apply_yield'] = apply_yield
        if interest_payment_type == '11': # 할인채의 경우
            bond_price = amount / ((1 + cf_data['apply_yield'] /100) ** cf_data['cash_time'])
        else:
            cf_data['pv_factor'] = 1 / (1 + cf_data['apply_yield'] / 100 / num_of_interest_payment) ** (cf_data.index + 1)
            cf_data['pv_cash_amt'] = cf_data['pv_factor'] * cf_data['cash_amt']
            bond_price = cf_data['pv_cash_amt'].sum()

        return bond_price

    def key_rate_duration(self, cf_data, spot_yield_data, delta=0.01):

        # delta는 금리변동분입니다. % 단위로 씁니다. 1bp 는 0.01 입니다.

        price = self.price(cf_data, spot_yield_data)
        key_rate_duration = []
        if interest_payment_type == '11' or '12' or '14':  # 할인, 단리, 복리채의 경우
            i=0
            chk_value = cf_data.iloc[i]['cash_time']
            chk_data = spot_yield_data.iloc[:]['key_rate'].values
            cash_idx = search_number_in_array(chk_value, chk_data)
            for i in range(len(spot_yield_data)):
                 if i <= cash_idx-3:
                     duration = 0
                 else:
                    spot_curve_plus = spot_yield_data.copy()
                    spot_curve_minus = spot_yield_data.copy()
                    spot_curve_plus.iloc[i]['yield'] += delta
                    spot_curve_minus.iloc[i]['yield'] -= delta
                    price_plus = self.price(cf_data, spot_curve_plus)
                    price_minus = self.price(cf_data, spot_curve_minus)
                    duration = (price_minus - price_plus) / (2 * price * delta / 100)
                 key_rate_duration.append(duration)
        else:
            for i in range(len(spot_yield_data)):
                spot_curve_plus = spot_yield_data.copy()
                spot_curve_minus = spot_yield_data.copy()

                spot_curve_plus.iloc[i]['yield'] += delta
                spot_curve_minus.iloc[i]['yield'] -= delta

                price_plus = self.price(cf_data,  spot_curve_plus)
                price_minus = self.price(cf_data, spot_curve_minus)
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


# spot curve interpolation을 위한 함수입니다.

def interpolate(x_val, df, known_x, known_y):
    # known_x, known_y : 실측값 x,y 입니다.
    # x_val : interpolation 하고자 하는 결측값 x 입니다.
    return np.interp([x_val], df[known_x], df[known_y])
