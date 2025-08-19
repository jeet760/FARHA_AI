import os
import sys
import django
from tqdm import tqdm
from django.db import transaction
from django.conf import settings
import shutil

# Step 1: Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Step 2: Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fhaiproject.settings')

# Step 3: Setup Django
django.setup()

# Now you can import your models
from fhaiapp.models import NutritentReferenceUnit, Food, DietaryFibre, WaterSolubleVitamins, FatSolubleVitamins, Carotenoids, MineralsAndTraceElements, StarchAndSugars, FattyAcid, AminoAcid, OrganicAcid, Polyphenols, Oligosaccharides, PhytosterolsPhytateSaponin
import csv

# def import_dietary_fibre_data():
#     print("🔄 Deleting old data...")
#     DietaryFibre.objects.all().delete()

#     file_path = 'fhaiproject/dietary_fibre.csv'
#     BATCH_SIZE = 1000
#     dietary_fibre_list = []

#     # Get total lines for tqdm
#     with open(file_path, 'r', encoding='utf-8') as f:
#         total = sum(1 for _ in f) - 1  # minus header

#     with open(file_path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)

#         for row in tqdm(reader, total=total, desc="📦 Importing Dietary Fibre Data"):
#             try:
#                 obj = DietaryFibre(
#                     food_code = row['\ufefffood_code'],
#                     food_id = Food.objects.get(food_code=row['\ufefffood_code']),
#                     water = float(row['WATER']),
#                     water_sd = float(row['water_sd']),
#                     protcnt = float(row['PROTCNT']),
#                     protcnt_sd = float(row['protcnt_sd']),
#                     ash = float(row['ASH']),
#                     ash_sd = float(row['ash_sd']),
#                     fatce = float(row['FATCE']),
#                     fatce_sd = float(row['fatce_sd']),
#                     fibtg = float(row['FIBTG']),
#                     fibtg_sd = float(row['fibtg_sd']),
#                     fibins = float(row['FIBINS']),
#                     fibins_sd = float(row['fibins_sd']),
#                     fibsol = float(row['FIBSOL']),
#                     fibsol_sd = float(row['fibsol_sd']),
#                     choavldf = float(row['CHOAVLDF']),
#                     choavldf_sd = float(row['choavldf_sd']),
#                     enerc = float(row['ENERC']),
#                     enerc_sd = float(row['enerc_sd']),
#                 )
#                 dietary_fibre_list.append(obj)
#                 if len(dietary_fibre_list) >= BATCH_SIZE:
#                     DietaryFibre.objects.bulk_create(dietary_fibre_list)
#                     dietary_fibre_list = []

#             except Exception as e:
#                 print(f"❌ Error processing row: {row}")
#                 print(f"Error: {e}")

#         # Insert remaining records
#         if dietary_fibre_list:
#             DietaryFibre.objects.bulk_create(dietary_fibre_list)

#     print("✅ Data import completed successfully.")

# def import_vitams_w_data():
#     print("🔄 Deleting old data...")
#     WaterSolubleVitamins.objects.all().delete()

#     file_path = 'fhaiproject/vitamins_w.csv'
#     BATCH_SIZE = 1000
#     dietary_fibre_list = []

#     # Get total lines for tqdm
#     with open(file_path, 'r', encoding='utf-8') as f:
#         total = sum(1 for _ in f) - 1  # minus header

#     with open(file_path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)

#         for row in tqdm(reader, total=total, desc="📦 Importing Dietary Fibre Data"):
#             try:
#                 obj = WaterSolubleVitamins(
#                     food_code = row['\ufefffood_code'],
#                     food_id = Food.objects.get(food_code=row['\ufefffood_code']),
#                     thia = float(row['THIA']),
#                     thia_sd = float(row['thia_sd']),
#                     ribf = float(row['RIBF']),
#                     ribf_sd = float(row['ribf_sd']),
#                     nia = float(row['NIA']),
#                     nia_sd = float(row['nia_sd']),
#                     pantac = float(row['PANTAC']),
#                     pantac_sd = float(row['pantac_sd']),
#                     vitb6a = float(row['VITB6A']),
#                     vitb6a_sd = float(row['vitb6a_sd']),
#                     biot = float(row['BIOT']),
#                     biot_sd = float(row['biot_sd']),
#                     folsum = float(row['FOLSUM']),
#                     folsum_sd = float(row['folsum_sd']),
#                     vitc = float(row['VITC']),
#                     vitc_sd = float(row['vitc_sd']),
#                 )
#                 dietary_fibre_list.append(obj)
#                 if len(dietary_fibre_list) >= BATCH_SIZE:
#                     WaterSolubleVitamins.objects.bulk_create(dietary_fibre_list)
#                     dietary_fibre_list = []

#             except Exception as e:
#                 print(f"❌ Error processing row: {row}")
#                 print(f"Error: {e}")

#         # Insert remaining records
#         if dietary_fibre_list:
#             WaterSolubleVitamins.objects.bulk_create(dietary_fibre_list)

#     print("✅ Data import completed successfully.")

def import_minerals_data():
    print("🔄 Deleting old data...")
    MineralsAndTraceElements.objects.all().delete()

    file_path = 'fhaiproject/minerals.csv'
    BATCH_SIZE = 1000
    dietary_fibre_list = []

    # Get total lines for tqdm
    with open(file_path, 'r', encoding='utf-8') as f:
        total = sum(1 for _ in f) - 1  # minus header

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in tqdm(reader, total=total, desc="📦 Importing Dietary Fibre Data"):
            try:
                obj = MineralsAndTraceElements(
                    food_code = row['\ufefffood_code'],
                    food_id = Food.objects.get(food_code=row['\ufefffood_code']),
                    al = float(row['AL']),
                    al_sd = float(row['al_sd']),
                    As = float(row['AS']),
                    As_sd = float(row['As_sd']),
                    cd = float(row['CD']),
                    cd_sd = float(row['cd_sd']),
                    ca = float(row['CA']),
                    ca_sd = float(row['ca_sd']),
                    cr = float(row['CR']),
                    cr_sd = float(row['cr_sd']),
                    co = float(row['CO']),
                    co_sd = float(row['co_sd']),
                    cu = float(row['CU']),
                    cu_sd = float(row['cu_sd']),
                    fe = float(row['FE']),
                    fe_sd = float(row['fe_sd']),
                    pb = float(row['PB']),
                    pb_sd = float(row['pb_sd']),
                    li = float(row['LI']),
                    li_sd = float(row['li_sd']),
                    mg = float(row['MG']),
                    mg_sd = float(row['mg_sd']),
                    mn = float(row['MN']),
                    mn_sd = float(row['mn_sd']),
                    hg = float(row['HG']),
                    hg_sd = float(row['hg_sd']),
                    mo = float(row['MO']),
                    mo_sd = float(row['mo_sd']),
                    ni = float(row['NI']),
                    ni_sd = float(row['ni_sd']),
                    p = float(row['P']),
                    p_sd = float(row['p_sd']),
                    k = float(row['K']),
                    k_sd = float(row['k_sd']),
                    se = float(row['SE']),
                    se_sd = float(row['se_sd']),
                    na = float(row['NA']),
                    na_sd = float(row['na_sd']),
                    zn = float(row['ZN']),
                    zn_sd = float(row['zn_sd']),
                )
                dietary_fibre_list.append(obj)
                #print(dietary_fibre_list)
                if len(dietary_fibre_list) >= BATCH_SIZE:
                    MineralsAndTraceElements.objects.bulk_create(dietary_fibre_list)
                    dietary_fibre_list = []

            except Exception as e:
                print(f"❌ Error processing row: {row}")
                print(f"Error: {e}")

        # Insert remaining records
        if dietary_fibre_list:
            MineralsAndTraceElements.objects.bulk_create(dietary_fibre_list)

    print("✅ Data import completed successfully.")

if __name__ == '__main__':
    import_minerals_data()