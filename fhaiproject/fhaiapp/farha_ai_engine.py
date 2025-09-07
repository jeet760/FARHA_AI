from django.http import JsonResponse
from .models import (
    FoodCategoryMap, Food, DietaryFibre, WaterSolubleVitamins, 
    FatSolubleVitamins, Carotenoids, MineralsAndTraceElements, 
    StarchAndSugars, FattyAcid, AminoAcid, OrganicAcid, 
    Polyphenols, Oligosaccharides, PhytosterolsPhytateSaponin
)
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from fuzzywuzzy import process

class FarhaAIEngine:
    NUTRIENTS_FIBRE = [
        'water','protcnt','ash','fatce','fibtg','fibins','fibsol',
        'choavldf','enerc'
    ]
    DIETARY_FIBRE_FIELD_LABELS = {
        "protcnt": "Protein",
        "fatce": "Fat",
        "fibtg": "Fiber",
        "choavldf": "Carbohydrates",
        "enerc": "Energy (kj)",
        "water": "Water",
        "ash": "Ash",
        "fibins": "Ins. Fiber",
        "fibsol": "Sol. Fiber",
    }
    # NUTRIENTS_VITAMIN = [
    #     'vitc','thia','ribf','niac','vitb6','folate_tot','folate_dfe',
    #     'folate_food','folate_supp','vitb12','vita_iu','vita_rae','vitk1'
    # ]
    # NUTRIENTS_MINERAL = ['ca','fe','mg','p','k','na','zn','cu','mn','se']
    # NUTRIENTS_STARCH_SUGAR = [
    #     'starch','sugar_tot','sugar_tot_nocal','glucose','fructose',
    #     'galactose','sucrose','lactose','maltose'
    # ]
    # NUTRIENTS_FATTY_ACID = [
    #     'fatty_acid_tot','fatty_acid_sat','fatty_acid_mono',
    #     'fatty_acid_poly','cholestrl','16_0','18_0','18_1','18_2','18_3'
    # ]
    # NUTRIENTS_AMINO_ACID = [
    #     'trptophan','threonine','isoleucine','leucine','lysine',
    #     'methionine','cystine','phenylalanine','tyrosine','valine',
    #     'arginine','histidine','alanine','aspartic_acid',
    #     'glutamic_acid','glycine','proline','serine'
    # ]
    # NUTRIENTS_ORGANIC_ACID = ['citric_acid','malic_acid','tartaric_acid','oxalic_acid']
    # NUTRIENTS_POLYPHENOLS = ['total_polyphenols','flavonoids','phenolic_acids','stilbenes','lignans']
    # NUTRIENTS_OLIGOSACCHARIDES = ['raffinose','stachyose','verbascose']
    # NUTRIENTS_PHYTOSTEROLS = ['campesterol','stigmasterol','beta_sitosterol','total_phytosterols']

    def __init__(self):
        # Load spaCy model once
        self.NUTRIENT_FIELD_MAP = {
            "protein": "protcnt",
            "fat": "fatce",
            "fiber": "fibtg",
            "carbohydrates": "choavldf",
            "carbohydrate": "choavldf",
            "energy": "enerc",
            "vitamin c": "vitc",
            "iron": "fe",
            "calcium": "ca",
            "zinc": "zn",
        }

        self.NUTRIENT_MODEL_MAP = {
            # Energy and Proximate
            "water": "food_dietary_fibre",
            "protcnt": "food_dietary_fibre",   # protein
            "ash": "food_dietary_fibre",
            "fatce": "food_dietary_fibre",     # fat
            "fibtg": "food_dietary_fibre",    # total dietary fibre
            "fibins": "food_dietary_fibre",    # insoluble dietary fibre
            "fibsol": "food_dietary_fibre",    # soluble dietary fibre
            "choavldf": "food_dietary_fibre",  # available carbohydrate
            "enerc": "food_dietary_fibre",

            # Vitamins – Water Soluble
            "thiamin": "water_soluble_vitamins",
            "riboflavin": "water_soluble_vitamins",
            "niacin": "water_soluble_vitamins",
            "pantothenicacid": "water_soluble_vitamins",
            "vitb6": "water_soluble_vitamins",
            "folate": "water_soluble_vitamins",
            "vitb12": "water_soluble_vitamins",
            "vitc": "water_soluble_vitamins",

            # Vitamins – Fat Soluble
            "vita_rae": "fat_soluble_vitamins",
            "retinol": "fat_soluble_vitamins",
            "alphacarotene": "fat_soluble_vitamins",
            "betacarotene": "fat_soluble_vitamins",
            "betacryptoxanthin": "fat_soluble_vitamins",
            "lycopene": "fat_soluble_vitamins",
            "lutein_zeaxanthin": "fat_soluble_vitamins",
            "vite": "fat_soluble_vitamins",
            "vitd": "fat_soluble_vitamins",
            "vitk": "fat_soluble_vitamins",

            # Minerals and Trace Elements
            "ca": "mineralsandtraceelements",   # Calcium
            "fe": "mineralsandtraceelements",   # Iron
            "mg": "mineralsandtraceelements",   # Magnesium
            "p": "mineralsandtraceelements",    # Phosphorus
            "k": "mineralsandtraceelements",    # Potassium
            "na": "mineralsandtraceelements",   # Sodium
            "zn": "mineralsandtraceelements",   # Zinc
            "cu": "mineralsandtraceelements",   # Copper
            "mn": "mineralsandtraceelements",   # Manganese
            "se": "mineralsandtraceelements",   # Selenium

            # Lipids
            "fasat": "lipids",                  # Saturated fat
            "fams": "lipids",                   # Monounsaturated fat
            "fapu": "lipids",                   # Polyunsaturated fat
            "cholestrol": "lipids",             # Cholesterol
        }


        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        #identify the numbers
        self.num_matcher = Matcher(self.nlp.vocab)
        num_patterns = [{"LIKE_NUM": True}]
        self.num_matcher.add("NUMBER", [num_patterns])

        # Use synonyms (user-friendly) for matching
        patterns = [self.nlp.make_doc(n) for n in self.NUTRIENT_FIELD_MAP.keys()]
        self.matcher.add("NUTRIENT", patterns)

    def extract_food_nutrient(self, query, food_list):
        doc = self.nlp(query)

        # --- Find model_nutrients ---
        matches = self.matcher(doc)
        model_nutrients = []
        for match_id, start, end in matches:
            text = doc[start:end].text.lower()
            if text in self.NUTRIENT_FIELD_MAP:
                model_nutrients.append([self.NUTRIENT_FIELD_MAP[text], text])

        # -- quantity number --
        # num_matches = self.num_matcher(doc)
        # for match_id, start, end in num_matches:
        #     print("Number found:", doc[start:end].text)

        # -- unit in quantity -- 
        user_qty = 0
        user_unit = None
        for i, token in enumerate(doc):
            if token.like_num and i+1 < len(doc):   # number found
                unit = doc[i+1].text.lower()
                print("Number:", token.text, "Unit:", unit)
                user_qty = float(token.text)
                user_unit = unit
        
        if user_qty == 0:
            user_qty = 100
            user_unit = 'grams'

        # --- Find ALL food matches ---
        candidates = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]
        results = []
        for c in candidates:
            best = process.extract(c, food_list, limit=5)
            results.extend(best)
        # results = process.extract(query, food_list, limit=5)
        foods = [food for food, score in results if score >= 80]

        return foods, model_nutrients, user_qty, user_unit

    def nutrition_query(self, q):
        user_query = q.lower()
        if user_query in ["", "hi", "hello", "hey"]:
            return JsonResponse({"success": False, "user_query":q, "respnose_text":'Hey There! I am FarHa, a rule based AI.', "foods": None})   
        # -- check whether the intent of user's query is specific or list --
        nutrients_mentioned = any(word in user_query.lower() for word in ["protein","fat","vitamin","fiber","calories"])
        if nutrients_mentioned:
            intent = "specific"
        else:
            intent = "list"
        
        compare_mentioned = any(word in user_query.lower() for word in ["compare","comparison","vs","versus"])
        if compare_mentioned:
            compare_table = self.intent_comparison_query(user_query, q)
            return JsonResponse({"success": True, "user_query":q, "respnose_text":compare_table, "foods": None})
        
        combine_mentioned = any(word in user_query.lower() for word in ["total", "sum", "combined", "combine"])
        if combine_mentioned:
            combine_table = self.intent_combine_query(user_query,q)
            return JsonResponse({"success": True, "user_query":q, "respnose_text":combine_table, "foods": None})

        if intent == 'specific':
            respnose_text,results = self.intent_specific_query(user_query, q)
            respnose_text+='.'
        else:
            respnose_text,results = self.intent_list_query(user_query, q)

        return JsonResponse({"success": True, "user_query":q, "respnose_text":respnose_text, "foods": results})


    def intent_specific_query(self, user_query, q):
        # Fetch all food names from DB
        food_items = [i.food_name for i in Food.objects.all()]

        # --- Step 1: Extract foods + model_nutrients ---
        foods, model_nutrients, user_qty, user_unit = self.extract_food_nutrient(user_query, food_items)

        if not foods:
            return JsonResponse({"success": False, "user_query":q, "respnose_text":None, "message": "Food item not found"})

        if not model_nutrients:
            return JsonResponse({"success": False, "user_query":q, "respnose_text":None, "message": "No nutrient found"})

        results = []
        for food in foods:
            item = Food.objects.filter(food_name__icontains=food).first()
            if not item:
                continue
            respnose_text = f'As per NIN (National Institute of Nutrition) database, {user_qty} {user_unit} of {item.food_name} contains '
            food_data = {"food": item.food_name, "model_nutrients": {}}

            for n in model_nutrients:
                model_name = self.NUTRIENT_MODEL_MAP.get(n[0])
                obj = getattr(item, model_name, None)
                #print(obj)
                if obj and hasattr(obj, n[0]):
                    food_data["model_nutrients"][n[0]] = getattr(obj, n[0])
                    print(food_data["model_nutrients"][n[0]])
                    scaled_value = self.scale_food_nutrient(user_qty, user_unit, food_data["model_nutrients"][n[0]])
                    print(scaled_value)
                    respnose_text += f" {scaled_value} grams of {n[1]}"
                else:
                    food_data["model_nutrients"][n] = None

            results.append(food_data)
        return respnose_text, results
    
    def intent_list_query(self, user_query, q):
        food_items = [i.food_name for i in Food.objects.all()]
        foods, model_nutrients, user_qty, user_unit = self.extract_food_nutrient(user_query, food_items)
        results = []
        # for food in foods:
        item = Food.objects.filter(food_name__icontains=foods[0]).first()
        # if not item:
        #     continue
        food_data = item.food_dietary_fibre
        scaled_value_protein = self.scale_food_nutrient(user_qty, user_unit, food_data.protcnt)
        scaled_value_carb = self.scale_food_nutrient(user_qty, user_unit, food_data.choavldf)
        scaled_value_energy = self.scale_food_nutrient(user_qty, user_unit, food_data.enerc)
        scaled_value_fat = self.scale_food_nutrient(user_qty, user_unit, food_data.fatce)
        scaled_value_fibre = self.scale_food_nutrient(user_qty, user_unit, food_data.fibtg)
        scaled_value_fibins = self.scale_food_nutrient(user_qty, user_unit, food_data.fibins)
        scaled_value_fibsol = self.scale_food_nutrient(user_qty, user_unit, food_data.fibsol)
        scaled_value_ash = self.scale_food_nutrient(user_qty, user_unit, food_data.ash)
        scaled_value_water = self.scale_food_nutrient(user_qty, user_unit, food_data.water)

        results.append(f'{scaled_value_protein} grams of protein, ')
        results.append(f'{scaled_value_carb} grams of carbohdrate, ')
        results.append(f'{round(scaled_value_energy/4.18, 2)} kcal of energy, ')
        results.append(f'{scaled_value_fat} grams of fats, ')
        results.append(f'{scaled_value_fibre} grams of fibre, ')
        results.append(f'{scaled_value_fibins} grams of insoluble fibre, ')
        results.append(f'{scaled_value_fibsol} grams of soluble fibre, ')
        results.append(f'{scaled_value_ash} grams of ash, ')
        results.append(f'{scaled_value_water} grams of water.')

        # if "compare" in user_query.lower() and len(foods) > 1:
        #     return self.nutrition_comparison(foods, results, user_qty, user_unit)

        respnose_text = f'As per NIN (National Institute of Nutrition) database, {user_qty} {user_unit} of {item.food_name} contains '
        for result in results:
            respnose_text+= result
        return respnose_text, results
    
    def scale_food_nutrient(self, quantity, unit, nutrient_value):
        # Convert the quantity to grams based on the unit
        standard_value = 100  # Standard value for scaling (100 grams)
        nutrient_value_per_100g = nutrient_value  # Nutrient value per 100 grams
        unit = unit.lower()
        if unit in ['g', 'gram', 'grams']:
            quantity_in_grams = quantity
            scaled_nutrient = round((nutrient_value_per_100g / standard_value) * quantity_in_grams, 2)
        elif unit in ['kg', 'kilogram', 'kilograms']:
            quantity_in_grams = quantity * 1000
            scaled_nutrient = round((nutrient_value_per_100g / standard_value) * quantity_in_grams, 2)
        elif unit in ['mg', 'milligram', 'milligrams']:
            quantity_in_grams = quantity / 1000
        elif unit in ['lb', 'pound', 'pounds']:
            quantity_in_grams = quantity * 453.592
        elif unit in ['oz', 'ounce', 'ounces']:
            quantity_in_grams = quantity * 28.3495
        else:
            return None, "Unsupported unit. Please use g, kg, mg, lb, or oz."

        return scaled_nutrient
    
    def intent_comparison_query(self, user_query, q):
        food_items = [i.food_name for i in Food.objects.all()]
        foods, model_nutrients, user_qty, user_unit = self.extract_food_nutrient(user_query, food_items)
        results = []
        col_widths = self.NUTRIENTS_FIBRE.__len__()
        for food in foods:
            item = Food.objects.filter(food_name__icontains=food).first()
            if not item:
                continue
            food_data = item.food_dietary_fibre
            results.append(food_data)


        rows = []
        headers = self.NUTRIENTS_FIBRE
        rows.append(['Food'] + headers)
        # rows.append(headers)

        for food, data in zip(foods, results):
            row = [food]
            for nutrient in headers:
                value = getattr(data, nutrient, 'N/A')
                row.append(value)
            rows.append(row)

        # Format as a simple text table
        table = '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; margin-top:10px;">'
        # header row (center aligned)
        table += "<tr>"
        for header in rows[0]:
            table += f"<th style='background-color:#f2f2f2; text-align:center;'>{self.DIETARY_FIBRE_FIELD_LABELS.get(header, header.capitalize())}</th>"
        table += "</tr>\n"

        # data rows (right aligned)
        for row in rows[1:]:
            table += "<tr>"
            for i, item in enumerate(row):
                if i == 0:  # First column (Food names) -> left align
                    table += f"<td style='text-align:left;'>{item}</td>"
                else:       # Nutrient values -> right align
                    table += f"<td style='text-align:right;'>{item}</td>"
            table += "</tr>\n"

        table += "</table>"
        return table

    def intent_combine_query(self, user_query, q):
        food_items = [i.food_name for i in Food.objects.all()]
        foods, model_nutrients, user_qty, user_unit = self.extract_food_nutrient(user_query, food_items)
        results = []
        col_widths = self.NUTRIENTS_FIBRE.__len__()
        for food in foods:
            item = Food.objects.filter(food_name__icontains=food).first()
            if not item:
                continue
            food_data = item.food_dietary_fibre
            results.append(food_data)
        rows = []
        total_row = []
        headers = self.NUTRIENTS_FIBRE
        rows.append(['Food'] + headers)
        # rows.append(headers)

        totals = {nutrient: 0 for nutrient in headers}  # dictionary for totals

        for food, data in zip(foods, results):
            row = [food]
            for nutrient in headers:
                value = getattr(data, nutrient, 'N/A')
                row.append(value)
                totals[nutrient] += value
            rows.append(row)

        total_row = ["Total"] + [round(totals[n], 2) for n in headers]
        rows.append(total_row)

        # ---- HTML rendering ----
        table = '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; margin-top:10px;">'

        # header row
        table += "<tr>"
        for header in rows[0]:
            table += f"<th style='background-color:#f2f2f2; text-align:center;'>{self.DIETARY_FIBRE_FIELD_LABELS.get(header, header.capitalize())}</th>"
        table += "</tr>\n"

        # data rows
        for row in rows[1:]:
            if row[0] == "Total":  # highlight last row
                table += "<tr style='font-weight:bold; background-color:#ffe4b2;'>"
            else:
                table += "<tr>"
            for i, item in enumerate(row):
                if i == 0:  # first column (Food names) -> left aligned
                    table += f"<td style='text-align:left;'>{item}</td>"
                else:  # numeric values -> right aligned
                    table += f"<td style='text-align:right;'>{item}</td>"
            table += "</tr>\n"

        table += "</table>"
        return table