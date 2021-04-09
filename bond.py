########################################################################
# 클래스 bond                                                           #
########################################################################
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dfply import *


# Bond 클래스 생성해 줄 때 날짜 타입은 datetime 으로 입력합니다.

class Bond:

    # 채권 정보: 발행일, 만기일, 쿠폰, 이자계산지급월수
    def __init__(self, td, issue_date, due_date, amt,
                 coupon_rate, num_of_interest_payment, interest_payment_type, payment_type):
        self.td = td
        self.issue_date = issue_date
        self.due_date = due_date
        self.amt = amt
        self.coupon_rate = coupon_rate
        self.num_of_interest_payment = num_of_interest_payment
        self.interest_payment_type = interest_payment_type
        self.payment_type = payment_type

    # 채권 현금흐름을 계산해 주는 함수입니다.
    # 위 채권정보가 입력되고, [cf_time, cash_amt] 정보가 있는 pandas dataframe을 출력합니다.

    def bond_cf(self):
        maturity = round((self.due_date - self.issue_date).days / 365)
        # 이자지급구분에 따라 계산식을 달리합니다.
        cf_td_data = []
        if self.interest_payment_type == '11': # 할인채인 경우
            cf_td = self.due_date
            cf_time = (cf_td - self.td).days / 365
            cash_amt = self.amt
            cf_td_data.append([cf_td, cf_time, cash_amt])

        elif self.interest_payment_type == '12': # 복리채인 경우
            cf_td = self.due_date
            cf_time = (cf_td - self.td).days / 365
            cash_amt = self.amt*((1+self.coupon_rate/self.num_of_interest_payment)**(self.num_of_interest_payment*maturity))
            cf_td_data.append([cf_td, cf_time, cash_amt])

        elif self.interest_payment_type == '14': # 단리채인 경우
            cf_td = self.due_date
            cf_time = (cf_td - self.td).days / 365
            cash_amt = self.amt * (1 + self.coupon_rate * maturity)
            cf_td_data.append([cf_td, cf_time, cash_amt])

        elif self.interest_payment_type == '15': #복5단2인 경우
            cf_td = self.due_date
            cf_time = (cf_td - self.td).days / 365
            cash_amt = self.amt * ((1 + self.coupon_rate / self.num_of_interest_payment) ** (self.num_of_interest_payment * 5))
            cash_amt += self.amt * self.coupon_rate * 2
            cf_td_data.append([cf_td, cf_time, cash_amt])

        else:  # 이표채인 경우
            diff = (self.due_date - self.issue_date).days / 365 # 날짜 차이
            cf_num = round(diff * self.num_of_interest_payment)
            interest_amt = self.amt * self.coupon_rate * 1 / self.num_of_interest_payment

            cf_td = self.issue_date
            # 발행일부터 만기일까지의 현금흐름 발생일을 만들어 낸다.
            i = 1
            while i <= cf_num:
                cf_td += relativedelta(months=12/self.num_of_interest_payment)
                if (cf_td - self.td).days > 0:
                    cash_amt = interest_amt
                    if i == cf_num:  # 마지막 현금흐름의 경우
                        if cf_td == self.due_date:
                            cash_amt = self.amt + interest_amt
                        else:
                            cf_td = self.due_date
                            cash_amt = self.amt
                            if len(cf_td_data) == 0:
                                cash_amt += interest_amt * ((self.due_date - self.td).days / 365) * self.num_of_interest_payment
                            else:
                                cash_amt += interest_amt * ((self.due_date - prev_cf_td).days / 365) * self.num_of_interest_payment
                    cf_time = (cf_td - self.td).days / 365
                    cf_td_data.append([cf_td, cf_time, cash_amt])
                    prev_cf_td = cf_td
                i += 1
        cf = pd.DataFrame(cf_td_data, columns=['cf_td', 'cf_time', 'cash_amt'])
        return cf

    def amortized_bond_cf(self, defered_period, amortized_period,
                          num_of_amortized_amt, interest_defered):

        diff = (self.due_date - self.issue_date).days / 365  # 날짜 차이
        cf_num = round(diff * self.num_of_interest_payment)
        remain_amt = self.amt
        prepay_amt = self.amt / (amortized_period * num_of_amortized_amt)

        cf_td = self.issue_date
        cf_td_data = []
        i = 1
        if defered_period == 0: # 거치기간이 없는 경우, 다음 현금흐름부터 바로 상환액과 이자금액을 합해 현금흐름을 만든다.
            while i <= cf_num:
                cf_td += relativedelta(months=12 / self.num_of_interest_payment)
                if (cf_td - self.td).days > 0:
                    # 이 부분이 차이가 난다.
                    cash_amt = prepay_amt + remain_amt * self.coupon_rate * 1 / self.num_of_interest_payment
                    cf_time = (cf_td - self.td).days / 365
                    cf_td_data.append([cf_td, cf_time, cash_amt])
                i += 1
                remain_amt -= prepay_amt
        else:  # 거치기간이 있는 경우
            if interest_defered == 0: # 이차 거치기간이 없는 경우
                while i <= cf_num: # 먼저 모든 현금흐름을 생성한다.
                    cf_td += relativedelta(months=12 / self.num_of_interest_payment)
                    cf_time = (cf_td - self.td).days / 365
                    if ((cf_td - self.issue_date).days / 365) >= defered_period + 1:  # 거치 기간 이후인 경우
                        cash_amt = remain_amt * self.coupon_rate * 1 / self.num_of_interest_payment
                        # 상환금 지급 주기가 이자 지급 주기가 차이가 나는 경우가 있다.
                        # num_of_amortized_amt을 체크한다.
                        if num_of_amortized_amt == self.num_of_interest_payment:
                            cash_amt += prepay_amt
                            remain_amt -= prepay_amt
                        else:
                            if i % self.num_of_interest_payment == 0:
                                cash_amt += prepay_amt
                                remain_amt -= prepay_amt
                        cf_td_data.append([cf_td, cf_time, cash_amt])
                    else: # 거치 기간이 경과하지 않은 경우
                        cash_amt = remain_amt * self.coupon_rate * 1 / self.num_of_interest_payment
                        cf_td_data.append([cf_td, cf_time, cash_amt])
                    i += 1
                # 아래에서 dataframe을 만든 후 현재 시점 이전까지의 현금흐름 데이터를 삭제한다.

            else:
                # 이자 거치기간이 있는 경우. 현금흐름은 발행일로부터 거치기간이 지난 후부터 생긴다.
                # 이자 거치기간이 있는 경우, 복리채이다.
                while i <= cf_num:
                    cf_td += relativedelta(months=12 / self.num_of_interest_payment)
                    if ((cf_td - self.issue_date).days / 365) >= defered_period + 1:  # 거치 기간 이후인 경우
                        if round((cf_td - self.issue_date).days / 365) == defered_period + 1:
                            cash_amt = remain_amt * ((1 + self.coupon_rate / self.num_of_interest_payment) ** (
                                    self.num_of_interest_payment * (defered_period + 1)))
                            cash_amt -= remain_amt
                        # 이 부분이 차이가 난다.
                        else:
                            cash_amt = remain_amt * self.coupon_rate * 1 / self.num_of_interest_payment
                        # 상환금 지급 주기가 이자 지급 주기가 차이가 나는 경우가 있다.
                        # num_of_amortized_amt을 체크한다.
                        if num_of_amortized_amt == self.num_of_interest_payment:
                            cash_amt += prepay_amt
                            remain_amt -= prepay_amt
                        else:
                            if i % self.num_of_interest_payment == 0:
                                cash_amt += prepay_amt
                                remain_amt -= prepay_amt
                        cf_time = (cf_td - self.td).days / 365
                        cf_td_data.append([cf_td, cf_time, cash_amt])

                    i += 1
        cf = pd.DataFrame(cf_td_data, columns=['cf_td', 'cf_time', 'cash_amt'])
        # 현재 시점 이후 현금흐름 데이터만 남긴다.
        cf = cf[cf.cf_time > 0]
        return cf
    # cf_data : num, cf_time, cash_amt
    # spot_yield_data : key_rate, yield_rate
    # 채권 가격을 반환해 줍니다.

    def price(self, cf_data, spot_yield_data, roop_number = 0):
        apply_yield = []
        cf_index = []
        for i in range(len(cf_data)):
            chk_value = cf_data.iloc[i]['cf_time']
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
                data_diff = spot_yield_data.iloc[cash_idx] - spot_yield_data.iloc[cash_idx - 1]
                apply_yield_value = spot_yield_data.iloc[cash_idx - 1]['yield']
                apply_yield_value += data_diff['yield'] / data_diff['key_rate'] * (cf_data.iloc[i]['cf_time'] - spot_yield_data.iloc[cash_idx - 1]['key_rate'])
            apply_yield.append(apply_yield_value)
            cf_index.append(cash_idx)

        cf_data['cf_index'] = cf_index
        cf_data['apply_yield'] = apply_yield
        cf_data['pv_factor'] = 1 / ((1 + cf_data['apply_yield'] / 100) ** cf_data['cf_time'])
        cf_data['pv_cash_amt'] = cf_data['pv_factor'] * cf_data['cash_amt']
        bond_price = cf_data['pv_cash_amt'].sum()
        if roop_number == 1:
            roop_from, roop_to = min(cf_data['cf_index']), max(cf_data['cf_index'])
            # key rate duration은 현금흐름 발생 시간으로부터 앞뒤로 한 단위 더 roop를 돌릴 것입니다.
            # 어느 채권의 현금흐름이 6개월에서 3년 사이에만 발생하였다면 key rate duration은 3개월에서 4년 구간만 산출합니다.
            # roop_from과 roop_to는 0에서 14까지의 값이 나옵니다. roop_from이 0인 경우 조정 roop_from은 0, roop_from이 14인 14로 조정합니다.
            roop_from = roop_from - 1 if roop_from >= 1 else roop_from
            roop_to = roop_to + 1 if roop_to <= 13 else roop_to

            return bond_price, roop_from, roop_to
        else:
            return bond_price

    def new_price(self, cf_data, spot_yield_data, roop_number = 0):
        # input
        # cf_data : num, cf_time, cash_amt
        # spot_yield_data : key_rate, yield
        spot_yield_data.columns = ['cf_time', 'yield']
        # 현금흐름 데이터와 key rate별 spot 금리 데이터를 병합합니다.
        df = spot_yield_data.merge(cf_data, how='outer', on='cf_time').sort_values('cf_time')
        df['time_index'] = np.select([df['cf_time'] < 0.5, df['cf_time'] < 0.75, df['cf_time'] < 1,
                                      df['cf_time'] < 1.5, df['cf_time'] < 2, df['cf_time'] < 2.5,
                                      df['cf_time'] < 3, df['cf_time'] < 4, df['cf_time'] < 5,
                                      df['cf_time'] < 7, df['cf_time'] < 10, df['cf_time'] < 20, df['cf_time'] < 30],
                                     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                     default=0)

        # 현금흐름 발생 시점별로 key rate 어느 구간에 속하는지 알아냅니다.
        pre_df = df.loc[df['time_index']][['cf_time', 'yield']]
        pre_df.columns = ['pre_cf_time', 'pre_yield']

        next_df = df.loc[df['time_index'] + 1][['cf_time', 'yield']]
        next_df.columns = ['next_cf_time', 'next_yield']
        # 위 세 가지 데이터를 병합하기 위해 각 데이터프레임의 인덱스를 초기화합니다.
        df.reset_index(inplace=True)
        pre_df.reset_index(inplace=True)
        next_df.reset_index(inplace=True)
        new_df = pd.concat([df, pre_df, next_df], axis=1)
        # 아래 코드로 현금흐름 발생 시점만 남겼습니다.
        new_df = new_df[new_df['cf_td'].notna()].reset_index()

        # 현금흐름이 어느 key rate 구간에서 발생하는지 알았으니,
        # 그러한 정보를 가지고 선형보간법을 사용하여 현금흐름 할인율(apply_yield),
        # 현가계수(pv_factor), 현가(pv_cash_amt)를 산출합니다. 현가를 더한 값이 채권 가격입니다.

        new_df['gradient'] = (new_df['next_yield'] - new_df['pre_yield']) / (
                    new_df['next_cf_time'] - new_df['pre_cf_time'])
        new_df['apply_yield'] = new_df['pre_yield'] + new_df['gradient'] * (new_df['cf_time'] - new_df['pre_cf_time'])
        # 현금흐름 발생시점이 3개월 미만인 경우 3개월 spot yield 사용
        # 현금흐름 발생시점이 30년 초과하는 경우 30년 spot yield 사용
        new_df.loc[new_df.cf_time < 0.25, 'apply_yield'] = spot_yield_data.iloc[0]['yield']
        new_df.loc[new_df.cf_time >= 30, 'apply_yield'] = spot_yield_data.iloc[13]['yield']
        new_df['pv_factor'] = 1 / (1 + new_df['apply_yield'] / 100 / self.num_of_interest_payment) ** (new_df.index + 1)
        new_df['pv_cash_amt'] = new_df['pv_factor'] * new_df['cash_amt']

        bond_price = new_df['pv_cash_amt'].sum()
        # 채권 가격 외에 채권 현금흐름의 발생 기간을 알려주는 roop_from, roop_to도 반환합니다.
        # 이것은 key_rate_duration 산출 시 작업시간을 효율화 해 줄 것입니다.
        if roop_number == 1:
            roop_from, roop_to = min(new_df['time_index']), max(new_df['time_index'])
            # key rate duration은 현금흐름 발생 시간으로부터 앞뒤로 한 단위 더 roop를 돌릴 것입니다.
            # 어느 채권의 현금흐름이 6개월에서 3년 사이에만 발생하였다면 key rate duration은 3개월에서 4년 구간만 산출합니다.
            # roop_from과 roop_to는 0에서 14까지의 값이 나옵니다. roop_from이 0인 경우 조정 roop_from은 0, roop_from이 14인 14로 조정합니다.
            roop_from = roop_from - 1 if roop_from >= 1 else roop_from
            roop_to = roop_to + 1 if roop_to <= 13 else roop_to

            return bond_price, roop_from, roop_to
        else:
            return bond_price



    def key_rate_duration(self, cf_data, spot_yield_data, delta=0.01):

        # delta는 금리변동분입니다. % 단위로 씁니다. 1bp 는 0.01 입니다.

        price, roop_from, roop_to = self.price(cf_data, spot_yield_data, roop_number=1)
        # price = self.price(cf_data, spot_yield_data)
        key_rate_duration = [0.0] * 14
        # key_rate_duration = []
        # for i in range(len(spot_yield_data)):
        for i in np.arange(roop_from, roop_to):
            spot_curve_plus = spot_yield_data.copy()
            spot_curve_minus = spot_yield_data.copy()

            spot_curve_plus.loc[i, 'yield'] += delta
            spot_curve_minus.loc[i, 'yield'] -= delta

            # price_plus = self.new_price(cf_data,  spot_curve_plus)
            # price_minus = self.new_price(cf_data, spot_curve_minus)
            price_plus = self.price(cf_data, spot_curve_plus)
            price_minus = self.price(cf_data, spot_curve_minus)
            duration = (price_minus - price_plus) / (2 * price * delta / 100)
            key_rate_duration[i] = duration
            # key_rate_duration.append(duration)

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