import os

file_path = r"d:\TILLU\tillu-backend\supabase\schema.sql"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all occurrences of "CREATE TRIGGER" with "CREATE OR REPLACE TRIGGER"
new_content = content.replace("CREATE TRIGGER", "CREATE OR REPLACE TRIGGER")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully updated triggers to use CREATE OR REPLACE TRIGGER")
