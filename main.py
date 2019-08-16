import json
import stripe

TEST_STRIPE_SECRET_KEY = 'sk_test_...'
PROD_STRIPE_SECRET_KEY = 'sk_live_...'

def hash_attribs(attribs):
    return json.dumps(attribs, sort_keys=True)

copy_keys = [
    'active', 'name', 'type',
    'description', 'caption', 'attributes',
    'images', 'metadata', 'shippable',
    'package_dimensions'
]

stripe.api_key = TEST_STRIPE_SECRET_KEY

products = stripe.Product.list(limit=100, active=True, type='good')['data']
skus = {}
for p in products:
    skus[p.id] = stripe.SKU.list(limit=100, product=p.id)
products += stripe.Product.list(limit=100, active=True, type='service')['data']

stripe.api_key = PROD_STRIPE_SECRET_KEY
prod_products = stripe.Product.list(limit=100, active=True, type='good')['data']
prod_skus = {}
for p in prod_products:
    skus[p.id] = {hash_attribs(s['attributes']): s for s in stripe.SKU.list(limit=100, active=True, product=p.id)}
prod_products += stripe.Product.list(limit=100, active=True, type='service')['data']
prod_products = {p.name: p for p in prod_products}

for d in products:
    name = d['name']
    kwargs = {k: d[k] for k in copy_keys}
    if name not in prod_products:
        p = stripe.Product.create(**kwargs)
        for sku in skus[d.id]:
            stripe.SKU.create(
                product=p.id,
                attributes=sku['attributes'],
                price=sku['price'],
                currency=sku['currency'],
                inventory=sku['inventory'])
    else:
        typ =  kwargs.pop('type')
        if typ != 'good':
            del kwargs['caption']
            del kwargs['description']
        p = prod_products[name]
        stripe.Product.modify(p.id, **kwargs)
        if typ == 'good':
            for sku in skus[d.id]:
                key = hash_attribs(sku['attributes'])
                if key in prod_skus.get(p.id, {}):
                    stripe.SKU.modify(
                        prod_skus[p.id][key].id,
                        attributes=sku['attributes'],
                        price=sku['price'],
                        currency=sku['currency'],
                        inventory=sku['inventory'])
                else:
                    stripe.SKU.create(
                        product=p.id,
                        attributes=sku['attributes'],
                        price=sku['price'],
                        currency=sku['currency'],
                        inventory=sku['inventory'])
