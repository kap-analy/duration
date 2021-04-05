from bond import *
from get_data import *
from logging_pack import *


securitycode = 'KR2099022J87'
td = '20200904'
amount = 10000


# 해당 날짜의 spot yield를 받아옵니다.
spot_yield_data = get_spot_yield(td)

info = get_one_bond_info(td = td, securitycode=securitycode)
info = info.iloc[0]
# Bond 객체를 생성합니다.
bond = Bond(td=td, issue_date=info['issue_date'], due_date=info['due_date'],
            amount=amount, coupon_rate=info['coupon_rate'],
            num_of_interest_payment=info['num_of_interest_payment'],
            interest_payment_type=info['interest_payment_type'])

bond_cf = bond.bond_cf()
print("현금흐름입니다", bond_cf)

yield_data = spot_yield_data.loc[info['sectorcode']]
yield_data = pd.DataFrame(yield_data).reset_index()
yield_data.columns=['key_rate', 'yield']
krd = bond.key_rate_duration(cf_data=bond_cf, spot_yield_data=yield_data, delta=0.01)
krd_df = pd.DataFrame(krd).transpose()

krd_df.columns = ['M3', 'M6', 'M9', 'Y1', 'Y1.5', 'Y2', 'Y2.5', 'Y3', 'Y4', 'Y5', 'Y7', 'Y10', 'Y20', 'Y30']

krd_df = krd_df.assign(**{'StdDate': datetime.strptime(td, '%Y%m%d').date(),
                            'SecurityCode': info['securitycode'],
                            'KeySum': np.sum(krd, axis = 0)})
print(krd_df)
