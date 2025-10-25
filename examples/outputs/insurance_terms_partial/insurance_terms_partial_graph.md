# Knowledge Graph Report

## Graph Statistics

- **Total Nodes**: 19
- **Total Edges**: 41
- **Average Degree**: 4.32

---

## Nodes (with properties)

### Node: InsuranceTerms (`InsuranceTerms_696b031073e7`)
- **Label**: InsuranceTerms
- **Document Reference**: UNKNOWN
- **Product Name**: Assurance Habitation
- **Issuer**: AXA France IARD
- **Effective Date**: None
- **Document Type**: Comparatif des formules
- **Contract Duration**: None
- **Territorial Scope**: ['France métropolitaine']
- **Common Exclusions**: ["Faute intentionnelle ou dolosive de l'assuré", 'Guerre civile ou étrangère', 'Dommages nucléaires', 'Usure normale', "Défaut d'entretien", 'Vice de construction', "Dommages résultant d'une activité professionnelle"]
- **Claims Procedure**: Déclaration sous 5 jours ouvrés, 2 jours en cas de vol
- **Prescription Period**: 2 ans à compter de l'événement
- **Cancellation Terms**: Résiliation annuelle avec préavis de 2 mois

### Node: InsurancePlan (`InsurancePlan_83b2b97326ea`)
- **Label**: InsurancePlan
- **Name**: Formule Essentielle
- **Description**: Formule de base avec garanties essentielles
- **Base Price**: None
- **Available Options**: ['Dommages électriques', 'Rééquipement à neuf', "Dépannage d'urgence", 'Jardin', 'Piscine', 'Assurance scolaire']

### Node: Guarantee (`Guarantee_56f71907a592`)
- **Label**: Guarantee
- **Name**: Dégâts des eaux
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_bdf21c00318d`)
- **Label**: Guarantee
- **Name**: Incendie et événements assimilés
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_845e59d360a1`)
- **Label**: Guarantee
- **Name**: Événements climatiques
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_ed3b24823928`)
- **Label**: Guarantee
- **Name**: Attentat
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_b2161845103e`)
- **Label**: Guarantee
- **Name**: Catastrophes naturelles et technologiques
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_7546c32638b6`)
- **Label**: Guarantee
- **Name**: Responsabilité civile
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_1741ec6ed69c`)
- **Label**: Guarantee
- **Name**: Assistance
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: InsurancePlan (`InsurancePlan_3bc6b85bacd5`)
- **Label**: InsurancePlan
- **Name**: Formule Confort
- **Description**: Couverture étendue pour propriétaires occupants
- **Base Price**: None
- **Available Options**: ['Dommages électriques', 'Rééquipement à neuf', "Dépannage d'urgence", 'Jardin', 'Piscine', 'Assurance scolaire']

### Node: Guarantee (`Guarantee_9dd028187542`)
- **Label**: Guarantee
- **Name**: Bris de vitre
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_dd96508880e4`)
- **Label**: Guarantee
- **Name**: Vol et vandalisme
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: InsurancePlan (`InsurancePlan_10bf85b8f6a2`)
- **Label**: InsurancePlan
- **Name**: Formule Confort Plus
- **Description**: Protection maximale incluant objets de valeur
- **Base Price**: None
- **Available Options**: ['Dommages électriques', 'Rééquipement à neuf', "Dépannage d'urgence", 'Jardin', 'Piscine', 'Assurance scolaire']

### Node: Guarantee (`Guarantee_0cee91f19218`)
- **Label**: Guarantee
- **Name**: Vol et casse des objets de loisir
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: InsurancePlan (`InsurancePlan_691398387dc8`)
- **Label**: InsurancePlan
- **Name**: Formule Propriétaire Non Occupant
- **Description**: None
- **Base Price**: None
- **Available Options**: None

### Node: Guarantee (`Guarantee_e23a82cdf5eb`)
- **Label**: Guarantee
- **Name**: Défense Pénale et Recours
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_f0f33e3260eb`)
- **Label**: Guarantee
- **Name**: Vol et Vandalisme
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_ba29e27739df`)
- **Label**: Guarantee
- **Name**: Dommages électriques
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

### Node: Guarantee (`Guarantee_23baaeb8f69a`)
- **Label**: Guarantee
- **Name**: Protection du mobilier
- **Description**: None
- **Coverage Conditions**: None
- **Coverage Limit**: None
- **Deductible**: None
- **Exclusions**: None

## Edges (with labels)

- **InsuranceTerms → InsurancePlan** `available_plans`
- **InsuranceTerms → InsurancePlan** `available_plans`
- **InsuranceTerms → InsurancePlan** `available_plans`
- **InsuranceTerms → InsurancePlan** `available_plans`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`
- **InsurancePlan → Guarantee** `guarantees`

---

_End of Graph Summary_
