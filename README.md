# Avito listing price coverage — why one "price coverage %" for a classifieds API is meaningless (measured, 2026)

**Electronics 45/45. Property to rent 50/50. Bicycles 48/48. Job ads 26/49. Aggregate: 85%, and that
85% describes your query mix rather than the data.**

Measured per category, because on a classifieds site the share of rows carrying a price is a
property of the *category*, not of the API you are evaluating.

Run it yourself with a [free ReefAPI key](https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=avito-listing-price-coverage)
(1,000 credits, no card), or point the one provider-specific function at any other
[classifieds data API](https://reefapi.com/docs/avito?utm_source=github&utm_medium=repo&utm_campaign=avito-listing-price-coverage)
and compare the same six categories.

This is a dataset and a script, not a client library. **The comparison is the point.**

---

## The finding

Measured 2026-09-25, one query per category, 288 rows:

| category | rows | with price | no price | free | withheld | neither |
|---|---:|---:|---:|---:|---:|---:|
| electronics | 45 | **45 (100%)** | 0 | 0 | 0 | 0 |
| property to rent | 50 | **50 (100%)** | 0 | 0 | 0 | 0 |
| bicycles | 48 | **48 (100%)** | 0 | 0 | 0 | 0 |
| furniture | 48 | 44 (92%) | 4 | **4** | 0 | 0 |
| pets | 48 | 33 (69%) | 15 | **15** | 0 | 0 |
| job ads | 49 | **26 (53%)** | 23 | 0 | **1** | 22 |
| **total** | **288** | **246 (85%)** | 42 | 19 | 1 | 22 |

Read the aggregate on its own and you would conclude the API drops 15% of prices. Read the
breakdown and there is nothing to fix: **the categories that have prices return them 100% of the
time.** The gap is job ads, which do not have a price, and items being given away.

## A null price means three different things

This is the part most integrations get wrong, and the reason the table above has three columns
instead of one:

| what it means | how you can tell |
|---|---|
| genuinely free, "take it away" | `is_free: true` — 19 of the 42 |
| the seller chose not to publish it | `price_not_published: true` — 1 of the 42 |
| the category simply has no price | neither flag set — 22 of the 42, all job ads |

If a provider collapses all three into `price: null`, **you cannot tell a free sofa from a scraping
failure**, and you will spend a day debugging a bug that does not exist.

## What one row actually looks like

One complete row from `avito/v1/search`, returned 2026-09-25, with nothing removed except
two personal fields. Every field name the endpoint can return is here, so you can check
whether the one you need exists before writing a line of code.

```json
{
  "ad_id": "8513237980",
  "title": "iPhone 18 Pro Max, 256 ГБ, SIM + eSIM",
  "url": "https://www.avito.ru/rostov-na-donu/telefony/iphone_18_pro_max_256_gb_sim_esim_8513237980",
  "category": {
    "category_id": 84,
    "name": "Телефоны",
    "slug": "telefony",
    "root_category_id": 6
  },
  "subtitle": null,
  "price": 176500,
  "price_min": null,
  "price_max": null,
  "price_is_from": false,
  "currency": "RUB",
  "price_text": "176 500 ₽",
  "price_period": null,
  "is_free": false,
  "price_not_published": false,
  "price_before_discount": null,
  "discount_percent": null,
  "price_lowered": false,
  "price_per_unit": null,
  "published_at": "2026-09-25T14:56:46Z",
  "location": {
    "location_id": 652000,
    "name": "Ростов-на-Дону",
    "address": "Ростовская обл., Ростов-на-Дону",
    "nearby": null
  },
  "coordinates": {
    "lat": 47.231967,
    "lng": 39.702679,
    "precision": "exact"
  },
  "coordinates_withheld": false,
  "address_as_typed": "<redacted in this README — returned populated in your own calls>",
  "seller": {
    "type": "company",
    "type_label": "Компания",
    "has_shop": false,
    "name": "<redacted in this README — returned populated in your own calls>",
    "name_withheld": false,
    "name_hidden_by_avito": false,
    "profile_id": null,
    "profile_url": "https://www.avito.ru",
    "rating": 4.9,
    "rating_scale": 5,
    "reviews_count": 108,
    "closed_ads_count": 616,
    "reseller_likely": true,
    "reseller_reasons": [
      "company account",
      "616 closed ads (>= 30)",
      "<1 more — same shape>"
    ],
    "info": null,
    "badges": [
      "Надёжный продавец"
    ]
  },
  "images": [
    "https://40.img.avito.st/image/1/1.chHeKraA3viQgCTztl8hT8eK3Pxsndr4bPq__Gxx1QJhidrikIAk82g.a-yrQwrHHoQz68C3ZsH3NDFFapb_3qfWjrUNCZO0QwA",
    "https://20.img.avito.st/image/1/1.xBkY3baAaPBWd5L7HKbGRgF9avSqamzwqg0J9KqGYwqnfmzqVneS-64.Q_AmNFWI7HJK0Bg5wfo-m69xbBCdYfphnsOkOM4PpGo?cqp=2.2LhnDdKx1gU5sZ7QAbwhSdJoeYt5K_KL9JwGcCXpGrDVbBxJ1yJf9Jn7hY3rGWaiHtSha9zz1w=="
  ],
  "images_count": 2,
  "has_video": false,
  "description_snippet": "18 pro max 256 в цвете Bulgundy.\n\nДанная позиция под заказ на следующий день, если есть на складе.\n\nПривезем за 1 день.\n\nЦена указана за наличный расчет, оплата по безналу — комиссия.\n\nПочему стоит покупать у нас:\n\nМагазин в центре города с удобной п...",
  "params_summary": "Новый",
  "badges": [
    "Цена ниже рыночной"
  ],
  "development_name": null,
  "realty_type": null,
  "is_promoted": false,
  "paid_services": null,
  "is_xl": false,
  "is_reserved": false,
  "delivery_available": false,
  "delivery_text": null,
  "is_verified_item": false
}
```

> **Only this README hides those values.** The API returns them populated: seller name, street
> address and the contact fields all come back in your own calls, and for most customers that is
> the point of the endpoint. They are masked here because a public README is not the right place to
> republish an individual's details, not because the data is unavailable.

Note `price_not_published`, `is_free` and `coordinates_withheld` sitting next to the values
they explain. That is this repo's argument in one object: **a null is only useful if
something beside it says why.**

## Why it is worth measuring yourself

The general lesson is not about Avito and not about us: **an aggregate field-coverage number is only
meaningful inside a category.** Before you accept or reject any classifieds provider, run the same
count per category on both, and look for whether the null is *explained* rather than merely present.

Location behaves the same way in this sample: 288 rows returned coordinates on 255, and the misses
cluster in shippable goods rather than spreading evenly.

## Run it

Get a key at [reefapi.com/signup](https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=avito-listing-price-coverage) — 1,000 credits, no card.

```bash
export REEFAPI_KEY=...
python measure.py
```

Six calls, 1 credit each.

### Comparing another provider

`fetch()` is the only provider-specific function. Point it at another classifieds endpoint, keep
`summarise()` as it is, and the table is directly comparable. The three-way split needs the other
provider to expose an equivalent of `is_free` and `price_not_published`; if it does not, that is
itself a result worth writing down.

## What is in here

| file | what |
|---|---|
| `measure.py` | the script, one provider-specific function |
| `data/coverage.json` | full result per category |
| `data/coverage.csv` | the same table |

## Caveats, stated rather than buried

* **A snapshot.** Dated 2026-09-25. Re-run it rather than citing the table as a current fact.
* **One query per category.** ~48 rows is one page of results, not a random sample of the category.
* **Category is inferred from the query**, not from a taxonomy id. "работа" returns job ads; it is
  not the same as asking the site for its jobs category.
* **Presence, not accuracy.** This counts whether a price is populated, not whether it is correct.
* **A ReefAPI repo.** We build the API this runs against, so read the numbers as reproducible rather
  than disinterested. That is why the script is here and the raw output is committed.

## Related

* [Avito API documentation — search, listings, cars and property endpoints](https://reefapi.com/docs/avito?utm_source=github&utm_medium=repo&utm_campaign=avito-listing-price-coverage)
* [One API key for 300+ web data sources](https://reefapi.com/?utm_source=github&utm_medium=repo&utm_campaign=avito-listing-price-coverage), one shared credit pool
* Same method applied to sold prices: [zillow-sold-price-coverage](https://github.com/reefapi/zillow-sold-price-coverage)

MIT licensed. Issues and pull requests welcome, especially a `fetch()` for another provider.
