from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import NutritentReferenceUnit, Food, DietaryFibre, WaterSolubleVitamins, FatSolubleVitamins, Carotenoids, MineralsAndTraceElements, StarchAndSugars, FattyAcid, AminoAcid, OrganicAcid, Polyphenols, Oligosaccharides, PhytosterolsPhytateSaponin
from django.db.models import Q, Max, Min, Sum, Count, OuterRef, Subquery, F, Value
import requests
import pandas as pd
import json
import socket
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


def process_dietary_fibre(item_cat_group):
    total_protein_content = 0
    total_fat_content = 0
    total_fibre_content = 0
    total_carb_content = 0
    total_calories = 0

    as_total_protein = 0
    as_total_carb = 0
    as_total_fat = 0
    as_total_fiber = 0
    vg_total_protein = 0
    vg_total_carb = 0
    vg_total_fat = 0
    vg_total_fiber = 0
    pl_total_protein = 0
    pl_total_carb = 0
    pl_total_fat = 0
    pl_total_fiber = 0

    food_cat_total_protein_list=[]
    food_cat_total_carb_list=[]
    food_cat_total_fat_list=[]
    food_cat_total_fiber_list=[]

    protcnt_nru = 0
    fatce_nru = 0
    fibtg_nru = 0
    choavldf_nru = 0
    enerc_nru = 0

    for _, row in item_cat_group.iterrows():
        item_name = row['item_name']
        item_unit = row['item_unit']
        item_qty = row['itemQty']
        item_code = Food.objects.filter(Q(food_name=item_name)|Q(food_name__icontains=item_name)|Q(description__icontains=item_name)).distinct().first()
        #for code in item_codes:
        if item_code:
            item_protein = 0
            item_carb = 0
            item_fat = 0
            item_fibre = 0

            food_code = item_code.food_code
            dietary_fibres = DietaryFibre.objects.filter(food_code=food_code)
            protcnt = dietary_fibres[0].protcnt
            fatce = dietary_fibres[0].fatce
            fibtg = dietary_fibres[0].fibtg
            choavldf = dietary_fibres[0].choavldf
            enerc = float(dietary_fibres[0].enerc)/4.18  # Convert to kcal

            protcnt_nru = NutritentReferenceUnit.objects.filter(nutrient='protcnt')[0].unit
            fatce_nru = NutritentReferenceUnit.objects.filter(nutrient='fatce')[0].unit
            fibtg_nru = NutritentReferenceUnit.objects.filter(nutrient='fibtg')[0].unit
            choavldf_nru = NutritentReferenceUnit.objects.filter(nutrient='choavldf')[0].unit
            enerc_nru = 'kcal' #NutritentReferenceUnit.objects.filter(nutrient='enerc')[0].unit

            # print(f'100grams - {item_name} - {food_code} - {item_unit} - {item_qty} - {protcnt} - {fatce} - {fibtg} - {choavldf} - {enerc}')
            if item_unit == 'kg':
                #print(f"({item_qty} kg.) | {item_name} | {food_code} | {item_unit} | {item_qty} | {float(protcnt)*10*float(item_qty)} | {float(fatce)*10*float(item_qty)} | {float(fibtg)*10*float(item_qty)} | {float(choavldf)*10*float(item_qty)} | {float(enerc)*10*float(item_qty)}")
                total_protein_content+= float(protcnt) * 10 * float(item_qty)
                total_fat_content+= float(fatce) * 10 * float(item_qty)
                total_fibre_content+= float(fibtg) * 10 * float(item_qty)   
                total_carb_content+= float(choavldf) * 10 * float(item_qty)
                total_calories+= float(enerc) * 10 * float(item_qty)
                #for individual items
                item_protein+=float(protcnt) * 10 * float(item_qty)
                item_carb+=float(choavldf) * 10 * float(item_qty)
                item_fat+=float(fatce) * 10 * float(item_qty)
                item_fibre+=float(fibtg) * 10 * float(item_qty)   
            elif item_unit == 'g':
                #print(f"({item_qty} g.) | {item_name} | {food_code} | {item_unit} | {item_qty} | {(float(protcnt)/100)*(float(item_qty))} | {(float(fatce)/100)*(float(item_qty))} | {(float(fibtg)/100)*(float(item_qty))} | {(float(choavldf)/100)*(float(item_qty))} | {(float(enerc)/100)*(float(item_qty))}")
                total_protein_content+= (float(protcnt)/100)*(float(item_qty))
                total_fat_content+= (float(fatce)/100)*(float(item_qty))
                total_fibre_content+= (float(fibtg)/100)*(float(item_qty))
                total_carb_content+= (float(choavldf)/100)*(float(item_qty))
                total_calories+= (float(enerc)/100)*(float(item_qty))
                #for individual items
                item_protein+=(float(protcnt)/100)*(float(item_qty))
                item_carb+=(float(choavldf)/100)*(float(item_qty))
                item_fat+= (float(fatce)/100)*(float(item_qty))
                item_fibre+=(float(fibtg)/100)*(float(item_qty))
            elif item_unit == 'Pieces':
                total_protein_content+= 0
                total_fat_content+=0
                total_fibre_content+=0
                total_carb_content+=0
                total_calories+=0
                #for individual items
                item_protein+=0
                item_carb+=0
                item_fat+=0
                item_fibre+=0

            print(f'Calculation for {row['item_name']} in {row['item_cat']} category:')
            if row['item_cat'] == 'Animal Sourced':
                as_total_protein+=item_protein
                as_total_carb+=item_carb
                as_total_fat+=item_fat
                as_total_fiber+=item_fibre
            elif row['item_cat'] == 'Vegetables':
                vg_total_protein+=item_protein
                vg_total_carb+=item_carb
                vg_total_fat+=item_fat
                vg_total_fiber+=item_fibre
            elif row['item_cat'] == 'Pulses':
                pl_total_protein+=item_protein
                pl_total_carb+=item_carb
                pl_total_fat+=item_fat
                pl_total_fiber+=item_fibre

    food_cat_total_protein_list.append(as_total_protein)
    food_cat_total_protein_list.append(vg_total_protein)
    food_cat_total_protein_list.append(pl_total_protein)
    food_cat_total_carb_list.append(as_total_carb)
    food_cat_total_carb_list.append(vg_total_carb)
    food_cat_total_carb_list.append(pl_total_carb)
    food_cat_total_fat_list.append(as_total_fat)
    food_cat_total_fat_list.append(vg_total_fat)
    food_cat_total_fat_list.append(pl_total_fat)
    food_cat_total_fiber_list.append(as_total_fiber)
    food_cat_total_fiber_list.append(vg_total_fiber)
    food_cat_total_fiber_list.append(pl_total_fiber)
        
    return_context = {
        'total_protein_content':total_protein_content,
        'total_fat_content':total_fat_content,
        'total_fibre_content':total_fibre_content,
        'total_carb_content':total_carb_content,
        'total_calories':total_calories,
        'protcnt_nru':protcnt_nru,
        'fatce_nru':fatce_nru,
        'fibtg_nru':fibtg_nru,
        'choavldf_nru':choavldf_nru,
        'enerc_nru':enerc_nru,
        'food_cat_total_carb_list':food_cat_total_carb_list,
        'food_cat_total_protein_list':food_cat_total_protein_list,
        'food_cat_total_fat_list':food_cat_total_fat_list,
        'food_cat_total_fiber_list':food_cat_total_fiber_list
    }
    return return_context

def process_dietary_minerals(item_cat_group):
    total_fe_content = 0
    total_ca_content = 0
    total_mg_content = 0
    total_p_content = 0

    iron_nru = 0
    calcium_nru = 0
    magnesium_nru = 0
    phosphorus_nru = 0


    for _, row in item_cat_group.iterrows():
        item_name = row['item_name']
        item_unit = row['item_unit']
        item_qty = row['itemQty']
        item_code = Food.objects.filter(Q(food_name=item_name)|Q(food_name__icontains=item_name)|Q(description__icontains=item_name)).distinct().first()
        #for code in item_codes:
        if item_code:
            food_code = item_code.food_code
            dietary_minerals = MineralsAndTraceElements.objects.filter(food_code=food_code)
            fe = dietary_minerals[0].fe
            ca = dietary_minerals[0].ca
            mg = dietary_minerals[0].mg
            p = dietary_minerals[0].p

            iron_nru = NutritentReferenceUnit.objects.filter(nutrient='fe')[0].unit
            calcium_nru = NutritentReferenceUnit.objects.filter(nutrient='ca')[0].unit
            magnesium_nru = NutritentReferenceUnit.objects.filter(nutrient='mg')[0].unit
            phosphorus_nru = NutritentReferenceUnit.objects.filter(nutrient='p')[0].unit


            # print(f'100grams - {item_name} - {food_code} - {item_unit} - {item_qty} - {protcnt} - {fatce} - {fibtg} - {choavldf} - {enerc}')
            if item_unit == 'kg':
                #print(f"({item_qty} kg.) | {item_name} | {food_code} | {item_unit} | {item_qty} | {float(protcnt)*10*float(item_qty)} | {float(fatce)*10*float(item_qty)} | {float(fibtg)*10*float(item_qty)} | {float(choavldf)*10*float(item_qty)} | {float(enerc)*10*float(item_qty)}")
                total_fe_content+= float(fe) * 10 * float(item_qty)
                total_ca_content+= float(ca) * 10 * float(item_qty)
                total_mg_content+= float(mg) * 10 * float(item_qty)   
                total_p_content+= float(p) * 10 * float(item_qty)
            elif item_unit == 'g':
                #print(f"({item_qty} g.) | {item_name} | {food_code} | {item_unit} | {item_qty} | {(float(protcnt)/100)*(float(item_qty))} | {(float(fatce)/100)*(float(item_qty))} | {(float(fibtg)/100)*(float(item_qty))} | {(float(choavldf)/100)*(float(item_qty))} | {(float(enerc)/100)*(float(item_qty))}")
                total_fe_content+= (float(fe)/100)*(float(item_qty))
                total_ca_content+= (float(ca)/100)*(float(item_qty))
                total_mg_content+= (float(mg)/100)*(float(item_qty))
                total_p_content+= (float(p)/100)*(float(item_qty))
            elif item_unit == 'Pieces':
                total_fe_content+= 0
                total_ca_content+=0
                total_mg_content+=0
                total_p_content+=0

        return_context = {
            'total_fe_content':total_fe_content,
            'total_ca_content':total_ca_content,
            'total_mg_content':total_mg_content,
            'total_p_content':total_p_content,
            'iron_nru':iron_nru,
            'calcium_nru':calcium_nru,
            'magnesium_nru':magnesium_nru,
            'phosphorus_nru':phosphorus_nru
        }
    return return_context

def process_dietary_vitamins(item_cat_group):
    total_vita_content = 0.0
    total_vitd_content = 0.0
    total_vite_content = 0.0
    total_vitk_content = 0.0
    total_vitc_content = 0.0
    vita_nru = 0.0
    vitd_nru = 0.0
    vite_nru = 0.0
    vitk_nru = 0.0
    vitc_nru = 0.0

    for _, row in item_cat_group.iterrows():
        item_name = row['item_name']
        item_unit = row['item_unit']
        item_qty = row['itemQty']
        item_code = Food.objects.filter(Q(food_name=item_name)|Q(food_name__icontains=item_name)|Q(description__icontains=item_name)).distinct().first()
        #for code in item_codes:
        if item_code:
            food_code = item_code.food_code
            dietary_vitamins_f = FatSolubleVitamins.objects.filter(food_code=food_code)
            dietary_carotenoids = Carotenoids.objects.filter(food_code=food_code)
            dietary_vitamins_w = WaterSolubleVitamins.objects.filter(food_code=food_code)
            #vitamin a
            retol = dietary_vitamins_f[0].retol or 0.0
            cartb = dietary_carotenoids[0].cartb or 0.0
            carta = dietary_carotenoids[0].carta or 0.0
            crypxb = dietary_carotenoids[0].crypxb or 0.0
            #vitamin d
            ergcal = dietary_vitamins_f[0].ergcal or 0.0
            chocal = dietary_vitamins_f[0].chocal or 0.0
            #vitamin e
            tocpha = dietary_vitamins_f[0].tocpha
            tocphb = dietary_vitamins_f[0].tocphb
            tocphg = dietary_vitamins_f[0].tocphg
            tocphd = dietary_vitamins_f[0].tocphd
            toctra = dietary_vitamins_f[0].toctra
            toctrb = dietary_vitamins_f[0].toctrb
            toctrg = dietary_vitamins_f[0].toctrg
            toctrd = dietary_vitamins_f[0].toctrd
            #vitamin k
            vitk1 = dietary_vitamins_f[0].vitk1
            vitk2 = dietary_vitamins_f[0].vitk2
            #vitamin c
            vitc = dietary_vitamins_w[0].vitc



            vita = retol + (cartb / 12.0) + (carta / 24.0) + (crypxb / 24.0)
            vitd = ergcal + chocal
            vite = tocpha + tocphb + tocphg + tocphd + toctra + toctrb + toctrg + toctrd
            vitk = vitk1 + vitk2
            vitc = vitc


            vita_nru = NutritentReferenceUnit.objects.filter(nutrient='retol')[0].unit
            vitd_nru = NutritentReferenceUnit.objects.filter(nutrient='ergcal')[0].unit
            vite_nru = NutritentReferenceUnit.objects.filter(nutrient='vite')[0].unit
            vitk_nru = NutritentReferenceUnit.objects.filter(nutrient='vitk1')[0].unit
            vitc_nru = NutritentReferenceUnit.objects.filter(nutrient='vitc')[0].unit


            # print(f'100grams - {item_name} - {food_code} - {item_unit} - {item_qty} - {protcnt} - {fatce} - {fibtg} - {choavldf} - {enerc}')
            if item_unit == 'kg':
                #print(f"({item_qty} kg.) | {item_name} | {food_code} | {item_unit} | {item_qty} | {float(protcnt)*10*float(item_qty)} | {float(fatce)*10*float(item_qty)} | {float(fibtg)*10*float(item_qty)} | {float(choavldf)*10*float(item_qty)} | {float(enerc)*10*float(item_qty)}")
                total_vita_content+= float(vita) * 10 * float(item_qty)
                total_vitd_content+= float(vitd) * 10 * float(item_qty)
                total_vite_content+= float(vite) * 10 * float(item_qty)   
                total_vitk_content+= float(vitk) * 10 * float(item_qty)
                total_vitc_content+= float(vitc) * 10 * float(item_qty)
            elif item_unit == 'g':
                #print(f"({item_qty} g.) | {item_name} | {food_code} | {item_unit} | {item_qty} | {(float(protcnt)/100)*(float(item_qty))} | {(float(fatce)/100)*(float(item_qty))} | {(float(fibtg)/100)*(float(item_qty))} | {(float(choavldf)/100)*(float(item_qty))} | {(float(enerc)/100)*(float(item_qty))}")
                total_vita_content+= (float(vita)/100)*(float(item_qty))
                total_vitd_content+= (float(vitd)/100)*(float(item_qty))
                total_vite_content+= (float(vite)/100)*(float(item_qty))
                total_vitk_content+= (float(vitk)/100)*(float(item_qty))
                total_vitc_content+= (float(vitc)/100)*(float(item_qty))
            elif item_unit == 'Pieces':
                total_vita_content+= 0
                total_vitd_content+=0
                total_vite_content+=0
                total_vitk_content+=0
                total_vitc_content+=0

        return_context = {
                'total_vita_content':total_vita_content,
                'total_vitd_content':total_vitd_content,
                'total_vite_content':total_vite_content,
                'total_vitk_content':total_vitk_content,
                'total_vitc_content':total_vitc_content,
                'vita_nru':vita_nru,
                'vitd_nru':vitd_nru,
                'vite_nru':vite_nru,
                'vitk_nru':vitk_nru,
                'vitc_nru':vitc_nru
            }
    return return_context

def fetch_api_data(request):
    # API URL (first page)
    url = "https://farmerharvest.in/api/orders/"

    all_users = []

    # Fetch all pages
    while url:
        resp = requests.get(url)
        data = resp.json()
        all_users.extend(data['results'])  # accumulate all users
        url = data['next']  # next page URL, None if last page

    # Flatten order_details into rows, keeping user and school info
    df = pd.json_normalize(
        all_users,
        record_path='order_details',                    # explode each order detail
        meta=['id', 'first_name', 'userType',          # keep user info
            ['school_info', 'total_students'],
            ['school_info', 'total_students_with_preprimary']],
        sep='_'
    )

    #checks whether any data fetched or not! if not fetched the make data = false
    if df.empty:
        messages.error(request, 'No data found!')
        return {'Data':False}

    # Group by item to get total quantities
    item_cat_group = df.groupby(
        ['item_name', 'item_cat', 'item_unit'], as_index=False
    )['itemQty'].sum()

    #global view of whole data like number of schools etc.
    student_json = pd.json_normalize(
        data["results"],
        sep="_"
    )
    student_i_v_df = student_json[[
        "first_name",
        "school_info_pre_primary_students","school_info_i_students","school_info_ii_students",
        "school_info_iii_students","school_info_iv_students","school_info_v_students",
        "school_info_total_students"
    ]]
    student_vi_x_df = student_json[[
        "first_name",
        "school_info_vi_students","school_info_vii_students","school_info_viii_students",
        "school_info_ix_students","school_info_x_students",
        "school_info_total_students"
    ]]

    no_of_schools = df['first_name'].nunique()

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


    no_of_students_i_v = int(student_df['primary_students'].sum())
    no_of_students_vi_x = int(student_df['upper_students'].sum())
    no_of_students = no_of_students_i_v + no_of_students_vi_x
    food_cat_summary_labels = df["item_cat"].unique().tolist()

    dietary_fibre_context = process_dietary_fibre(item_cat_group=item_cat_group)
    dietary_minerals_context = process_dietary_minerals(item_cat_group=item_cat_group)
    dietary_vitamins_context = process_dietary_vitamins(item_cat_group=item_cat_group)

    return_context = {
        'no_of_schools': no_of_schools,
        'no_of_students': no_of_students,
        'no_of_students_i_v':no_of_students_i_v,
        'no_of_students_vi_x':no_of_students_vi_x,
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
    if not site_online():
        messages.error(request, 'Please connect to internet!')
    else:
        api_data = fetch_api_data(request)
        if api_data['Data'] == False: #checks whether data found or not
            messages.error(request, 'Error in fetching data!')
            return HttpResponse('Data not found!')

        rda_macro_labels = ['Energy', 'Carbohydrates', 'Protein', 'Fat', 'Fibre']
        rda_micro_labels_vitamins = ['Vit-A', 'Vit-D', 'Vit-E', 'Vit-K', 'Vit-C']
        rda_micro_labels_minerals = ['Iron', 'Calcium', 'Magnesium', 'Phosphorus']
        rda_macro_coverage = [80, 70, 75, 60, 90]
        rda_micro_coverage_vitamins = [80, 70, 75, 60, 90]
        rda_micro_coverage_minerals = [0, 0, 0, 0]

        mdm_target_calories_data = []
        mdm_target_protein_data = []
        mdm_achieved_calories_data = []
        mdm_achieved_protein_data = []

        mdm_target_total_calorie_i_v = 2962 if int(api_data['no_of_students_i_v']) > 0 else 0
        mdm_target_avg_calorie_i_v = 493 if int(api_data['no_of_students_i_v']) > 0 else 0
        mdm_target_total_calorie_vi_x = 4372 if int(api_data['no_of_students_vi_x']) > 0 else 0
        mdm_target_avg_calorie_vi_x = 729 if int(api_data['no_of_students_vi_x']) > 0 else 0
        mdm_target_calories_data.append(mdm_target_total_calorie_i_v)
        mdm_target_calories_data.append(mdm_target_avg_calorie_i_v)
        mdm_target_calories_data.append(mdm_target_total_calorie_vi_x)
        mdm_target_calories_data.append(mdm_target_avg_calorie_vi_x)

        mdm_target_total_protein_i_v = 83 if int(api_data['no_of_students_i_v']) > 0 else 0
        mdm_target_avg_protein_i_v = 14 if int(api_data['no_of_students_i_v']) > 0 else 0
        mdm_target_total_protein_vi_x = 123 if int(api_data['no_of_students_vi_x']) > 0 else 0
        mdm_target_avg_protein_vi_x = 21 if int(api_data['no_of_students_vi_x']) > 0 else 0
        mdm_target_protein_data.append(mdm_target_total_protein_i_v)
        mdm_target_protein_data.append(mdm_target_avg_protein_i_v)
        mdm_target_protein_data.append(mdm_target_total_protein_vi_x)
        mdm_target_protein_data.append(mdm_target_avg_protein_vi_x)


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
        unit_calories = total_calories / api_data['no_of_students']
        unit_carb_content = total_carb_content / api_data['no_of_students']
        unit_protein_content = total_protein_content / api_data['no_of_students']
        unit_fat_content = total_fat_content / api_data['no_of_students']
        unit_fibre_content = total_fibre_content / api_data['no_of_students']

        #micro nutrients-vitamins
        unit_vit_a_content = total_vit_a_content / api_data['no_of_students']
        unit_vit_d_content = total_vit_d_content / api_data['no_of_students']
        unit_vit_e_content = total_vit_e_content / api_data['no_of_students']
        unit_vit_k_content = total_vit_k_content / api_data['no_of_students']
        unit_vit_c_content = total_vit_c_content / api_data['no_of_students']

        #micro nutrients-minerals
        unit_iron_content = total_iron_content / api_data['no_of_students']
        unit_calcium_content = total_calcium_content / api_data['no_of_students']
        unit_magnesium_content = total_magnesium_content / api_data['no_of_students']
        unit_phosphorus_content = total_phosphorus_content / api_data['no_of_students']

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
            
        
        for key in rda_macro_ref.keys():
            if key == 'energy':
                rda_macro_coverage[0] = (unit_calories / rda_macro_ref[key]) * 100
            elif key == 'carbohydrates':
                rda_macro_coverage[1] = (unit_carb_content / rda_macro_ref[key]) * 100
            elif key == 'protein':
                rda_macro_coverage[2] = (unit_protein_content / rda_macro_ref[key]) * 100
            elif key == 'fat':
                rda_macro_coverage[3] = (unit_fat_content / rda_macro_ref[key]) * 100
            elif key == 'fibre':
                rda_macro_coverage[4] = (unit_fibre_content / rda_macro_ref[key]) * 100
        
        for key in rda_micro_ref_vitamins.keys():
            if key == 'vit-a':
                rda_micro_coverage_vitamins[0] = (unit_vit_a_content / rda_micro_ref_vitamins[key]) * 100
            elif key == 'vit-d':
                rda_micro_coverage_vitamins[1] = (unit_vit_d_content / rda_micro_ref_vitamins[key]) * 100
            elif key == 'vit-e':
                rda_micro_coverage_vitamins[2] = (unit_vit_e_content / rda_micro_ref_vitamins[key]) * 100
            elif key == 'vit-k':
                rda_micro_coverage_vitamins[3] = (unit_vit_k_content / rda_micro_ref_vitamins[key]) * 100
            elif key == 'vit-c':
                rda_micro_coverage_vitamins[4] = (unit_vit_c_content / rda_micro_ref_vitamins[key]) * 100
        
        for key in rda_micro_ref_minerals.keys():
            if key == 'iron':
                rda_micro_coverage_minerals[0] = (unit_iron_content / rda_micro_ref_minerals[key]) * 100
            elif key == 'calcium':
                rda_micro_coverage_minerals[1] = (unit_calcium_content / rda_micro_ref_minerals[key]) * 100
            elif key == 'magnesium':
                rda_micro_coverage_minerals[2] = (unit_magnesium_content / rda_micro_ref_minerals[key]) * 100
            elif key == 'phosphorus':
                rda_micro_coverage_minerals[3] = (unit_phosphorus_content / rda_micro_ref_minerals[key]) * 100

        #print(f'{api_data['dietary_fibre_context']['food_cat_total_carb_list']}')
        return_context = {
            'states':json.dumps(LIST_STATES),
            'no_of_schools': api_data['no_of_schools'],
            'no_of_students': api_data['no_of_students'],
            'no_of_students_i_v':api_data['no_of_students_i_v'],
            'no_of_students_vi_x':api_data['no_of_students_vi_x'],
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
            
            'unit_protein_content': f'{api_data['total_protein_content']/api_data['no_of_students']}',
            'unit_fat_content': f'{api_data['total_fat_content']/api_data['no_of_students']}',
            'unit_fibre_content': f'{api_data['total_fibre_content']/api_data['no_of_students']}',
            'unit_carb_content': f'{api_data['total_carb_content']/api_data['no_of_students']}',
            'unit_calories': f'{api_data['total_calories']/api_data['no_of_students']}',
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

            'api_data': api_data,
            'item_cat_group': api_data['item_cat_group'],
            'rda_macro_labels':json.dumps(rda_macro_labels),
            'rda_macro_coverage':json.dumps(rda_macro_coverage),
            'rda_micro_labels_vitamins':json.dumps(rda_micro_labels_vitamins),
            'rda_micro_coverage_vitamins':json.dumps(rda_micro_coverage_vitamins),
            'rda_micro_labels_minerals':json.dumps(rda_micro_labels_minerals),
            'rda_micro_coverage_minerals':json.dumps(rda_micro_coverage_minerals),
        }
        return render(request, 'dashboard.html', context=return_context)
    return render(request, 'dashboard.html', context={})

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
