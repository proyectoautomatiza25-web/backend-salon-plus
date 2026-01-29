import mercadopago
sdk = mercadopago.SDK("TEST")
def list_methods(obj, name):
    methods = [m for m in dir(obj) if not m.startswith('__')]
    print(f"{name} methods: {methods}")

list_methods(sdk, "SDK")
if hasattr(sdk, 'preapproval'): list_methods(sdk.preapproval, "Preapproval")
if hasattr(sdk, 'subscription'): list_methods(sdk.subscription, "Subscription")
