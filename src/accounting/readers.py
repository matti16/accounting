import pandas as pd


FORMATS = ["%m/%d/%y", "%d/%m/%y", "%d/%m/%Y"]

class BalanceData:

    count_col_name = "Conteggio"
    date_col_name = "Data"
    desc_col_name = "Descrizione"

    def __init__(
        self, 
        file_io, 
        file_format,
        col_plus, 
        col_minus, 
        col_amount, 
        col_date, 
        col_description,
        skiprows,
        ignore_neg=False
    ) -> None:
        if file_format == "csv":
            df = pd.read_csv(file_io, skiprows=skiprows, delimiter=";", encoding='latin1')
        else:
            df = pd.read_excel(file_io, skiprows=skiprows, engine='openpyxl')

        self.col_plus = df.columns[col_plus]
        self.col_minus = df.columns[col_minus]
        self.col_date = df.columns[col_date]
        self.col_description = df.columns[col_description]

        self.col_amount = col_amount

        if col_minus != col_plus and not ignore_neg:
            df[self.col_minus] = df[self.col_minus] * -1

        df[self.col_amount] = df[self.col_plus].combine_first(df[self.col_minus])\
            .apply(lambda x: str(x).replace(",", ".")).astype(float)

        for f in FORMATS:
            try:
                df[self.col_date] = pd.to_datetime(df[self.col_date], format=f).dt.date
                break
            except Exception as e:
                if f == FORMATS[-1]:
                    raise(e)
        
        self.data = df

    def aggregate_by_amount(self):
        df_groupped = self.data\
            .groupby(self.col_amount)\
            .agg(
                Data=(self.col_date, "first"), 
                Descrizione=(self.col_description, "first"), 
                Conteggio=(self.col_description, "count")
            ).reset_index()
        
        df_groupped[self.count_col_name] = df_groupped[self.count_col_name].astype(int)
        df_groupped.loc[df_groupped[self.count_col_name] > 1, "Data"] = None
        df_groupped.loc[df_groupped[self.count_col_name] > 1, "Descrizione"] = ""
        return df_groupped
        




