class NutritionCalculator:
    def __init__(self, data):
        self.data = data

    def calculate_nutrition(self):
        total_students = self.data['i_v_students']+self.data['vi_x_students']
        total_recommended = self.data['recommended_i_v']+self.data['recommended_vi_x']
        pc_nutrition_i_v = (self.data['total_nutrition_value']/total_recommended)*self.data['recommended_i_v']
        pc_nutrition_vi_x = (self.data['total_nutrition_value']/total_recommended)*self.data['recommended_vi_x']
        pc_wt_avg_i_v = pc_nutrition_i_v/self.data['i_v_students']
        pc_wt_avg_vi_x = pc_nutrition_vi_x/self.data['vi_x_students']

        return {
            'total_students':total_students, 
            'total_recommended':total_recommended,
            'per capita I-V':pc_nutrition_i_v,
            'per capita VI-X':pc_nutrition_vi_x,
            'Wt. Avg. I-V':pc_wt_avg_i_v,
            'Wt. Avg. VI-X':pc_wt_avg_vi_x
            }

if __name__ == "__main__":
    # Sample usage when running directly
    sample_data = {
        'i_v_students':208,
        'vi_x_students':261,
        'total_nutrition_value':11793,
        'recommended_i_v':83,
        'recommended_vi_x':123,
    }

    calc = NutritionCalculator(sample_data)
    print(calc.calculate_nutrition())  # 👉 prints (2025-09-02, 2025-09-10)
