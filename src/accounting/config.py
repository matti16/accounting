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

class VatsConfig:
    col_plus = 10
    col_minus = 11
    col_date = 0
    col_description = 5
    skiprows = 1

    def __init__(self, col_amount):
        self.col_amount = col_amount