from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import NutritentReferenceUnit, Food, DietaryFibre, WaterSolubleVitamins, FatSolubleVitamins, Carotenoids, MineralsAndTraceElements, StarchAndSugars, FattyAcid, AminoAcid, OrganicAcid, Polyphenols, Oligosaccharides, PhytosterolsPhytateSaponin
from django.db.models import Q, Max, Min, Sum, Count, OuterRef, Subquery, F, Value
import requests
import pandas as pd
import json
import socket
from .nutrients import NutritionReport
from .process_dietary_elements import PDE
from .farha_ai_engine import FarhaAIEngine

# Create your views here.
def site_online(host='farmerharvest.in', port=443, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        return True
    except socket.error:
        return False

LIST_STATES = [
    ('', 'Select State'),
    ('28','Andhra Pradesh'),
    ('12','Arunachal Pradesh'),
    ('18','Assam'),
    ('10','Bihar'),
    ('22','Chhattisgarh'),
    ('30','Goa'),
    ('24','Gujarat'),
    ('6','Haryana'),
    ('2','Himachal Pradesh'),
    ('20','Jharkhand'),
    ('29','Karnataka'),
    ('32','Kerala'),
    ('23','Madhya Pradesh'),
    ('27','Maharashtra'),
    ('14','Manipur'),
    ('17','Meghalaya'),
    ('15','Mizoram'),
    ('13','Nagaland'),
    ('21','Odisha'),
    ('3','Punjab'),
    ('8','Rajasthan'),
    ('11','Sikkim'),
    ('33','Tamil Nadu'),
    ('36','Telangana'),
    ('16','Tripura'),
    ('9','Uttar Pradesh'),
    ('5','Uttarakhand'),
    ('19','West Bengal'),
    ('35','Andaman And Nicobar Islands [UT]'),
    ('4','Chandigarh [UT]'),
    ('7','Delhi [UT]'),
    ('1','Jammu And Kashmir [UT]'),
    ('37','Ladakh [UT]'),
    ('31','Lakshadweep [UT]'),
    ('34','Puducherry [UT]'),
    ('38','The Dadra And Nagar Haveli And Daman And Diu [UT]'),
]

rda_macro_ref = {
    "energy": 2100,   # kcal
    "carbohydrates": 300, # g
    "protein": 50,    # g
    "fat": 70,        # g
    "fibre": 30,      # g
}
rda_micro_ref_vitamins = {
    "vit-a": 1000,
    "vit-d": 10,
    "vit-e": 10,
    "vit-k": 55,
    "vit-c": 80,
}
rda_micro_ref_minerals = {
    "iron": 17,
    "calcium": 1000,
    "magnesium": 340,
    "phosphorus": 700,
}

def calculate_for_students(all_users):
    filtered_schools = [
        user for user in all_users if user.get('userType') == '3'
    ]
    no_of_schools = len(filtered_schools)
    school_df = pd.json_normalize(
        filtered_schools,
        record_path='order_details',                    # explode each order detail
        meta=['id', 'first_name', 'userType',          # keep user info
            ['school_info', 'total_students'],
            ['school_info', 'total_students_with_preprimary'],
            ['school_info', 'pre_primary_students'],
            ['school_info', 'i_students'],
            ['school_info', 'ii_students'],
            ['school_info', 'iii_students'],
            ['school_info', 'iv_students'],
            ['school_info', 'v_students'],
            ['school_info', 'vi_students'],
            ['school_info', 'vii_students'],
            ['school_info', 'viii_students'],
            ['school_info', 'ix_students'],
            ['school_info', 'x_students'],
            ['school_info', 'xi_students'],
            ['school_info', 'xii_students']],
        sep='_',
        errors='ignore'
    )
    #calculate total number of schools, students and individuals
    school_df['i_iv_total'] = (
        school_df["school_info_i_students"]
        + school_df["school_info_ii_students"]
        + school_df["school_info_iii_students"]
        + school_df["school_info_iv_students"]
        + school_df["school_info_v_students"]
    )
    school_df['vi_x_total'] = (
        school_df["school_info_vi_students"]
        + school_df["school_info_vii_students"]
        + school_df["school_info_viii_students"]
        + school_df["school_info_ix_students"]
        + school_df["school_info_x_students"]
    )
    no_of_schools = school_df['first_name'].nunique()   #total schools
    no_of_students_i_v = int(school_df['i_iv_total'].iloc[0])
    no_of_students_vi_x = int(school_df['vi_x_total'].iloc[0])
    no_of_students = no_of_students_i_v + no_of_students_vi_x   #total students
    item_cat_group = school_df.groupby(
        ['item_name', 'item_cat', 'item_unit'], as_index=False
    )['itemQty'].sum()
    food_cat_summary_labels = school_df["item_cat"].unique().tolist()

    return_context = {
        'school_df':school_df,
        'no_of_schools':no_of_schools,
        'no_of_students_i_v':no_of_students_i_v,
        'no_of_students_vi_x':no_of_students_vi_x,
        'no_of_students':no_of_students,
        'item_cat_group':item_cat_group,
        'food_cat_summary_labels':food_cat_summary_labels
    }
    return return_context

def calculate_for_others(all_users):
    filtered_individuals = [
        user for user in all_users if user.get('userType') == '5'
    ]
    no_of_individuals = len(filtered_individuals)
    indvidual_df = pd.json_normalize(
        filtered_individuals,
        record_path='order_details',                    # explode each order detail
        meta=['id', 'first_name', 'userType'],          # keep user info
        sep='_',
        errors='ignore'
    )
    no_of_individuals = indvidual_df['first_name'].nunique()    #total individuals
    item_cat_group = indvidual_df.groupby(
        ['item_name', 'item_cat', 'item_unit'], as_index=False
    )['itemQty'].sum()
    food_cat_summary_labels = indvidual_df["item_cat"].unique().tolist()

    return_context = {
        'no_of_individuals':no_of_individuals,
        'item_cat_group':item_cat_group,
        'food_cat_summary_labels':food_cat_summary_labels
    }
    return return_context

def calculate_for_all(all_users):
    school_context = calculate_for_students(all_users=all_users)
    school_df = school_context['school_df']
    no_of_schools = school_df['first_name'].nunique()   #total schools
    no_of_students_i_v = int(school_df['i_iv_total'].iloc[0])
    no_of_students_vi_x = int(school_df['vi_x_total'].iloc[0])
    no_of_students = no_of_students_i_v + no_of_students_vi_x   #total students
    
    others_context = calculate_for_others(all_users=all_users)
    no_of_individuals = others_context['no_of_individuals']

    total_consumers = no_of_schools+no_of_individuals

    all_users_df = pd.json_normalize(
        all_users,
        record_path='order_details',                    # explode each order detail
        meta=['id', 'first_name', 'userType',
            ['school_info', 'total_students'],
            ['school_info', 'total_students_with_preprimary'],
            ['school_info', 'pre_primary_students'],
            ['school_info', 'i_students'],
            ['school_info', 'ii_students'],
            ['school_info', 'iii_students'],
            ['school_info', 'iv_students'],
            ['school_info', 'v_students'],
            ['school_info', 'vi_students'],
            ['school_info', 'vii_students'],
            ['school_info', 'viii_students'],
            ['school_info', 'ix_students'],
            ['school_info', 'x_students'],
            ['school_info', 'xi_students'],
            ['school_info', 'xii_students']],          # keep user info
        sep='_',
        errors='ignore'
    )
    item_cat_group = all_users_df.groupby(
        ['item_name', 'item_cat', 'item_unit'], as_index=False
    )['itemQty'].sum()
    food_cat_summary_labels = all_users_df["item_cat"].unique().tolist()

    return_context = {
        'no_of_individuals':no_of_individuals,
        'no_of_schools':no_of_schools,
        'no_of_students_i_v':no_of_students_i_v,
        'no_of_students_vi_x':no_of_students_vi_x,
        'no_of_students':no_of_students,
        'total_consumers':total_consumers,
        'item_cat_group':item_cat_group,
        'food_cat_summary_labels':food_cat_summary_labels,
    }
    return return_context

def fetch_api_data(request, user):
    # API URL (first page)
    url = "https://farmerharvest.in/api/orders/"
    if user and user != '0':
        url += f"?userType={user}"

    all_users = []
    # Fetch all pages
    try:
        while url:
            resp = requests.get(url)
            data = resp.json()
            all_users.extend(data['results'])  # accumulate all users
            url = data['next']  # next page URL, None if last page
    except Exception as ex:
        messages.warning('Please connect to internet!')
        return {'Data':False}

    #checks whether any data fetched or not! if not fetched the make data = false
    if all_users.__len__() == 0:
        messages.error(request, 'No data found!')
        return {'Data':False}
    
    if user == '3':
        #calculation for students
        student_data = calculate_for_students(all_users=all_users)
        no_of_schools = student_data['no_of_schools']
        no_of_students_i_v = student_data['no_of_students_i_v']
        no_of_students_vi_x = student_data['no_of_students_vi_x']
        no_of_students = student_data['no_of_students']
        item_cat_group = student_data['item_cat_group']
        food_cat_summary_labels = student_data['food_cat_summary_labels']
        total_no_of_consumers = no_of_students
        no_of_individuals = 0
    elif user == '5':
        #calculation for others (individuals)
        others_data = calculate_for_others(all_users=all_users)
        no_of_individuals = others_data['no_of_individuals']
        item_cat_group = others_data['item_cat_group']
        food_cat_summary_labels = others_data['food_cat_summary_labels']
        total_no_of_consumers = no_of_individuals
        no_of_schools, no_of_students, no_of_students_i_v, no_of_students_vi_x = 0, 0, 0, 0
    else:
        #calculation for others (individuals)
        all_users_data = calculate_for_all(all_users=all_users)
        no_of_individuals = all_users_data['no_of_individuals']
        no_of_schools = all_users_data['no_of_schools']
        no_of_students_i_v = all_users_data['no_of_students_i_v']
        no_of_students_vi_x = all_users_data['no_of_students_vi_x']
        no_of_students = all_users_data['no_of_students']
        item_cat_group = all_users_data['item_cat_group']
        food_cat_summary_labels = all_users_data['food_cat_summary_labels']
        total_no_of_consumers = all_users_data['total_consumers']
    #process dietary elements
    dietary_fibre_context = PDE.process_dietary_fibre(item_cat_group=item_cat_group)
    dietary_minerals_context = PDE.process_dietary_minerals(item_cat_group=item_cat_group)
    dietary_vitamins_context = PDE.process_dietary_vitamins(item_cat_group=item_cat_group)

    return_context = {
        'Data':True,
        'no_of_schools': no_of_schools,
        'no_of_individuals': 0 if not no_of_individuals else no_of_individuals,
        'no_of_students': no_of_students,
        'no_of_students_i_v':no_of_students_i_v,
        'no_of_students_vi_x':no_of_students_vi_x,
        'total_no_of_consumers':total_no_of_consumers,
        'food_cat_summary_labels':food_cat_summary_labels,
        'api_data': data,
        'item_cat_group': item_cat_group,
        'dietary_fibre_context':dietary_fibre_context,
        'total_protein_content': dietary_fibre_context['total_protein_content'],#dietary fibre starts
        'total_fat_content': dietary_fibre_context['total_fat_content'],
        'total_fibre_content': dietary_fibre_context['total_fibre_content'],
        'total_carb_content': dietary_fibre_context['total_carb_content'],
        'total_calories': dietary_fibre_context['total_calories'],
        'protcnt_nru': dietary_fibre_context['protcnt_nru'],
        'fatce_nru': dietary_fibre_context['fatce_nru'],
        'fibtg_nru': dietary_fibre_context['fibtg_nru'],
        'choavldf_nru': dietary_fibre_context['choavldf_nru'],
        'enerc_nru': dietary_fibre_context['enerc_nru'],
        'total_fe_content':dietary_minerals_context['total_fe_content'],
        'total_ca_content':dietary_minerals_context['total_ca_content'],
        'total_mg_content':dietary_minerals_context['total_mg_content'],
        'total_p_content':dietary_minerals_context['total_p_content'],
        'iron_nru':dietary_minerals_context['iron_nru'],
        'calcium_nru':dietary_minerals_context['calcium_nru'],
        'magnesium_nru':dietary_minerals_context['magnesium_nru'],
        'phosphorus_nru':dietary_minerals_context['phosphorus_nru'],
        'total_vita_content':dietary_vitamins_context['total_vita_content'],
        'total_vitd_content':dietary_vitamins_context['total_vitd_content'],
        'total_vite_content':dietary_vitamins_context['total_vite_content'],
        'total_vitk_content':dietary_vitamins_context['total_vitk_content'],
        'total_vitc_content':dietary_vitamins_context['total_vitc_content'],
        'vita_nru':dietary_vitamins_context['vita_nru'],
        'vitd_nru':dietary_vitamins_context['vitd_nru'],
        'vite_nru':dietary_vitamins_context['vite_nru'],
        'vitk_nru':dietary_vitamins_context['vitk_nru'],
        'vitc_nru':dietary_vitamins_context['vitc_nru'],
    }
    return return_context

def dashboard(request):
    user_type = '0'
    if not site_online():
        messages.error(request, 'Please connect to internet!')
    else:
        user_type = request.GET.get('user', '0')

    api_data = fetch_api_data(request, user=user_type)
    if api_data['Data'] == False: #checks whether data found or not
        messages.error(request, 'Data not found!')
        return HttpResponse('Data not found!')

    # RDA references and coverage
    nutrient_data = [
        {'category': 'macros', 'name': 'Energy', 'unit': 'kcal', 'amount': api_data['total_calories'], 'rda': rda_macro_ref['energy'], 'rda_percentage': ((api_data['total_calories']/api_data['total_no_of_consumers'])/rda_macro_ref['energy'])*100 if rda_macro_ref['energy'] > 0 else 0},
        {'category': 'macros', 'name': 'Carbohydrates', 'unit': 'g', 'amount': api_data['total_carb_content'], 'rda': rda_macro_ref['carbohydrates'], 'rda_percentage': ((api_data['total_carb_content']/api_data['total_no_of_consumers'])/rda_macro_ref['carbohydrates'])*100 if rda_macro_ref['carbohydrates'] > 0 else 0},
        {'category': 'macros', 'name': 'Protein', 'unit': 'g', 'amount': api_data['total_protein_content'], 'rda': rda_macro_ref['protein'], 'rda_percentage': ((api_data['total_protein_content']/api_data['total_no_of_consumers'])/rda_macro_ref['protein'])*100 if rda_macro_ref['protein'] > 0 else 0},
        {'category': 'macros', 'name': 'Fat', 'unit': 'g', 'amount': api_data['total_fat_content'], 'rda': rda_macro_ref['fat'], 'rda_percentage': ((api_data['total_fat_content']/api_data['total_no_of_consumers'])/rda_macro_ref['fat'])*100 if rda_macro_ref['fat'] > 0 else 0},
        {'category': 'macros', 'name': 'Fibre', 'unit': 'g', 'amount': api_data['total_fibre_content'], 'rda': rda_macro_ref['fibre'], 'rda_percentage': ((api_data['total_fibre_content']/api_data['total_no_of_consumers'])/rda_macro_ref['fibre'])*100 if rda_macro_ref['fibre'] > 0 else 0},
        {'category': 'vitamins', 'name': 'Vit-A', 'unit': 'µg', 'amount': api_data['total_vita_content'], 'rda': rda_micro_ref_vitamins['vit-a'], 'rda_percentage': ((api_data['total_vita_content']/api_data['total_no_of_consumers'])/rda_micro_ref_vitamins['vit-a'])*100 if rda_micro_ref_vitamins['vit-a'] > 0 else 0},
        {'category': 'vitamins', 'name': 'Vit-D', 'unit': 'µg', 'amount': api_data['total_vitd_content'], 'rda': rda_micro_ref_vitamins['vit-d'], 'rda_percentage': ((api_data['total_vitd_content']/api_data['total_no_of_consumers'])/rda_micro_ref_vitamins['vit-d'])*100 if rda_micro_ref_vitamins['vit-d'] > 0 else 0},
        {'category': 'vitamins', 'name': 'Vit-E', 'unit': 'mg', 'amount': api_data['total_vite_content'], 'rda': rda_micro_ref_vitamins['vit-e'], 'rda_percentage': ((api_data['total_vite_content']/api_data['total_no_of_consumers'])/rda_micro_ref_vitamins['vit-e'])*100 if rda_micro_ref_vitamins['vit-e'] > 0 else 0},
        {'category': 'vitamins', 'name': 'Vit-K', 'unit': 'µg', 'amount': api_data['total_vitk_content'], 'rda': rda_micro_ref_vitamins['vit-k'], 'rda_percentage': ((api_data['total_vitk_content']/api_data['total_no_of_consumers'])/rda_micro_ref_vitamins['vit-k'])*100 if rda_micro_ref_vitamins['vit-k'] > 0 else 0},
        {'category': 'vitamins', 'name': 'Vit-C', 'unit': 'mg', 'amount': api_data['total_vitc_content'], 'rda': rda_micro_ref_vitamins['vit-c'], 'rda_percentage': ((api_data['total_vitc_content']/api_data['total_no_of_consumers'])/rda_micro_ref_vitamins['vit-c'])*100 if rda_micro_ref_vitamins['vit-c'] > 0 else 0},
        {'category': 'minerals', 'name': 'Iron', 'unit': 'mg', 'amount': api_data['total_fe_content'], 'rda': rda_micro_ref_minerals['iron'], 'rda_percentage': ((api_data['total_fe_content']/api_data['total_no_of_consumers'])/rda_micro_ref_minerals['iron'])*100 if rda_micro_ref_minerals['iron'] > 0 else 0},
        {'category': 'minerals', 'name': 'Calcium', 'unit': 'mg', 'amount': api_data['total_ca_content'], 'rda': rda_micro_ref_minerals['calcium'], 'rda_percentage': ((api_data['total_ca_content']/api_data['total_no_of_consumers'])/rda_micro_ref_minerals['calcium'])*100 if rda_micro_ref_minerals['calcium'] > 0 else 0},
        {'category': 'minerals', 'name': 'Magnesium', 'unit': 'mg', 'amount': api_data['total_mg_content'], 'rda': rda_micro_ref_minerals['magnesium'], 'rda_percentage': ((api_data['total_mg_content']/api_data['total_no_of_consumers'])/rda_micro_ref_minerals['magnesium'])*100 if rda_micro_ref_minerals['magnesium'] > 0 else 0},
        {'category': 'minerals', 'name': 'Phosphorus', 'unit': 'mg', 'amount': api_data['total_p_content'], 'rda': rda_micro_ref_minerals['phosphorus'], 'rda_percentage': ((api_data['total_p_content']/api_data['total_no_of_consumers'])/rda_micro_ref_minerals['phosphorus'])*100 if rda_micro_ref_minerals['phosphorus'] > 0 else 0},
    ]

    report = NutritionReport.from_list(nutrient_data)

    rda_macro_labels = report.macro_labels()
    rda_macro_coverage = report.macro_coverages()

    rda_micro_labels_vitamins = report.vitamins_labels()
    rda_micro_coverage_vitamins = report.vitamins_coverages()
    
    rda_micro_labels_minerals = report.minerals_labels()
    rda_micro_coverage_minerals = report.minerals_coverages()

    mdm_target_calories_data = []
    mdm_target_protein_data = []
    # define rules for each group
    target_mdm_calories = {
        "i_v": {"total": 2962, "avg": 493},
        "vi_x": {"total": 4372, "avg": 729},
    }

    target_mdm_protein = {
        "i_v": {"total": 83, "avg": 14},
        "vi_x": {"total": 123, "avg": 21},
    }

    for group, values in target_mdm_calories.items():
        if int(api_data[f'no_of_students_{group}']) > 0:
            mdm_target_calories_data.extend([values["total"], values["avg"]])
        else:
            mdm_target_calories_data.extend([0, 0])

    for group, values in target_mdm_protein.items():
        if int(api_data[f'no_of_students_{group}']) > 0:
            mdm_target_protein_data.extend([values["total"], values["avg"]])
        else:
            mdm_target_protein_data.extend([0, 0])

    mdm_achieved_calories_data = []
    mdm_achieved_protein_data = []

    unit_calories_i_v = 0
    unit_calories_vi_x = 0
    avg_unit_calories_i_v = 0
    avg_unit_calories_vi_x = 0
    unit_protein_i_v = 0
    unit_protein_vi_x  = 0
    avg_unit_protein_i_v = 0
    avg_unit_protein_vi_x  = 0
    
    
    unit_rice_calories_i_v = (1491/4.18)*6
    unit_rice_calories_vi_x = (2236/4.18)*6
    unit_rice_protein_i_v = 8*6
    unit_rice_protein_vi_x = 12*6

    #macro
    total_calories = api_data['total_calories']
    total_carb_content = api_data['total_carb_content']
    total_protein_content = api_data['total_protein_content']
    total_fat_content = api_data['total_fat_content']
    total_fibre_content = api_data['total_fibre_content']
    #micro-vitamins
    total_vit_a_content = api_data['total_vita_content']  # Placeholder, as vitamin A content is not calculated in the current logic
    total_vit_d_content = api_data['total_vitd_content']  #
    total_vit_e_content = api_data['total_vite_content']  #
    total_vit_k_content = api_data['total_vitk_content']  #
    total_vit_c_content = api_data['total_vitc_content']  #
    #micro-minerals
    total_iron_content = api_data['total_fe_content']  # Placeholder, as iron content is not calculated in the current logic
    total_calcium_content = api_data['total_ca_content']  # Placeholder, as calcium content is not calculated in the current logic
    total_magnesium_content = api_data['total_mg_content']  # Placeholder, as sodium content is not calculated in the current logic
    total_phosphorus_content = api_data['total_p_content']

    #macro nutrients
    unit_calories = total_calories / api_data['total_no_of_consumers']
    unit_carb_content = total_carb_content / api_data['total_no_of_consumers']
    unit_protein_content = total_protein_content / api_data['total_no_of_consumers']
    unit_fat_content = total_fat_content / api_data['total_no_of_consumers']
    unit_fibre_content = total_fibre_content / api_data['total_no_of_consumers']

    #micro nutrients-vitamins
    unit_vit_a_content = total_vit_a_content / api_data['total_no_of_consumers']
    unit_vit_d_content = total_vit_d_content / api_data['total_no_of_consumers']
    unit_vit_e_content = total_vit_e_content / api_data['total_no_of_consumers']
    unit_vit_k_content = total_vit_k_content / api_data['total_no_of_consumers']
    unit_vit_c_content = total_vit_c_content / api_data['total_no_of_consumers']

    #micro nutrients-minerals
    unit_iron_content = total_iron_content / api_data['total_no_of_consumers']
    unit_calcium_content = total_calcium_content / api_data['total_no_of_consumers']
    unit_magnesium_content = total_magnesium_content / api_data['total_no_of_consumers']
    unit_phosphorus_content = total_phosphorus_content / api_data['total_no_of_consumers']

    #mdm nutrition calculation
    if api_data['no_of_students_i_v'] > 0:
        unit_calories_i_v = (total_calories/4.18)/api_data['no_of_students_i_v']
        unit_calories_i_v += unit_rice_calories_i_v
        avg_unit_calories_i_v = unit_calories_i_v/6 #(6 days a week)

        unit_protein_i_v = (total_protein_content)/api_data['no_of_students_i_v']
        unit_protein_i_v += unit_rice_protein_i_v
        avg_unit_protein_i_v = unit_protein_i_v/6#(6 days a week)

    if api_data['no_of_students_vi_x'] > 0:
        unit_calories_vi_x = (total_calories/4.18)/api_data['no_of_students_vi_x']
        unit_calories_vi_x += unit_rice_calories_vi_x
        avg_unit_calories_vi_x = unit_calories_vi_x/6 #(6 days a week)

        unit_protein_vi_x = (total_protein_content)/api_data['no_of_students_vi_x']
        unit_protein_vi_x += unit_rice_protein_vi_x
        avg_unit_protein_vi_x = unit_protein_vi_x/6#(6 days a week)
        

    mdm_achieved_calories_data.append(unit_calories_i_v)
    mdm_achieved_calories_data.append(avg_unit_calories_i_v)
    mdm_achieved_calories_data.append(unit_calories_vi_x)
    mdm_achieved_calories_data.append(avg_unit_calories_vi_x)

    mdm_achieved_protein_data.append(unit_protein_i_v)
    mdm_achieved_protein_data.append(avg_unit_protein_i_v)
    mdm_achieved_protein_data.append(unit_protein_vi_x)
    mdm_achieved_protein_data.append(avg_unit_protein_vi_x)
        
    #print(f'{api_data['dietary_fibre_context']['food_cat_total_carb_list']}')

    return_context = {
        'states':json.dumps(LIST_STATES),
        'no_of_schools': api_data['no_of_schools'],
        'no_of_individuals': api_data['no_of_individuals'],
        'no_of_students': api_data['no_of_students'],
        'no_of_students_i_v':api_data['no_of_students_i_v'],
        'no_of_students_vi_x':api_data['no_of_students_vi_x'],
        'total_no_of_consumers':api_data['total_no_of_consumers'],
        'mdm_target_calories_data':json.dumps(mdm_target_calories_data),
        'mdm_target_protein_data':json.dumps(mdm_target_protein_data),
        'mdm_achieved_calories_data':json.dumps(mdm_achieved_calories_data),
        'mdm_achieved_protein_data':json.dumps(mdm_achieved_protein_data),

        'food_cat_summary_labels':json.dumps(api_data['food_cat_summary_labels']),
        'food_cat_total_carb_list':json.dumps(api_data['dietary_fibre_context']['food_cat_total_carb_list']),
        'food_cat_total_protein_list':json.dumps(api_data['dietary_fibre_context']['food_cat_total_protein_list']),
        'food_cat_total_fat_list':json.dumps(api_data['dietary_fibre_context']['food_cat_total_fat_list']),
        'food_cat_total_fiber_list':json.dumps(api_data['dietary_fibre_context']['food_cat_total_fiber_list']),

        'total_protein_content': f'{api_data['total_protein_content']}',
        'total_fat_content': f'{api_data['total_fat_content']}',
        'total_fibre_content': f'{api_data['total_fibre_content']}',
        'total_carb_content': f'{api_data['total_carb_content']}',
        'total_calories': f'{api_data['total_calories']/4.18}',
        
        'unit_protein_content': f'{api_data['total_protein_content']/api_data['total_no_of_consumers']}',
        'unit_fat_content': f'{api_data['total_fat_content']/api_data['total_no_of_consumers']}',
        'unit_fibre_content': f'{api_data['total_fibre_content']/api_data['total_no_of_consumers']}',
        'unit_carb_content': f'{api_data['total_carb_content']/api_data['total_no_of_consumers']}',
        'unit_calories': f'{api_data['total_calories']/api_data['total_no_of_consumers']}',
        'protcnt_nru' : f'{api_data['protcnt_nru']}',
        'fatce_nru' : f'{api_data['fatce_nru']}',
        'fibtg_nru' : f'{api_data['fibtg_nru']}',
        'choavldf_nru' : f'{api_data['choavldf_nru']}',
        'enerc_nru' : f'kcal',

        'total_fe_content':f'{api_data['total_fe_content']}',
        'total_ca_content':f'{api_data['total_ca_content']}',
        'total_mg_content':f'{api_data['total_mg_content']}',
        'total_p_content':f'{api_data['total_p_content']}',
        'iron_nru':f'{api_data['iron_nru']}',
        'calcium_nru':f'{api_data['calcium_nru']}',
        'magnesium_nru':f'{api_data['magnesium_nru']}',
        'phosphorus_nru':f'{api_data['phosphorus_nru']}',

        'user': user_type,
        'item_cat_group': api_data['item_cat_group'],
        'rda_macro_labels':json.dumps(rda_macro_labels),
        'rda_macro_coverage':json.dumps(rda_macro_coverage),
        'rda_micro_labels_vitamins':json.dumps(rda_micro_labels_vitamins),
        'rda_micro_coverage_vitamins':json.dumps(rda_micro_coverage_vitamins),
        'rda_micro_labels_minerals':json.dumps(rda_micro_labels_minerals),
        'rda_micro_coverage_minerals':json.dumps(rda_micro_coverage_minerals),
    }
    return render(request, 'dashboard.html', context=return_context)

def details(request):
    api_data = fetch_api_data(request)
    # Fetching all food items
    food_items = Food.objects.all()
    
    # Fetching all nutrient reference units
    nutrient_reference_units = NutritentReferenceUnit.objects.all()

    return_context = {
        'api_data': api_data['api_data']['results'],
        'item_cat_group': api_data['item_cat_group'],
        'total_protein_content': f'{api_data['total_protein_content']:.2f} {api_data['protcnt_nru']}',
        'total_fat_content': f'{api_data['total_fat_content']:.2f} {api_data['fatce_nru']}',
        'total_fibre_content': f'{api_data['total_fibre_content']:.2f} {api_data['fibtg_nru']}',
        'total_carb_content': f'{api_data['total_carb_content']:.2f} {api_data['choavldf_nru']}',
        'total_calories': f'{api_data['total_calories']/4.18:.2f} {api_data['enerc_nru']}',
        'no_of_schools': api_data['no_of_schools'],
        'no_of_students': api_data['no_of_students'],
        'unit_protein_content': f'{api_data['total_protein_content']/api_data['no_of_students']:.2f} {api_data['protcnt_nru']}',
        'unit_fat_content': f'{api_data['total_fat_content']/api_data['no_of_students']:.2f} {api_data['fatce_nru']}',
        'unit_fibre_content': f'{api_data['total_fibre_content']/api_data['no_of_students']:.2f} {api_data['fibtg_nru']}',
        'unit_carb_content': f'{api_data['total_carb_content']/api_data['no_of_students']:.2f} {api_data['choavldf_nru']}',
        'unit_calories': f'{api_data['total_calories']/api_data['no_of_students']:.2f} {api_data['enerc_nru']}',
    }
    
    return render(request, 'nutrition.html', return_context)

def farha_ai_engine_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("query", "")
        #user_message = request.POST['input']
        if user_message:
            faie = FarhaAIEngine()
            bot_response = faie.nutrition_query(q=user_message)
            ai_response = json.loads(bot_response.content)
            # print(ai_response['user_query'])
            # print(ai_response['respnose_text'])
            return_context = {
                'user_message': user_message,
                'bot_response': ai_response['respnose_text'],
                'user_query':ai_response['user_query']
            }
            return JsonResponse(return_context)
        else:
            return_context = {
                'user_message': None,
                'bot_response': 'Sorry! Something went wrong.',
                'user_query':None
            }
            return JsonResponse(return_context)
    else:
        return_context = {
            'user_message': None,
            'bot_response': 'Sorry! Something went wrong.',
            'user_query':None
        }
    return render(request, 'farha-ai.html', context=return_context)