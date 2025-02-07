import os
import time
import json
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Load credentials from GitHub secret
    creds_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise ValueError("Missing Google Service Account credentials.")
    
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def extract_mid_part_of_website(website):
    if not website:
        return "example.com"
    website = re.sub(r'^(https?://)?(www\.)?', '', website).split('/')[0]
    return website.replace(".", ".\u0323").strip()

# Google Sheet details
SHEET_ID = "1yUpVe8a3XzvmpcytXx5Jx5mnkrAXjsqaf6EmIc1_dsc"
WORKSHEET_NAME = "Sheet8"
START_ROW, END_ROW = 2, 473

client = authenticate_google_sheets()
sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.worksheet(WORKSHEET_NAME)

headers = worksheet.row_values(1)
if "Icebreaker" not in headers:
    headers.append("Icebreaker")
    worksheet.update('1:1', [headers])

reviews_col = headers.index("Reviews") + 1
rating_col = headers.index("Average Rating") + 1
icebreaker_col = headers.index("Icebreaker") + 1
website_col = headers.index("Website") + 1

# Pick a random row
row_index = random.randint(START_ROW, END_ROW)

reviews = worksheet.cell(row_index, reviews_col).value
rating = worksheet.cell(row_index, rating_col).value
website = worksheet.cell(row_index, website_col).value

try:
    reviews = int(reviews) if reviews and reviews.strip().upper() != "N/A" else None
except ValueError:
    reviews = None

mid_part_website = extract_mid_part_of_website(website)

if not reviews or not rating:
    icebreaker = f"I came across your website({mid_part_website}) and noticed that your Google profile doesn’t yet have any ratings or reviews."
elif reviews >= 40:
    icebreaker = f"I came across your website({mid_part_website}) and noticed your Google profile has a {rating}-star rating with {reviews} reviews—great work!"
elif reviews < 40 and float(rating) < 5.0:
    icebreaker = f"I came across your website({mid_part_website}) and noticed your Google profile has a {rating}-star rating with {reviews} reviews. Competitors with more reviews or higher ratings tend to attract more visitors."
elif reviews < 40:
    icebreaker = f"I came across your website({mid_part_website}) and noticed your Google profile has a {rating}-star rating with {reviews} reviews. Many of your competitors tend to attract more visitors online."

worksheet.update_cell(row_index, icebreaker_col, icebreaker)
print(f"Updated row {row_index} with Icebreaker: {icebreaker}")

# Random delay between 1 to 4 minutes
sleep_time = random.randint(60, 240)
print(f"Sleeping for {sleep_time} seconds before next execution...")
time.sleep(sleep_time)
