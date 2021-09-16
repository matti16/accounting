class BankAccountConfig:
    col_plus = 2
    col_minus = 2
    col_date = 0
    col_description = 3
    skiprows = None
    col_amount = "Cifra Banca"


class IncomeStatementConfig:
    col_plus = 3
    col_minus = 4
    col_date = 0
    col_description = 2
    skiprows = 1
    col_amount = "Cifra Bilancio"