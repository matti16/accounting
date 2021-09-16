from accounting.checks import AccountChecks
import sys

def main_accounts_check(path_bank, path_income):
    checker = AccountChecks(path_bank, path_income)
    diff = checker.get_differences()
    diff.to_excel("Differenze Conti.xlsx", index=False)



if __name__ == "__main__":
    path_bank = sys.argv[1]
    path_income = sys.argv[2]
    main_accounts_check(path_bank, path_income)

