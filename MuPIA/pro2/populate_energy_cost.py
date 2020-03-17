import os

def populate():
    p, created = Energy_Cost.objects.get_or_create(energy_type="Biomass hh", price_with_taxes="64.6", price_without_taxes="52.1", growth_rate="0.02")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Diesel oil hh", price_with_taxes="98.6", price_without_taxes="41.8", growth_rate="0.025")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Diesel oil tertiary", price_with_taxes="79.5", price_without_taxes="41.8", growth_rate="0.025")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Diesel oil transport", price_with_taxes="104.8", price_without_taxes="49.0", growth_rate="0.025")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Electricity hh", price_with_taxes="177.0", price_without_taxes="124.0", growth_rate="0.015")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Electricity tertiary", price_with_taxes="166.4", price_without_taxes="116.0", growth_rate="0.015")
    p, created = Energy_Cost.objects.get_or_create(energy_type="LPG price", price_with_taxes="56.3", price_without_taxes="45.4", growth_rate="0.017")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Motor Gasoline", price_with_taxes="134.7", price_without_taxes="45.0", growth_rate="0.025")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Natural gas hh", price_with_taxes="62.0", price_without_taxes="51.0", growth_rate="0.017")
    p, created = Energy_Cost.objects.get_or_create(energy_type="Natural gas tertiary", price_with_taxes="62.0", price_without_taxes="51.0", growth_rate="0.017")

if __name__ == '__main__':
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'pro2.settings')
    django.setup()
    from app2.models import Energy_Cost
    populate()
