# Knowledge Graph Report

## Graph Statistics

- **Total Nodes**: 7
- **Total Edges**: 6
- **Average Degree**: 1.71

---

## Nodes (with properties)

### Node: Invoice (`Invoice_836143eb823c`)
- **Label**: Invoice
- **Bill No**: 3139
- **Date**: 01.07.2020
- **Currency**: CHF
- **Subtotal**: 3667.35
- **Vat Rate**: 7.7
- **Vat Amount**: 282.4
- **Total**: 3949.75

### Node: Issuer (`Issuer_613c8041a0ac`)
- **Label**: Issuer
- **Name**: Robert Schneider AG
- **Phone**: 059/987 6540
- **Email**: robert@rschneider.ch
- **Website**: www.rschneider.ch

### Node: Address (`Address_40ad89089af3`)
- **Label**: Address
- **Street**: Rue du Lac 1268
- **Postal Code**: 2501
- **City**: Biel
- **Country**: CH

### Node: Client (`Client_f794e61ca0e6`)
- **Label**: Client
- **Name**: Pia Rutschmann
- **Phone**: None
- **Email**: None
- **Website**: None

### Node: Address (`Address_b6f37a826a92`)
- **Label**: Address
- **Street**: Marktgasse 28
- **Postal Code**: 9400
- **City**: Rorschach
- **Country**: CH

### Node: LineItem (`LineItem_2efae2ae49dc`)
- **Label**: LineItem
- **Description**: Garden work
- **Quantity**: 28.0
- **Unit**: Std.
- **Unit Price**: 120.0
- **Total**: 3360.0

### Node: LineItem (`LineItem_fc8688cc2853`)
- **Label**: LineItem
- **Description**: Disposal of cuttings
- **Quantity**: 1.0
- **Unit**: None
- **Unit Price**: 307.35
- **Total**: 307.35

## Edges (with labels)

- **Invoice → Issuer** `issued_by`
- **Invoice → Client** `sent_to`
- **Invoice → LineItem** `contains_items`
- **Invoice → LineItem** `contains_items`
- **Issuer → Address** `located_at`
- **Client → Address** `lives_at`

---

_End of Graph Summary_
