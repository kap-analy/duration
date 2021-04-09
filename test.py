from bond import *
from get_data import *
from logging_pack import *


securitycode = 'KR2005011334'
td = '20210302'
amt = 10000

bond_info = get_bond_info(td=td)
idx = bond_info[bond_info.securitycode == securitycode].index
info = bond_info.iloc[idx].squeeze()
info

issue_date = datetime.strptime(info['issue_date'], '%Y%m%d').date()
due_date = datetime.strptime(info['due_date'], '%Y%m%d').date()
td = datetime.strptime(td, '%Y%m%d').date()

# Bond 객체를 생성합니다.
bond = Bond(td=td, issue_date=issue_date, due_date=due_date,
                amt=amt, coupon_rate=info['coupon_rate'],
                num_of_interest_payment=info['num_of_interest_payment'],
                interest_payment_type=info['interest_payment_type'],
                payment_type=info['payment_type'])

if info['payment_type'] == '2':
    amortized_info = get_amortized_bond(info['securitycode'])
    bond_cf = bond.amortized_bond_cf()
else:
    bond_cf = bond.bond_cf()
print("현금흐름입니다", bond_cf)
