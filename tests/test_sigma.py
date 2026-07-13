from app.services.sigma_service import get_sigma_rules

rules = get_sigma_rules("T1059")

for rule in rules:
    print(rule)