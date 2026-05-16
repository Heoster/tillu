import re
import os

file_path = r"d:\TILLU\tillu-backend\supabase\schema.sql"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace CREATE POLICY name ON table with DROP POLICY IF EXISTS ... ; CREATE POLICY ...
# It might be spread over multiple lines, but usually "CREATE POLICY name ON table" is on one line.
pattern = re.compile(r"CREATE\s+POLICY\s+([a-zA-Z0-9_]+)\s+ON\s+([a-zA-Z0-9_]+)", re.IGNORECASE)

def replacer(match):
    policy_name = match.group(1)
    table_name = match.group(2)
    return f"DROP POLICY IF EXISTS {policy_name} ON {table_name};\nCREATE POLICY {policy_name} ON {table_name}"

new_content = pattern.sub(replacer, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully added DROP POLICY IF EXISTS before CREATE POLICY")
