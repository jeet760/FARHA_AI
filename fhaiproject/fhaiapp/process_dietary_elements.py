from django.db.models import Q, Max, Min, Sum, Count, OuterRef, Subquery, F, Value
from .models import NutritentReferenceUnit, Food, DietaryFibre, WaterSolubleVitamins, FatSolubleVitamins, Carotenoids, MineralsAndTraceElements, StarchAndSugars, FattyAcid, AminoAcid, OrganicAcid, Polyphenols, Oligosaccharides, PhytosterolsPhytateSaponin
import pandas as pd
class PDE:
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
                    if item_name == 'Egg':
                        item_qty = item_qty * 50  # assuming average egg weight is 50g
                        total_protein_content+= (float(protcnt)/100)*(float(item_qty))
                        total_fat_content+= (float(fatce)/100)*(float(item_qty))
                        total_fibre_content+=(float(fibtg)/100)*(float(item_qty))
                        total_carb_content+=(float(choavldf)/100)*(float(item_qty))
                        total_calories+=(float(enerc)/100)*(float(item_qty))
                        #for individual items
                        item_protein+=(float(protcnt)/100)*(float(item_qty))
                        item_carb+=(float(choavldf)/100)*(float(item_qty))
                        item_fat+=(float(fatce)/100)*(float(item_qty))
                        item_fibre+=(float(fibtg)/100)*(float(item_qty))

                #print(f'Calculation for {row['item_name']} in {row['item_cat']} category:')
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

    def process_proximates(item_cat_group):
        # Pre-fetch NRU units (once only)
        nru_map = {
            "protcnt": NutritentReferenceUnit.objects.get(nutrient="protcnt").unit,
            "fatce": NutritentReferenceUnit.objects.get(nutrient="fatce").unit,
            "fibtg": NutritentReferenceUnit.objects.get(nutrient="fibtg").unit,
            "choavldf": NutritentReferenceUnit.objects.get(nutrient="choavldf").unit,
            "enerc": "kcal",
        }

        # Attach food_code and nutrient values to rows
        def get_nutrients(item_name):
            food = (
                Food.objects.filter(
                    Q(food_name=item_name)
                    | Q(food_name__icontains=item_name)
                    | Q(description__icontains=item_name)
                )
                .distinct()
                .first()
            )
            if not food:
                return pd.Series([0, 0, 0, 0, 0], 
                                index=["protcnt", "fatce", "fibtg", "choavldf", "enerc"])
            df = DietaryFibre.objects.filter(food_code=food.food_code).values().first()
            return pd.Series({
                "protcnt": df["protcnt"],
                "fatce": df["fatce"],
                "fibtg": df["fibtg"],
                "choavldf": df["choavldf"],
                "enerc": float(df["enerc"]) / 4.18,
            })

        nutrients_df = item_cat_group["item_name"].apply(get_nutrients)
        df = pd.concat([item_cat_group, nutrients_df], axis=1)

        # Handle units → conversion factors
        def qty_factor(row):
            if row.item_unit == "kg":
                return 10 * float(row.itemQty)   # 1kg = 1000g → (1000/100)=10
            elif row.item_unit == "g":
                return float(row.itemQty) / 100
            elif row.item_unit == "Pieces" and row.item_name == "Egg":
                return (row.itemQty * 50) / 100  # avg 50g per egg
            return 0

        df["factor"] = df.apply(qty_factor, axis=1)

        # Calculate contributions
        for col in ["protcnt", "fatce", "fibtg", "choavldf", "enerc"]:
            df[col + "_total"] = df[col].astype(float) * df["factor"]

        # Grand totals
        totals = df[["protcnt_total","fatce_total","fibtg_total","choavldf_total","enerc_total"]].sum()

        # Group by category (Animal Sourced / Vegetables / Pulses)
        grouped = df.groupby("item_cat")[["protcnt_total","fatce_total","fibtg_total","choavldf_total"]].sum()

        return {
            "total_protein_content": totals["protcnt_total"],
            "total_fat_content": totals["fatce_total"],
            "total_fibre_content": totals["fibtg_total"],
            "total_carb_content": totals["choavldf_total"],
            "total_calories": totals["enerc_total"],
            "protcnt_nru": nru_map["protcnt"],
            "fatce_nru": nru_map["fatce"],
            "fibtg_nru": nru_map["fibtg"],
            "choavldf_nru": nru_map["choavldf"],
            "enerc_nru": nru_map["enerc"],
            "food_cat_total_protein_list": grouped["protcnt_total"].tolist(),
            "food_cat_total_carb_list": grouped["choavldf_total"].tolist(),
            "food_cat_total_fat_list": grouped["fatce_total"].tolist(),
            "food_cat_total_fiber_list": grouped["fibtg_total"].tolist(),
        }
    
    def process_item_proximates(item_cat_group):
        # Pre-fetch NRU units (once only)
        nru_map = {
            "protcnt": NutritentReferenceUnit.objects.get(nutrient="protcnt").unit,
            "fatce": NutritentReferenceUnit.objects.get(nutrient="fatce").unit,
            "fibtg": NutritentReferenceUnit.objects.get(nutrient="fibtg").unit,
            "choavldf": NutritentReferenceUnit.objects.get(nutrient="choavldf").unit,
            "enerc": "kcal",
        }

        # Attach food_code and nutrient values to rows
        def get_nutrients(item_name):
            food = (
                Food.objects.filter(
                    Q(food_name=item_name)
                    | Q(food_name__icontains=item_name)
                    | Q(description__icontains=item_name)
                )
                .distinct()
                .first()
            )
            if not food:
                return pd.Series([0, 0, 0, 0, 0], 
                                index=["protcnt", "fatce", "fibtg", "choavldf", "enerc"])
            df = DietaryFibre.objects.filter(food_code=food.food_code).values().first()
            return pd.Series({
                "protcnt": df["protcnt"],
                "fatce": df["fatce"],
                "fibtg": df["fibtg"],
                "choavldf": df["choavldf"],
                "enerc": float(df["enerc"]) / 4.18,
            })

        nutrients_df = item_cat_group["item_name"].apply(get_nutrients)
        df = pd.concat([item_cat_group, nutrients_df], axis=1)

        # Handle units → conversion factors
        def qty_factor(row):
            if row.item_unit == "kg":
                return 10 * float(row.itemQty)   # 1kg = 1000g → (1000/100)=10
            elif row.item_unit == "g":
                return float(row.itemQty) / 100
            elif row.item_unit == "Pieces" and row.item_name == "Egg":
                return (row.itemQty * 50) / 100  # avg 50g per egg
            return 0

        df["factor"] = df.apply(qty_factor, axis=1)

        # Calculate contributions
        for col in ["protcnt", "fatce", "fibtg", "choavldf", "enerc"]:
            df[col + "_total"] = df[col].astype(float) * df["factor"]

        # Grand totals
        totals = df[["protcnt_total","fatce_total","fibtg_total","choavldf_total","enerc_total"]].sum()

        # Group by category (Animal Sourced / Vegetables / Pulses)
        grouped = df.groupby("item_cat")[["protcnt_total","fatce_total","fibtg_total","choavldf_total"]].sum()

        return df
    
    def process_item_vitamins(item_cat_group):
        # Pre-fetch NRU units (once only)
        nru_map = {
            #vitamin a
            "retol": NutritentReferenceUnit.objects.get(nutrient="retol").unit,
            "cartb": NutritentReferenceUnit.objects.get(nutrient="cartb").unit,
            "carta": NutritentReferenceUnit.objects.get(nutrient="carta").unit,
            "crypxb": NutritentReferenceUnit.objects.get(nutrient="crypxb").unit,
            #vitamin D
            "ergcal": NutritentReferenceUnit.objects.get(nutrient="ergcal").unit,
            "chocal": NutritentReferenceUnit.objects.get(nutrient="chocal").unit,
            #vitamin e
            "tocpha": NutritentReferenceUnit.objects.get(nutrient="tocpha").unit,
            "tocphb": NutritentReferenceUnit.objects.get(nutrient="tocphb").unit,
            "tocphg": NutritentReferenceUnit.objects.get(nutrient="tocphg").unit,
            "tocphd": NutritentReferenceUnit.objects.get(nutrient="tocphd").unit,
            "toctra": NutritentReferenceUnit.objects.get(nutrient="toctra").unit,
            "toctrb": NutritentReferenceUnit.objects.get(nutrient="toctrb").unit,
            "toctrg": NutritentReferenceUnit.objects.get(nutrient="toctrg").unit,
            "toctrd": NutritentReferenceUnit.objects.get(nutrient="toctrd").unit,
            #vitamin k
            "vitk1": NutritentReferenceUnit.objects.get(nutrient="vitk1").unit,
            "vitk2": NutritentReferenceUnit.objects.get(nutrient="vitk2").unit,
            #vitamin c
            "vitc": NutritentReferenceUnit.objects.get(nutrient="vitc").unit,
        }

        # Attach food_code and nutrient values to rows
        def get_nutrients(item_name):
            food = (
                Food.objects.filter(
                    Q(food_name=item_name)
                    | Q(food_name__icontains=item_name)
                    | Q(description__icontains=item_name)
                )
                .distinct()
                .first()
            )
            if not food:
                return pd.Series([0, 0, 0, 0, 0], 
                                index=["vita", "vitc", "vitd", "vite", "vitk"])
            dietary_vitamins_f = FatSolubleVitamins.objects.filter(food_code=food.food_code).values().first()
            dietary_vitamins_w = WaterSolubleVitamins.objects.filter(food_code=food.food_code).values().first()
            dietary_carotenoids = Carotenoids.objects.filter(food_code=food.food_code).values().first()
            #vitamin a
            retol = dietary_vitamins_f['retol'] or 0.0 #µg
            cartb = dietary_carotenoids['cartb'] or 0.0 #µg
            carta = dietary_carotenoids['carta'] or 0.0 #µg
            crypxb = dietary_carotenoids['crypxb'] or 0.0 #µg
            #vitamin d
            ergcal = dietary_vitamins_f['ergcal'] or 0.0 #µg
            chocal = dietary_vitamins_f['chocal'] or 0.0 #µg
            #vitamin e
            tocpha = dietary_vitamins_f['tocpha'] or 0.0 #mg
            tocphb = dietary_vitamins_f['tocphb'] or 0.0 #mg
            tocphg = dietary_vitamins_f['tocphg'] or 0.0 #mg
            tocphd = dietary_vitamins_f['tocphd'] or 0.0 #mg
            toctra = dietary_vitamins_f['toctra'] or 0.0 #mg
            toctrb = dietary_vitamins_f['toctrb'] or 0.0 #mg
            toctrg = dietary_vitamins_f['toctrg'] or 0.0 #mg
            toctrd = dietary_vitamins_f['toctrd'] or 0.0 #mg
            #vitamin k
            vitk1 = dietary_vitamins_f['vitk1'] or 0.0 #µg
            vitk2 = dietary_vitamins_f['vitk2'] or 0.0 #µg
            #vitamin c
            vitc = dietary_vitamins_w['vitc'] or 0.0 #mg

            vita = retol + (cartb / 12.0) + (carta / 24.0) + (crypxb / 24.0)
            vitd = ergcal + chocal
            vite = tocpha + tocphb + tocphg + tocphd + toctra + toctrb + toctrg + toctrd
            vitk = vitk1 + vitk2

            return pd.Series({
                "vita": vita,
                "vitc": vitc,
                "vitd": vitd,
                "vite": vite,
                "vitk": vitk
            })

        nutrients_df = item_cat_group["item_name"].apply(get_nutrients)
        df = pd.concat([item_cat_group, nutrients_df], axis=1)

        # Handle units → conversion factors
        def qty_factor(row):
            if row.item_unit == "kg":
                return 10 * float(row.itemQty)   # 1kg = 1000g → (1000/100)=10
            elif row.item_unit == "g":
                return float(row.itemQty) / 100
            elif row.item_unit == "Pieces" and row.item_name == "Egg":
                return (row.itemQty * 50) / 100  # avg 50g per egg
            return 0

        df["factor"] = df.apply(qty_factor, axis=1)

        # Calculate contributions
        for col in ["vita", "vitc", "vitd", "vite", "vitk"]:
            df[col + "_total"] = df[col].astype(float) * df["factor"]

        # Grand totals
        totals = df[["vita_total","vitc_total","vitd_total","vite_total","vitk_total"]].sum()

        # Group by category (Animal Sourced / Vegetables / Pulses)
        grouped = df.groupby("item_cat")[["vita_total","vitc_total","vitd_total","vite_total","vitk_total"]].sum()

        # cols_to_sum = ["vita", "vitc", "vitd", "vite", "vitk", "vita_total","vitc_total","vitd_total","vite_total","vitk_total"]
        # sum_row = df[cols_to_sum].sum()
        # total_row = {col: "" for col in df.columns}
        # for col in cols_to_sum:
        #     total_row[col] = sum_row[col]
        # df.loc["Total"] = total_row
        # print(df)
        return df

    def process_item_minerals(item_cat_group):
        # Pre-fetch NRU units (once only)
        nru_map = {
            "fe": NutritentReferenceUnit.objects.get(nutrient="fe").unit,
            "ca": NutritentReferenceUnit.objects.get(nutrient="ca").unit,
            "mg": NutritentReferenceUnit.objects.get(nutrient="mg").unit,
            "p": NutritentReferenceUnit.objects.get(nutrient="p").unit,
            "k": NutritentReferenceUnit.objects.get(nutrient="k").unit,
        }

        # Attach food_code and nutrient values to rows
        def get_nutrients(item_name):
            food = (
                Food.objects.filter(
                    Q(food_name=item_name)
                    | Q(food_name__icontains=item_name)
                    | Q(description__icontains=item_name)
                )
                .distinct()
                .first()
            )
            if not food:
                return pd.Series([0, 0, 0, 0, 0], 
                                index=["fe", "ca", "mg", "p", "k"])
            df = MineralsAndTraceElements.objects.filter(food_code=food.food_code).values().first()
            return pd.Series({
                "fe": df["fe"],
                "ca": df["ca"],
                "mg": df["mg"],
                "p": df["p"],
                "k": df["k"],
            })

        nutrients_df = item_cat_group["item_name"].apply(get_nutrients)
        df = pd.concat([item_cat_group, nutrients_df], axis=1)

        # Handle units → conversion factors
        def qty_factor(row):
            if row.item_unit == "kg":
                return 10 * float(row.itemQty)   # 1kg = 1000g → (1000/100)=10
            elif row.item_unit == "g":
                return float(row.itemQty) / 100
            elif row.item_unit == "Pieces" and row.item_name == "Egg":
                return (row.itemQty * 50) / 100  # avg 50g per egg
            return 0

        df["factor"] = df.apply(qty_factor, axis=1)

        # Calculate contributions
        for col in ["fe", "ca", "mg", "p", "k"]:
            df[col + "_total"] = df[col].astype(float) * df["factor"]

        # Grand totals
        totals = df[["fe_total","ca_total","mg_total","p_total","k_total"]].sum()

        # Group by category (Animal Sourced / Vegetables / Pulses)
        grouped = df.groupby("item_cat")[["fe_total","ca_total","mg_total","p_total","k_total"]].sum()

        return df