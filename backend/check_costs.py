#!/usr/bin/env python3
import json

with open('../excel_mock_converted.json', 'r') as f:
    data = json.load(f)

print(f'Custos no Excel: {len(data["costs"])}')

# Verificar IDs únicos
cost_ids = [c['id'] for c in data['costs']]
unique_ids = set(cost_ids)
print(f'IDs únicos: {len(unique_ids)}')

if len(cost_ids) != len(unique_ids):
    print('⚠️ Há IDs duplicados!')
    from collections import Counter
    duplicates = [id for id, count in Counter(cost_ids).items() if count > 1]
    print(f'IDs duplicados: {duplicates}')
else:
    print('✅ Todos os IDs são únicos')

# Verificar range de IDs
max_id = max(int(id.replace('c', '')) for id in cost_ids if id.startswith('c'))
print(f'ID máximo: c{max_id}')

# Verificar o que foi escrito no main.py
print('\n🔍 Verificando main.py...')
with open('app/main.py', 'r') as f:
    content = f.read()

actual_cost_count = content.count('"id": "c')
print(f'Custos encontrados no main.py: {actual_cost_count}')

# Contar custos dentro da seção costs
import re
costs_section = re.search(r'"costs": \[(.*?)\]', content, re.DOTALL)
if costs_section:
    costs_content = costs_section.group(1)
    costs_in_section = costs_content.count('"id": "c')
    print(f'Custos na seção costs: {costs_in_section}')