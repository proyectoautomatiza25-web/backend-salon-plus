import mercadopago
sdk = mercadopago.SDK("TEST")
print("SDK Attributes:", dir(sdk))
if hasattr(sdk, 'subscription'):
    print("Subscription Attributes:", dir(sdk.subscription))
if hasattr(sdk, 'preapproval'):
    print("Preapproval Attributes:", dir(sdk.preapproval))
