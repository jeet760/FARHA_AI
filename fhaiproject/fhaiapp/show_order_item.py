import requests
import pandas as pd

# API URL (first page)
url = "https://farmerharvest.in/api/orders/?page=1"

all_users = []

# Fetch all pages
while url:
    resp = requests.get(url)
    data = resp.json()
    all_users.extend(data['results'])  # accumulate all users
    url = data['next']  # next page URL, None if last page

print(f"Total users fetched: {len(all_users)}")

# Flatten order_details into rows, keeping user and school info
item_df = pd.json_normalize(
    all_users,
    record_path='order_details',                    # explode each order detail
    meta=['id', 'first_name', 'userType',          # keep user info
          ['school_info', 'total_students'],
          ['school_info', 'total_students_with_preprimary'],
          ['school_info', 'i_students'],
          ['school_info', 'ii_students'],
          ['school_info', 'iii_students'],
          ['school_info', 'iv_students'],
          ['school_info', 'v_students'],
          ['school_info', 'vi_students'],
          ['school_info', 'vii_students'],
          ['school_info', 'viii_students'],],
    sep='_',
    errors="ignore"
)

# Group by item to get total quantities
item_cat_group = item_df.groupby(
    ['item_name', 'item_cat', 'item_unit'], as_index=False
)['itemQty'].sum()


print("Item summary:")
print(item_cat_group)

print('Data frame is:')
print(item_df)

print('Student Summary')
student_df = pd.json_normalize(
    all_users,                          # your JSON
    meta=['id', 'first_name', 'userType',
          ['school_info','i_students'],
          ['school_info','ii_students'],
          ['school_info','iii_students'],
          ['school_info','iv_students'],
          ['school_info','v_students'],
          ['school_info','vi_students'],
          ['school_info','vii_students'],
          ['school_info','viii_students'],
          ['school_info','ix_students'],
          ['school_info','x_students'],
          ['school_info','total_students']]
)
# Rename cols for clarity
student_df = student_df.rename(columns={
    'school_info.i_students':'i_students',
    'school_info.ii_students':'ii_students',
    'school_info.iii_students':'iii_students',
    'school_info.iv_students':'iv_students',
    'school_info.v_students':'v_students',
    'school_info.vi_students':'vi_students',
    'school_info.vii_students':'vii_students',
    'school_info.viii_students':'viii_students',
    'school_info.ix_students':'ix_students',
    'school_info.x_students':'x_students',
    'school_info.total_students':'total_students'
})

# Create groups
student_df['primary_students'] = student_df[['i_students','ii_students','iii_students','iv_students','v_students']].sum(axis=1)
student_df['upper_students']   = student_df[['vi_students','vii_students','viii_students','ix_students','x_students']].sum(axis=1)

print('Total Students from I to V:')
print(student_df['primary_students'].sum())
print('Total Students from VI to X:')
print(student_df['upper_students'].sum())
# print('VI-X total Students:')
# total_v_x_students = class_totals_vi_x.groupby("first_name")["school_info_total_students"].max()
# print(f'No. of Students in VI to X {total_v_x_students.sum()}')


# #global view of whole data like number of schools etc.
# no_of_schools = item_df['first_name'].nunique()
# print(f'No. of Schools: {no_of_schools}')
# school_students = item_df.groupby("first_name")["school_info_total_students"].max()
# print(f'No. of Students {school_students.sum()}')
# #school details
# school_df = item_df[item_df["userType"] == "3"]
# individual_school_totals = school_df.groupby(
#     ["id", "first_name"]
# )[["school_info_total_students", "school_info_total_students_with_preprimary"]].max().reset_index()
# print(individual_school_totals)
# category_summary = item_df.groupby(
#     ["item_name", "item_cat", "item_unit"], as_index=False
# )["itemQty"].sum()
# print(category_summary.head())
# #list category
# categories = item_df["item_cat"].unique().tolist()
# print(f'List of categories: {categories}')
