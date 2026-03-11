class UnclearTerm:
    def __init__(self, name, a, b, c):
        self.name = name
        self.a = a
        self.b = b
        self.c = c
    
    def belong(self, x):
        if x == self.b:
            return 1.0
        if x <= self.a or x >= self.c:
            return 0.0
        elif self.a < x < self.b:
            return (x - self.a) / (self.b - self.a)
        elif self.b < x < self.c:
            return (self.c - x) / (self.c - self.b)
    
        return 0.0

class UnclearVariable:
    def __init__(self, name, terms):
        self.name = name
        self.terms = terms
    
    def get_belong(self, value, term_name):
        return self.terms[term_name].belong(value)

class ExpertSystem:
    
    def __init__(self, gender):
        self.gender = gender
        self.rules = self._create_rules()
        self.variables = self._create_variables(gender)
    
    def _create_variables(self, gender):        
        if gender == 'женщина':
            fat_ranges = {
                'low':     (7, 10, 25),
                'healthy': (20, 28, 38),
                'high':    (35, 60, 63)
            }
            muscle_ranges = {
                'low':     (22, 25, 36),
                'healthy': (33, 38, 43),
                'perfect': (40, 45, 48)
            }
            water_ranges = {
                'low':     (32, 35, 50),
                'healthy': (47, 55, 63),
                'perfect': (60, 65, 68)
            }
        else:
            fat_ranges = {
                'low':     (0, 2, 15),
                'healthy': (12, 18, 25),
                'high':    (22, 50, 53)
            }
            muscle_ranges = {
                'low':     (27, 30, 40),
                'healthy': (37, 43, 50),
                'perfect': (47, 55, 58)
            }
            water_ranges = {
                'low':     (42, 45, 57),
                'healthy': (54, 60, 68),
                'perfect': (65, 75, 78)     
            }
        
        fat_terms = {name: UnclearTerm(name, *ranges) for name, ranges in fat_ranges.items()}
        muscle_terms = {name: UnclearTerm(name, *ranges) for name, ranges in muscle_ranges.items()}
        water_terms = {name: UnclearTerm(name, *ranges) for name, ranges in water_ranges.items()}
        balance_terms = {
            'low': UnclearTerm('low', 0, 0, 50),
            'healthy': UnclearTerm('healthy', 25, 65, 100),
            'perfect': UnclearTerm('perfect', 50, 100, 100)
        }
        return {
            'fat': UnclearVariable('Жир в организме', fat_terms),
            'muscle': UnclearVariable('Скелетная мышечная масса', muscle_terms),
            'water': UnclearVariable('Вода', water_terms),
            'balance': UnclearVariable('Сбалансированность', balance_terms)
        }
    
    def _create_rules(self):
        rules = [
            {'if': {'fat': 'healthy', 'muscle': 'healthy', 'water': 'healthy'}, 'then': 'perfect'},
            {'if': {'fat': 'healthy', 'muscle': 'perfect', 'water': 'perfect'}, 'then': 'perfect'},
            {'if': {'fat': 'low', 'muscle': 'perfect', 'water': 'perfect'}, 'then': 'perfect'},
            
            {'if': {'fat': 'high', 'muscle': 'healthy', 'water': 'healthy'}, 'then': 'healthy'},
            {'if': {'fat': 'healthy', 'muscle': 'low', 'water': 'healthy'}, 'then': 'healthy'},
            {'if': {'fat': 'healthy', 'muscle': 'healthy', 'water': 'low'}, 'then': 'healthy'},
            {'if': {'fat': 'low', 'muscle': 'low', 'water': 'low'}, 'then': 'healthy'},
            
            {'if': {'fat': 'high', 'muscle': 'low'}, 'then': 'low'},
            {'if': {'fat': 'high', 'water': 'low'}, 'then': 'low'},
            {'if': {'muscle': 'low', 'water': 'low'}, 'then': 'low'},
            {'if': {'fat': 'high', 'muscle': 'low', 'water': 'low'}, 'then': 'low'},
        ]
        return rules
    
    def _fuzzify(self, fat_val, muscle_val, water_val):
        memberships = {
            'fat': {
                term: self.variables['fat'].get_belong(fat_val, term)
                for term in self.variables['fat'].terms
            },
            'muscle': {
                term: self.variables['muscle'].get_belong(muscle_val, term)
                for term in self.variables['muscle'].terms
            },
            'water': {
                term: self.variables['water'].get_belong(water_val, term)
                for term in self.variables['water'].terms
            }
        }
        return memberships
    
    def _evaluate_rules(self, memberships):

        output_activation = {'low': 0.0, 'healthy': 0.0, 'perfect': 0.0}
        
        for rule in self.rules:

            condition_values = []
            for var_name, term_name in rule['if'].items():
                condition_values.append(memberships[var_name][term_name])
            
            rule_strength = min(condition_values) if condition_values else 0.0
            
            if rule_strength > 0:
                output_term = rule['then']
                output_activation[output_term] = max(
                    output_activation[output_term],
                    rule_strength
                )
        
        return output_activation
    
    def _defuzzify(self, output_activation):

        centers = {'low': 25, 'healthy': 65, 'perfect': 95}
        
        numerator = sum(activation * centers[term] 
                       for term, activation in output_activation.items())
        denominator = sum(output_activation.values())
        
        if denominator == 0:
            return 50.0
        
        return numerator / denominator
    
    def calculate(self, fat, muscle, water):

        memberships = self._fuzzify(fat, muscle, water)

        output_activation = self._evaluate_rules(memberships)

        balance_score = self._defuzzify(output_activation)
        
        if balance_score >= 85:
            category = "совершенная"
        elif balance_score >= 50:
            category = "здоровая"
        else:
            category = "низкая"
        
        return {
            'score': balance_score,
            'category': category,
            'activations': output_activation,
            'memberships': memberships
        }

def get_float_input(prompt, min_val, max_val):
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Значение должно быть в диапазоне {min_val}...{max_val}")
        except ValueError:
            print("Введите корректное число")

def main():
    print("=" * 70)
    print("ЭКСПЕРТНАЯ СИСТЕМА 'ОЦЕНКА БАЛАНСА СОСТАВА ТЕЛА ЧЕЛОВЕКА'")
    print("=" * 70)
    
    while True:
        gender = input("\nВведите пол (мужчина/женщина): ").strip().lower()
        if gender in ['мужчина', 'женщина']:
            break
        print("Введите 'мужчина' или 'женщина'")
    
    system = ExpertSystem(gender)
    
    if gender == 'женщина':
        fat_range = (10, 60)
        muscle_range = (25, 45)
        water_range = (35, 65)
    else:
        fat_range = (2, 50)
        muscle_range = (30, 55)
        water_range = (45, 75)
    
    print(f"\nСистема настроена для: {gender.upper()}")
    print("-" * 70)
    
    print("\nВведите показатели состава тела:")
    fat = get_float_input(f"  Жир в организме (%) [{fat_range[0]}...{fat_range[1]}]: ",  *fat_range)
    muscle = get_float_input(f"  Скелетная мышечная масса (%) [{muscle_range[0]}...{muscle_range[1]}]: ", *muscle_range)
    water = get_float_input(f"  Вода в организме (%) [{water_range[0]}...{water_range[1]}]: ", *water_range)
    
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ РАСЧЁТА")
    print("=" * 70)
    
    result = system.calculate(fat, muscle, water)
    
    print(f"\nСбалансированность состава тела:")
    print(f"   Оценка: {result['score']:.1f} из 100")
    print(f"   Категория: {result['category'].upper()}")
    
    print(f"\nАктивация выходных термов:")
    for term, activation in result['activations'].items():
        term_rus = {'low': 'низкая', 'healthy': 'здоровая', 'perfect': 'совершенная'}[term]
        bar = '█' * int(activation * 20)
        print(f"   {term_rus:12} [{activation:.3f}] {bar}")
    
    print(f"\nСтепени принадлежности входов:")
    
    fat_terms = {'low': 'низкий', 'healthy': 'здоровый', 'high': 'высокий'}
    for term, membership in result['memberships']['fat'].items():
        if membership > 0.01:
            print(f"   Жир ({fat_terms[term]:8}): {membership:.3f}")
    
    muscle_terms = {'low': 'низкое', 'healthy': 'здоровое', 'perfect': 'совершенное'}
    for term, membership in result['memberships']['muscle'].items():
        if membership > 0.01:
            print(f"   Мышцы ({muscle_terms[term]:10}): {membership:.3f}")
    
    water_terms = {'low': 'низкая', 'healthy': 'здоровая', 'perfect': 'совершенная'}
    for term, membership in result['memberships']['water'].items():
        if membership > 0.01:
            print(f"   Вода ({water_terms[term]:10}): {membership:.3f}")
    
    print("\n" + "=" * 70)
    print("Расчёт завершён!")
    print("=" * 70)

if __name__ == "__main__":
    main()