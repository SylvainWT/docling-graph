# Knowledge Graph Report

---

## Nodes (with properties):

### Node: Invoice (`Invoice_47cf4dcbc4`)
- **id**: Invoice_47cf4dcbc4
- **label**: Invoice
- **bill_no**: 3139
- **date**: 2020-07-01
- **currency**: CHF
- **subtotal**: 360.0
- **vat_rate**: 7.7
- **vat_amount**: 282.4
- **total**: 3949.75

### Node: Issuer (`Issuer_613c8041a0`)
- **id**: Issuer_613c8041a0
- **label**: Issuer
- **name**: Robert Schneider AG
- **phone**: 059/987 6540
- **email**: robert@rschneider.ch
- **website**: www.rschneider.ch

### Node: Address (`Address_52dae2cc0f`)
- **id**: Address_52dae2cc0f
- **label**: Address
- **street**: Rue du Lac 1268
- **postal_code**: 2501
- **city**: Biel

### Node: Client (`Client_c873814ac1`)
- **id**: Client_c873814ac1
- **label**: Client
- **name**: MineralTree

### Node: Address (`Address_24a67ff16b`)
- **id**: Address_24a67ff16b
- **label**: Address
- **street**: Rue du Lac 1268
- **postal_code**: 9400
- **city**: Biel

### Node: LineItem (`LineItem_dd0c85f2d1`)
- **id**: LineItem_dd0c85f2d1
- **label**: LineItem
- **description**: Garden work
- **quantity**: 28.0
- **unit**: Std.
- **unit_price**: 120.0
- **total**: 360.0

### Node: LineItem (`LineItem_944461d439`)
- **id**: LineItem_944461d439
- **label**: LineItem
- **description**: Disposal of cuttings
- **quantity**: 1.0
- **unit**: Std.
- **unit_price**: 307.35
- **total**: 307.35

## Edges (with labels):

- **Invoice → Issuer**  `issued_by`
- **Invoice → Client**  `sent_to`
- **Invoice → LineItem**  `contains_items`
- **Invoice → LineItem**  `contains_items`
- **Issuer → Address**  `located_at`
- **Client → Address**  `lives_at`

---

_End of Graph Summary_
