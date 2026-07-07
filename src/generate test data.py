# generate_test_data.py
# Purpose: Generate realistic IAM test datasets at scale for stress testing

import pandas as pd
import random
from datetime import datetime, timedelta
import sys

DEPARTMENTS = ["Finance", "IT", "HR", "Legal", "Exec", "Operations", "Sales",
               "Marketing", "Engineering", "Compliance", "Audit", "Treasury"]
ROLES = ["Analyst", "Manager", "SysAdmin", "Developer", "Contractor", "VP",
         "Director", "Specialist", "Coordinator", "Engineer"]
FIRST = ["james", "mary", "robert", "patricia", "john", "jennifer", "michael",
         "linda", "david", "elizabeth", "william", "barbara", "richard", "susan",
         "joseph", "jessica", "thomas", "sarah", "carlos", "maria", "wei", "priya",
         "ahmed", "fatima", "kenji", "yuki", "oluwaseun", "amara", "diego", "sofia"]
LAST = ["smith", "johnson", "williams", "brown", "jones", "garcia", "miller",
        "davis", "rodriguez", "martinez", "chen", "patel", "kim", "nguyen",
        "singh", "lopez", "gonzalez", "wilson", "anderson", "taylor"]

def generate_dataset(n_users: int, output_path: str):
    random.seed(42)  # reproducible
    today = datetime(2026, 7, 7)
    rows = []
    managers = [f"{random.choice(FIRST)[0]}{random.choice(LAST)}" for _ in range(max(10, n_users // 50))]

    for i in range(1, n_users + 1):
        first = random.choice(FIRST)
        last = random.choice(LAST)
        username = f"{first[0]}{last}{i}"
        dept = random.choice(DEPARTMENTS)
        role = random.choices(ROLES, weights=[25, 15, 8, 15, 10, 3, 4, 8, 6, 6])[0]

        # 8% privileged
        access = "Privileged" if random.random() < 0.08 else "Standard"

        # 5% terminated
        status = "Terminated" if random.random() < 0.05 else "Active"

        # last login: 80% recent, 15% dormant (90-400 days), 5% very stale
        r = random.random()
        if r < 0.80:
            days_ago = random.randint(0, 60)
        elif r < 0.95:
            days_ago = random.randint(91, 400)
        else:
            days_ago = random.randint(401, 900)
        last_login = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        # 2% missing manager
        manager = "" if random.random() < 0.02 else random.choice(managers)

        rows.append({
            "user_id": f"U{i:06d}",
            "username": username,
            "department": dept,
            "role": role,
            "access_level": access,
            "last_login": last_login,
            "account_status": status,
            "manager": manager
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    size_mb = round(len(df.to_csv(index=False)) / 1024 / 1024, 2)
    print(f"[+] Generated {n_users:,} users -> {output_path} ({size_mb} MB)")
    return df

if __name__ == "__main__":
    sizes = [1000, 10000, 50000, 100000]
    if len(sys.argv) > 1:
        sizes = [int(sys.argv[1])]
    for n in sizes:
        generate_dataset(n, f"data/test_users_{n}.csv")