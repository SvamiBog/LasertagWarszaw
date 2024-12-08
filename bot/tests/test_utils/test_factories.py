import random
from faker import Faker

def generate_random_user_data(is_admin = False):
    fake = Faker()

    return {
        'telegram_id': random.randint(1000000, 9999999),  # Уникальный ID
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'username': fake.unique.user_name(),
        'phone_number': fake.phone_number(),
        'language': 'en'
    }
