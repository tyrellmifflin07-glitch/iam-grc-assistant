# src/load_data.py
# Purpose: Load IAM user data and print a basic access summary

import pandas as pd
from datetime import datetime

def load_users(filepath: str) -> pd.DataFrame:
    """Load a CSV of IAM users into a pandas DataFrame."""
    df = pd.read_csv(filepath)
    print(f"[+] Loaded {len(df)} user records from {filepath}")
    return df

def summarize_users(df: pd.DataFrame) -> None:
    """Print a quick summary of user access data."""
    print("\n===== IAM DATA SUMMARY =====")
    print(f"Total users:       {len(df)}")
    print(f"Active users:      {len(df[df['account_status'] == 'Active'])}")
    print(f"Terminated users:  {len(df[df['account_status'] == 'Terminated'])}")
    print(f"Privileged users:  {len(df[df['access_level'] == 'Privileged'])}")
    print(f"Contractors:       {len(df[df['role'] == 'Contractor'])}")
    
    print("\nUsers by department:")
    print(df['department'].value_counts().to_string())

if __name__ == "__main__":
    df = load_users("data/users.csv")
    summarize_users(df)