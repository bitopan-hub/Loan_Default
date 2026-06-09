import pandas as pd
import numpy as np

def preprocess_data(df,stats):
    df = df.copy()
    
    rename_dict = {
        'Unnamed: 0': 'id',
        'RevolvingUtilizationOfUnsecuredLines': 'util_ratio',
        'NumberOfTime30-59DaysPastDueNotWorse': 'late_30_59',
        'DebtRatio': 'debt_ratio',
        'MonthlyIncome': 'income(M)',
        'NumberOfOpenCreditLinesAndLoans': 'open_lines',
        'NumberOfTimes90DaysLate': 'late_90_plus',
        'NumberRealEstateLoansOrLines': 'realEstate_lines',
        'NumberOfTime60-89DaysPastDueNotWorse': 'late_60_89',
        'NumberOfDependents': 'dependents'
    }

    df.rename(columns=rename_dict, inplace=True)

    df['income_missing'] = df['income(M)'].isna().astype(int)
    df['income(M)'] = df['income(M)'].fillna(stats['income_median'])

    df['dependents_missing'] = df['dependents'].isna().astype(int)
    df['dependents'] = df['dependents'].fillna(0)
    
    df['monthly_debt'] = np.where((df['debt_ratio'] > 2) | (df['income_missing'] == 1), 
                              df['debt_ratio'], 
                              df['debt_ratio'] * df['income(M)'])

    df['debt_is_absolute'] = (df['debt_ratio'] > 2).astype(int)
    df['high_debt_ratio_flag'] = ((df['debt_ratio'] > 1) & (df['debt_ratio'] <= 2)).astype(int)
    df['debt_ratio_cleaned'] = df['debt_ratio'].copy()
    df['debt_ratio_cleaned'] = np.where(
        df['debt_ratio'] > 2 ,
        np.nan,
        df['debt_ratio']
    )
    df['debt_ratio_cleaned'] = df['debt_ratio_cleaned'].fillna(stats['debt_ratio_median'])
    df.drop(columns=['debt_ratio'], inplace=True)
    
    df['util_ratio'] = df['util_ratio'].clip(upper=stats['util_upper_limit'])
    df['high_util_flag'] = (df['util_ratio'] > 0.9).astype(int)
    
    median_age = stats['age_median']
    df.loc[df['age'] < 18, 'age'] = median_age
    df.loc[df['age'] > 90, 'age'] = 90
    
    df.loc[df['late_30_59'] >= 96, 'late_30_59'] = stats['late_30_59_cap']
    df.loc[df['late_60_89'] >= 96, 'late_60_89'] = stats['late_60_89_cap']
    df.loc[df['late_90_plus'] >= 96, 'late_90_plus'] = stats['late_90_plus_cap']
    
    df['open_lines'] = df['open_lines'].clip(upper=stats['open_lines_cap'])
    df['realEstate_lines'] = df['realEstate_lines'].clip(upper=10)

    # feature engineering
    df['income_per_dependent'] = df['income(M)'] / (df['dependents'].fillna(0) + 1)
    df["late_payment_score"] = df["late_30_59"] + (df["late_60_89"] * 2) + (df["late_90_plus"] * 3)
    df['monthly_cash_flow'] =  df['income(M)'] - df['monthly_debt']
    df['util_debt_impact'] = df['util_ratio'] * df['monthly_debt']
    
    df.drop(columns=['id'], inplace=True)

    return df