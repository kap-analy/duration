########################################################################
# 클래스 bond                                                           #
########################################################################
import numpy as np
import pandas as pd

class Bond:

    def __init__(self, cf_data):
        self.cf_data = cf_data

    # 채권 현금흐름이 발생하는 시점별로 spot curve 데이터 상에서 어디에 위치하는지 찾아본다
    # 예) 4개월 후의 현금흐름은 spot curve 데이터 상에서 3개월과 6개월 사이에 위치한다

    # cf_data : num, cash_time, cash_amt
    # spot_curve_data : key_rate, yield
    # 채권 가격을 반환해 줍니다.

    def price(self, spot_curve_data, interestpaycalmcnt = 6):
        apply_yield = []
        for i in range(len(self.cf_data)):
            chk_value = self.cf_data.iloc[i]['cash_time']
            chk_data = spot_curve_data.iloc[:]['key_rate'].values
            cash_idx = search_number_in_array(chk_value, chk_data)
            # search_number가 array 데이터 중 숫자 크기상으로 어디에 위치하는지를 반환합니다.
            #         if cash_idx == 0:
            #             apply_yield.append(spot_curve_data.iloc[i]['yield'].values)

            #         elif cash_idx == len(spot_curve_data) - 1 :
            #             apply_yield.append(spot_curve_data.iloc[len(spot_curve_data)]['yield'].values)

            #         else:
            data_diff = spot_curve_data.iloc[cash_idx] - spot_curve_data.iloc[cash_idx - 1]
            apply_yield_value = spot_curve_data.iloc[cash_idx - 1]['yield']
            apply_yield_value += data_diff['yield'] / data_diff['key_rate'] * (
                        self.cf_data.iloc[i]['cash_time'] - spot_curve_data.iloc[cash_idx - 1]['key_rate'])
            apply_yield.append(apply_yield_value)

        self.cf_data['apply_yield'] = apply_yield
        self.cf_data['pv_factor'] = 1 / (1 + self.cf_data['apply_yield'] / 100 / (12 / interestpaycalmcnt)) ** (self.cf_data['num'])
        self.cf_data['pv_cash_amt'] = self.cf_data['pv_factor'] * self.cf_data['cash_amt']

        bond_price = self.cf_data['pv_cash_amt'].sum()
        return bond_price

    def key_rate_duration(self, spot_curve_data, interestpaycalmcnt=6, delta=0.01):

        # delta는 금리변동분입니다. % 단위로 씁니다. 1bp 는 0.01 입니다.

        price = self.price(spot_curve_data, interestpaycalmcnt)
        key_rate_duration = []
        for i in range(len(spot_curve_data)):
            spot_curve_plus = spot_curve_data.copy()
            spot_curve_minus = spot_curve_data.copy()

            spot_curve_plus.iloc[i]['yield'] += delta
            spot_curve_minus.iloc[i]['yield'] -= delta

            price_plus = self.price(spot_curve_plus, interestpaycalmcnt)
            price_minus = self.price(spot_curve_minus, interestpaycalmcnt)
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