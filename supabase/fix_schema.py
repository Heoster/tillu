import os

file_path = r"d:\TILLU\tillu-backend\supabase\schema.sql"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all occurrences of "user_id TEXT" with "user_id UUID"
new_content = content.replace("user_id TEXT", "user_id UUID")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully updated user_id types in schema.sql")
