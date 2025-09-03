from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Nutrient:
    category: str = field(default="macros")  # 'macro' or 'micro'
    name: str = field(default="")
    amount: float = field(default=0.0)
    unit: str = field(default="")
    rda_percentage: float = field(default=0.0)

    def to_dict(self):
        return {
            "name": self.name,
            "amount": self.amount,
            "unit": self.unit,
            "rda_percentage": self.rda_percentage,
            "category": self.category,
        }
    @staticmethod
    def from_dict(data):
        return Nutrient(
            category=data.get("category", "macros"),
            name=data.get("name", ""),
            amount=data.get("amount", 0.0),
            unit=data.get("unit", ""),
            rda_percentage=data.get("rda_percentage", 0.0),
        )
    
@dataclass
class NutritionReport:
    nutrients: List[Nutrient] = field(default_factory=list)

    @classmethod
    def from_list(cls, nutrient_data: List[Dict[str, Any]]) -> "NutritionReport":
        nutrients = []
        for item in nutrient_data:
            nutrients.append(
                Nutrient(
                    category=item.get("category", "macros"),
                    name=item.get("name", ""),
                    amount=item.get("amount", 0.0),
                    unit=item.get("unit", ""),
                    rda_percentage=item.get("rda_percentage", 0.0),
                )
            )
        return cls(nutrients=nutrients)
    
    def add_nutrient(self, nutrient: Nutrient):
        self.nutrients.append(nutrient)

    def to_dict(self):
        return [n.to_dict() for n in self.nutrients]

    def macro_labels(self):
        return [n.name for n in self.nutrients if n.category == "macros"]
    
    def vitamins_labels(self):
        return [n.name for n in self.nutrients if n.category == "vitamins"]
    
    def minerals_labels(self):
        return [n.name for n in self.nutrients if n.category == "minerals"]

    def macro_coverages(self):
        return [n.rda_percentage for n in self.nutrients if n.category == "macros"]
    
    def vitamins_coverages(self):
        return [n.rda_percentage for n in self.nutrients if n.category == "vitamins"]
    
    def minerals_coverages(self):
        return [n.rda_percentage for n in self.nutrients if n.category == "minerals"]
    
    def macros(self) -> List[Nutrient]:
        return [n for n in self.nutrients if n.category == "macros"]

    def vitamins(self) -> List[Nutrient]:
        return [n for n in self.nutrients if n.category == "vitamins"]
    
    def minerals(self) -> List[Nutrient]:
        return [n for n in self.nutrients if n.category == "minerals"]

    def macros_dict(self) -> List[Dict[str, Any]]:
        return [n.to_dict() for n in self.macros()]

    def vitamins_dict(self) -> List[Dict[str, Any]]:
        return [n.to_dict() for n in self.vitamins()]
    
    def minerals_dict(self) -> List[Dict[str, Any]]:
        return [n.to_dict() for n in self.minerals()]

    