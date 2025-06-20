# 📋 Relatório de Conformidade IVA - Junho 2025

## 🎯 Estado de Conformidade: 70/100

### ✅ IMPLEMENTADO CORRETAMENTE

1. **Fórmula Base IVA sobre Margem**
   - ✅ `IVA = Margem × Taxa / 100` (CIVA Art. 308º)
   - ✅ Calcula sobre margem, não sobre vendas totais
   - ✅ Localização: `calculator.py`, linhas 166-173

2. **Tratamento Margem Negativa**
   - ✅ Quando margem < 0, IVA = 0
   - ✅ Sistema deteta e avisa corretamente

3. **Suporte Documentos Portugueses**
   - ✅ FT (Fatura), FR (Fatura-Recibo), NC (Nota Crédito)
   - ✅ Parser SAF-T completo com namespaces PT
   - ✅ e-Fatura CSV funcionando

4. **Validações Básicas**
   - ✅ Valida requisitos regime margem
   - ✅ Avisa se IVA destacado (proibido no regime)
   - ✅ Margens realistas para turismo

### ❌ FALTA IMPLEMENTAR (Crítico para Conformidade)

1. **Compensação Períodos (CRÍTICO!)**
   ```python
   # ATUAL: Calcula por transação
   Venda 1: Margem -€1000 → IVA = €0
   Venda 2: Margem +€2000 → IVA = €460
   Total IVA = €460 ❌ ERRADO
   
   # CORRETO: Calcula por período
   Trimestre: -€1000 + €2000 = €1000
   IVA = €1000 × 23% = €230 ✅ CORRETO
   ```

2. **Taxas Regionais IVA**
   - Falta suporte para Madeira (22%) e Açores (18%)
   - Sistema assume sempre 23%

3. **Notas de Crédito**
   - Não revertem margens originais
   - Tratadas como vendas normais

4. **Anexo O e Declarações**
   - Não gera formato oficial AT
   - Falta exportação declaração periódica

### 🔧 SOLUÇÃO IMPLEMENTADA

Criei novo módulo `period_calculator.py` com:
- ✅ Cálculo por período com compensação
- ✅ Suporte taxas regionais
- ✅ Carry-forward margens negativas
- ✅ Preparação dados Anexo O

### 📊 EXEMPLO PRÁTICO

**Seu Caso Atual:**
```
Q4/2024: Custos €45.225 > Vendas €0 = Margem -€45.225
Q1/2025: Vendas €34.951 > Custos €0 = Margem +€34.951

SEM compensação: IVA = €34.951 × 23% = €8.039 ❌
COM compensação: Margem líquida = -€10.274
                  IVA = €0 ✅ (margem ainda negativa)
```

### 🚨 AÇÕES NECESSÁRIAS

1. **Integrar `period_calculator.py` no sistema**
2. **Modificar interface para cálculo trimestral**
3. **Adicionar gestão de períodos fiscais**
4. **Implementar exportação Anexo O**

### 📅 Conformidade Temporal

- **Lei em vigor**: Sim, CIVA Art. 308º sem alterações
- **Ofícios AT**: Último relevante 30.195/2019
- **Taxas IVA 2025**: Mantêm-se (23%/22%/18%)

### ⚖️ Risco de Não Conformidade

**ALTO** - Sistema atual pode resultar em:
- Pagamento excessivo de IVA
- Não conformidade com obrigações declarativas
- Potenciais coimas por declarações incorretas

### ✅ Recomendação

**Implementar urgentemente cálculo por período** para estar em conformidade total com a legislação portuguesa.