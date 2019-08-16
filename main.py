import stripe

TEST_STRIPE_SECRET_KEY = 'sk_test_...'
PROD_STRIPE_SECRET_KEY = 'sk_live_...'

copy_keys = [
    'active', 'name', 'type',
    'description', 'caption', 'attributes',
    'images', 'metadata', 'shippable',
    'package_dimensions'
]

stripe.api_key = TEST_STRIPE_SECRET_KEY

products = stripe.Product.list(limit=100, active=True, type='good')['data']
products += stripe.Product.list(limit=100, active=True, type='service')['data']

stripe.api_key = PROD_STRIPE_SECRET_KEY
prod_products = stripe.Product.list(limit=100, active=True, type='good')['data']
prod_products += stripe.Product.list(limit=100, active=True, type='service')['data']
prod_products = {p.name: p for p in prod_products}

for d in products:
    name = d['name']
    kwargs = {k: d[k] for k in copy_keys}
    if name not in prod_products:
        stripe.Product.create(**kwargs)
    else:
        typ =  kwargs.pop('type')
        if typ != 'good':
            del kwargs['caption']
            del kwargs['description']
        p = prod_products[name]
        stripe.Product.modify(p.id, **kwargs)