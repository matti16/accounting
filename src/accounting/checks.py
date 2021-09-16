from accounting.config import BankAccountConfig, IncomeStatementConfig

from accounting.readers import BalanceData

class AccountChecks:
    suffix_bank = " Banca"
    suffix_income = " Bilancio"

    def __init__(self, file_bank, file_income, bank_fmt="csv", income_fmt="xlsx"):
        self.bank_data = BalanceData(
            file_bank,
            bank_fmt,
            BankAccountConfig.col_plus,
            BankAccountConfig.col_minus,
            BankAccountConfig.col_amount,
            BankAccountConfig.col_date,
            BankAccountConfig.col_description,
            BankAccountConfig.skiprows
        )

        self.income_data = BalanceData(
            file_income,
            income_fmt,
            IncomeStatementConfig.col_plus,
            IncomeStatementConfig.col_minus,
            IncomeStatementConfig.col_amount,
            IncomeStatementConfig.col_date,
            IncomeStatementConfig.col_description, 
            IncomeStatementConfig.skiprows
        )

    
    def compute_differences(self):
        agg_bank = self.bank_data.aggregate_by_amount()
        agg_income = self.income_data.aggregate_by_amount()

        merged_data = agg_bank.merge(
            agg_income, 
            how="outer",
            left_on=BankAccountConfig.col_amount, 
            right_on=IncomeStatementConfig.col_amount, 
            suffixes=(self.suffix_bank, self.suffix_income)
        )

        differences_data = merged_data[
            (merged_data[BankAccountConfig.col_amount] != merged_data[IncomeStatementConfig.col_amount]) \
            | (merged_data[f"{BalanceData.count_col_name}{self.suffix_bank}"] != merged_data[f"{BalanceData.count_col_name}{self.suffix_income}"])
        ]
        return differences_data

    def format_differences(self, differences_data):
        differences_data["sort_col_1"] = differences_data[f"{BalanceData.date_col_name}{self.suffix_bank}"]\
            .combine_first(differences_data[f"{BalanceData.date_col_name}{self.suffix_income}"])
        differences_data["sort_col_2"] = differences_data[BankAccountConfig.col_amount]\
            .combine_first(differences_data[IncomeStatementConfig.col_amount])
        
        differences_data = differences_data.sort_values(["sort_col_1", "sort_col_2"])
        differences_data.loc[
            differences_data[f"{BalanceData.count_col_name}{self.suffix_bank}"] + \
            differences_data[f"{BalanceData.count_col_name}{self.suffix_income}"] > 2,
            [
                f"{BalanceData.date_col_name}{self.suffix_bank}",
                f"{BalanceData.desc_col_name}{self.suffix_bank}",
                f"{BalanceData.desc_col_name}{self.suffix_income}",
                f"{BalanceData.date_col_name}{self.suffix_income}"
            ]
        ] = ""

        columns = [
            f"{BalanceData.date_col_name}{self.suffix_bank}",
            f"{BalanceData.desc_col_name}{self.suffix_bank}",
            f"{BalanceData.count_col_name}{self.suffix_bank}",
            BankAccountConfig.col_amount,
            IncomeStatementConfig.col_amount,
            f"{BalanceData.count_col_name}{self.suffix_income}",
            f"{BalanceData.desc_col_name}{self.suffix_income}",
            f"{BalanceData.date_col_name}{self.suffix_income}",
        ]

        differences_data = differences_data[columns]
        return differences_data

    def get_differences(self):
        diff = self.compute_differences()
        diff = self.format_differences(diff)
        return diff
