# Customer RFM Segmentation

This project segments customers using Recency, Frequency, and Monetary analysis on transaction-level retail data.

The goal is to convert purchase history into practical CRM segments and campaign actions.

## Business Problem

A marketing or retention team needs to prioritize customer groups instead of sending the same campaign to everyone.

The key questions:

1. Which customers are the most valuable?
2. Which customers are active but low value?
3. Which high-value customers are becoming inactive?
4. Which segments should receive loyalty, cross-sell, or reactivation campaigns?

## Dataset

Source: UCI Online Retail Dataset.

Dataset overview:

| Field | Description |
|---|---|
| InvoiceNo | Transaction identifier |
| StockCode | Product identifier |
| Description | Product description |
| Quantity | Purchased quantity |
| InvoiceDate | Transaction timestamp |
| UnitPrice | Product unit price |
| CustomerID | Customer identifier |
| Country | Customer country |

Data period: December 2010 to December 2011.

## Methodology

The analysis follows this workflow:

1. Load transaction data.
2. Remove duplicates, cancelled transactions, and missing customer identifiers.
3. Calculate customer-level Recency, Frequency, and Monetary values.
4. Assign R, F, and M scores using quartiles.
5. Combine scores into customer segments.
6. Analyze segment size, value, and behavior.
7. Convert segments into marketing actions.

## Metrics

Recency:

```text
recency = analysis_date - last_purchase_date
```

Frequency:

```text
frequency = number of unique purchases per customer
```

Monetary:

```text
monetary = sum(quantity * unit_price)
```

RFM score:

```text
rfm_score = r_score + f_score + m_score
```

## Segment Logic

Initial segment groups:

| Segment | Description | Suggested Action |
|---|---|---|
| Champions | Recent, frequent, high-value customers | Loyalty and VIP offers |
| Loyal Customers | Frequent buyers with stable activity | Cross-sell and retention offers |
| Potential Loyalists | Recent customers with growing activity | Onboarding and product education |
| At Risk High Value | High monetary value but low recent activity | Reactivation campaign |
| Need Attention | Medium activity with weakening behavior | Personalized reminder |
| Low Value Casual | Low frequency and low monetary value | Low-cost automated campaigns |

## Visualizations

### Customer Distribution by RFM Score

![RFM Score Distribution](screenshots/rfm_score_distribution.png)

### Average Monetary Value by Recency and Frequency

![RFM Heatmap](screenshots/rfm_heatmap.png)

## Key Findings

1. Recent and frequent customers generate the highest value.
2. High-value inactive customers are a separate priority group.
3. Broad campaigns would waste budget on low-value segments.
4. RFM segmentation helps translate transaction history into clear CRM actions.

## Business Recommendations

1. Protect the Champions segment.
   Use loyalty mechanics instead of broad discounts.

2. Reactivate high-value inactive customers first.
   They have stronger potential value than low-frequency casual users.

3. Use low-cost automation for low-value segments.
   Expensive promotions should not target the full base.

4. Track segment migration monthly.
   Movement from Champions to At Risk should trigger CRM action.

5. Add revenue share by segment.
   Segment size alone is not enough for campaign prioritization.

## Limitations

- The dataset does not include acquisition source, margin, discount cost, or campaign exposure.
- RFM does not explain why customers change behavior.
- Monetary value is based on revenue, not profit.
- The current version does not evaluate campaign uplift.
- Segment names are business rules and should be validated with stakeholders.

## Next Steps

Planned improvements:

- add revenue share by segment,
- add country-level segment comparison,
- add segment migration over time,
- add SQL implementation,
- create a Tableau dashboard for CRM prioritization.

## Tools

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook
