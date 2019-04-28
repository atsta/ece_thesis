

from faker import Faker

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'pro2.settings')

import django
django.setup()

from app2.models import User1




def populate(N=5):
    fakegen = Faker()
    for entry in range(N):
        fake_name = fakegen.name().split()
        fake_first_name = fake_name[0]
        fake_last_name = fake_name[1]
        fake_email = fakegen.email()

        #new entry
        user = User1.objects.get_or_create(first_name=fake_first_name, last_name=fake_last_name,email=fake_email)[0]

if __name__ == '__main__':
    print("populte db..")
    populate(20)
    print("done!")

