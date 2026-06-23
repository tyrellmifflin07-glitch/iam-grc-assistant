# src/risk_engine.py
# Purpose: Detect IAM access risks from user data

import pandas as pd
from datetime import datetime, timedelta

def load_users(filepath: str) -> pd.DataFrame:
    """Load IAM user CSV into a DataFrame."""
    df = pd.read_csv(filepath)
    df['last_login'] = pd.to_datetime(df['last_login'])
    return df

def flag_terminated_with_access(df: pd.DataFrame) -> pd.DataFrame:
    """Flag terminated users who still appear as active in the system."""
    flagged = df[df['account_status'] == 'Terminated'].copy()
    flagged['risk_finding'] = 'Terminated user with active system record'
    flagged['severity'] = 'Critical'
    return flagged

def flag_contractors_with_privilege(df: pd.DataFrame) -> pd.DataFrame:
    """Flag contractors who have privileged access."""
    flagged = df[
        (df['role'] == 'Contractor') &
        (df['access_level'] == 'Privileged')
    ].copy()
    flagged['risk_finding'] = 'Contractor with privileged access'
    flagged['severity'] = 'High'
    return flagged

def flag_dormant_accounts(df: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    """Flag accounts with no login activity in the past N days."""
    cutoff = datetime.now() - timedelta(days=days)
    flagged = df[
        (df['account_status'] == 'Active') &
        (df['last_login'] < cutoff)
    ].copy()
    flagged['risk_finding'] = f'Dormant account — no login in {days}+ days'
    flagged['severity'] = 'Medium'
    return flagged

def flag_privileged_no_manager(df: pd.DataFrame) -> pd.DataFrame:
    """Flag privileged users with no manager assigned."""
    flagged = df[
        (df['access_level'] == 'Privileged') &
        (df['manager'].isna() | (df['manager'].str.strip() == ''))
    ].copy()
    flagged['risk_finding'] = 'Privileged user with no manager assigned'
    flagged['severity'] = 'High'
    return flagged

def run_all_checks(filepath: str) -> pd.DataFrame:
    """Run all risk checks and return a combined findings report."""
    df = load_users(filepath)
    
    checks = [
        flag_terminated_with_access(df),
        flag_contractors_with_privilege(df),
        flag_dormant_accounts(df),
        flag_privileged_no_manager(df),
    ]
    
    findings = pd.concat(checks, ignore_index=True)
    
    report_cols = [
        'user_id', 'username', 'department', 'role',
        'access_level', 'last_login', 'account_status',
        'manager', 'risk_finding', 'severity'
    ]
    
    return findings[report_cols].drop_duplicates()

if __name__ == "__main__":
    findings = run_all_checks("data/users.csv")
    
    print(f"\n===== IAM RISK FINDINGS =====")
    print(f"Total findings: {len(findings)}\n")
    
    for severity in ['Critical', 'High', 'Medium']:
        subset = findings[findings['severity'] == severity]
        if not subset.empty:
            print(f"--- {severity} ---")
            for _, row in subset.iterrows():
                print(f"  [{row['severity']}] {row['username']} ({row['department']}) — {row['risk_finding']}")
            print()