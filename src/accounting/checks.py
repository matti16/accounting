import copy

from accounting.config import BankAccountConfig, IncomeStatementConfig, VatsConfig
from accounting.readers import BalanceData


class Checks:
    suffix_1 = " 1"
    suffix_2 = " 2"

    def __init__(self, data_1, data_2, config_1, config_2):
        self.data_1 = data_1
        self.data_2 = data_2
        self.config_1 = config_1
        self.config_2 = config_2
    
    def compute_differences(self):
        agg_1 = self.data_1.aggregate_by_amount()
        agg_2= self.data_2.aggregate_by_amount()

        merged_data = agg_1.merge(
            agg_2, 
            how="outer",
            left_on=self.config_1.col_amount, 
            right_on=self.config_2.col_amount, 
            suffixes=(self.suffix_1, self.suffix_2)
        )

        differences_data = merged_data[
            (merged_data[self.config_1.col_amount] != merged_data[self.config_2.col_amount]) \
            | (merged_data[f"{BalanceData.count_col_name}{self.suffix_1}"] != merged_data[f"{BalanceData.count_col_name}{self.suffix_2}"])
        ]
        return differences_data

    def format_differences(self, differences_data):
        differences_data["sort_col_1"] = differences_data[f"{BalanceData.date_col_name}{self.suffix_1}"]\
            .combine_first(differences_data[f"{BalanceData.date_col_name}{self.suffix_2}"])
        
        differences_data["sort_col_2"] = differences_data[self.config_1.col_amount]\
            .combine_first(differences_data[self.config_2.col_amount])
        
        differences_data = differences_data.sort_values(["sort_col_1", "sort_col_2"])
        differences_data.loc[
            differences_data[f"{BalanceData.count_col_name}{self.suffix_1}"] + \
            differences_data[f"{BalanceData.count_col_name}{self.suffix_2}"] > 2,
            [
                f"{BalanceData.date_col_name}{self.suffix_1}",
                f"{BalanceData.desc_col_name}{self.suffix_1}",
                f"{BalanceData.desc_col_name}{self.suffix_2}",
                f"{BalanceData.date_col_name}{self.suffix_2}"
            ]
        ] = ""

        columns = [
            f"{BalanceData.date_col_name}{self.suffix_1}",
            f"{BalanceData.desc_col_name}{self.suffix_1}",
            f"{BalanceData.count_col_name}{self.suffix_1}",
            self.config_1.col_amount,
            self.config_2.col_amount,
            f"{BalanceData.count_col_name}{self.suffix_2}",
            f"{BalanceData.desc_col_name}{self.suffix_2}",
            f"{BalanceData.date_col_name}{self.suffix_2}",
        ]

        differences_data = differences_data[columns]
        return differences_data

    def get_differences(self):
        diff = self.compute_differences()
        diff = self.format_differences(diff)
        return diff


class AccountChecks(Checks):
    suffix_1 = " Banca"
    suffix_2 = " Bilancio"

    def __init__(self, file_bank, file_income, bank_fmt="csv", income_fmt="xlsx"):
        bank_data = BalanceData(
            file_bank,
            bank_fmt,
            BankAccountConfig.col_plus,
            BankAccountConfig.col_minus,
            BankAccountConfig.col_amount,
            BankAccountConfig.col_date,
            BankAccountConfig.col_description,
            BankAccountConfig.skiprows
        )

        income_data = BalanceData(
            file_income,
            income_fmt,
            IncomeStatementConfig.col_plus,
            IncomeStatementConfig.col_minus,
            IncomeStatementConfig.col_amount,
            IncomeStatementConfig.col_date,
            IncomeStatementConfig.col_description, 
            IncomeStatementConfig.skiprows
        )

        super().__init__(bank_data, income_data, BankAccountConfig, IncomeStatementConfig)


class VatChecks(Checks):
    suffix_1 = " Dare"
    suffix_2 = " Avere"

    def __init__(self, file_vat, fmt="xlsx"):
        vats_config = VatsConfig("Cifra")
        vat_data_1 = BalanceData(
            file_vat,
            fmt,
            vats_config.col_plus,
            vats_config.col_minus,
            vats_config.col_amount,
            vats_config.col_date,
            vats_config.col_description,
            vats_config.skiprows,
            ignore_neg=True
        )

        vat_data_2 = copy.deepcopy(vat_data_1)
        vat_data_1.data = vat_data_1.data[~vat_data_1.data[vat_data_1.data.columns[vats_config.col_plus]].isna()]
        vat_data_2.data = vat_data_2.data[~vat_data_2.data[vat_data_2.data.columns[vats_config.col_minus]].isna()]

        super().__init__(vat_data_1, vat_data_2, vats_config, vats_config)

    