from django.db.models import Q, Max, Min, Sum, Count, OuterRef, Subquery, F, Value
from .models import NutritentReferenceUnit, Food, DietaryFibre, WaterSolubleVitamins, FatSolubleVitamins, Carotenoids, MineralsAndTraceElements, StarchAndSugars, FattyAcid, AminoAcid, OrganicAcid, Polyphenols, Oligosaccharides, PhytosterolsPhytateSaponin

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
