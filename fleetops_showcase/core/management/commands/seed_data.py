import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import (
    Profile, Driver, DriverInvoice, Deduction, Message, MessageRecipient, Task,
)

class Command(BaseCommand):
    help = 'Seed the database with SAYEDNA LOGISTICS showcase data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding SAYEDNA LOGISTICS data...'))

        if Profile.objects.exists():
            self.stdout.write(self.style.SUCCESS('Data already exists. Skipping seed.'))
            return

        # 1. Create Users
        self.stdout.write('Creating users...')

        superadmin_user = Profile.objects.create_user(
            username='admin@sayednalogistics.com',
            email='admin@sayednalogistics.com',
            password='admin123',
            first_name='Super',
            last_name='Admin',
            role='superadmin',
            position='HRManager'
        )

        manager_user = Profile.objects.create_user(
            username='manager@sayednalogistics.com',
            email='manager@sayednalogistics.com',
            password='manager123',
            first_name='Sara',
            last_name='Al-Mutairi',
            role='manager',
            position='OperationsManager'
        )

        employee_user = Profile.objects.create_user(
            username='employee@sayednalogistics.com',
            email='employee@sayednalogistics.com',
            password='employee123',
            first_name='Khalid',
            last_name='Al-Enezi',
            role='employee',
            position='Administrative'
        )

        accountant_user = Profile.objects.create_user(
            username='accountant@sayednalogistics.com',
            email='accountant@sayednalogistics.com',
            password='accountant123',
            first_name='Fatima',
            last_name='Al-Sabah',
            role='accountant',
            position='Accountant'
        )

        # 2. Create Drivers with proper contract_type values
        self.stdout.write('Creating drivers...')
        drivers = []
        today = timezone.now().date()

        # Talabat drivers
        talabat_drivers = [
            ('Ahmed Hassan', 'bike', 'Gulf City'),
            ('John Doe', 'car', 'Salmiya'),
            ('Ali Reza', 'car', 'Hawally'),
            ('Omar Nabil', 'bike', 'Farwaniya'),
            ('Hassan Mahmoud', 'bike', 'Jahra'),
        ]
        for name, v, z in talabat_drivers:
            d = Driver.objects.create(
                full_name=name,
                phone=f'965{random.randint(10000000, 99999999)}',
                civil_id_number=f'290{random.randint(100000000, 999999999)}',
                working_id=f'WID-{random.randint(1000, 9999)}',
                company_name='sayedna', contract_type='talabat',
                vehicle_type=v, zone=z,
                civil_id_expiry=today + timedelta(days=random.randint(30, 300)),
                driver_license_expiry=today + timedelta(days=random.randint(15, 200)),
                is_active=True
            )
            drivers.append(d)

        # Pharma Zone drivers
        pharma_drivers = [
            ('Mohamed Ali', 'bike', 'Salmiya'),
            ('Yusuf Ibrahim', 'car', 'Gulf City'),
            ('Rashid Khalil', 'bike', 'Hawally'),
        ]
        for name, v, z in pharma_drivers:
            d = Driver.objects.create(
                full_name=name,
                phone=f'965{random.randint(10000000, 99999999)}',
                civil_id_number=f'280{random.randint(100000000, 999999999)}',
                company_name='sayedna', contract_type='pharmazone',
                vehicle_type=v, zone=z,
                civil_id_expiry=today + timedelta(days=random.randint(30, 300)),
                is_active=True
            )
            drivers.append(d)

        # Burger King drivers
        bk_drivers = [
            ('Suresh Kumar', 'bike', 'Farwaniya'),
            ('Tariq Zaman', 'car', 'Jahra'),
        ]
        for name, v, z in bk_drivers:
            d = Driver.objects.create(
                full_name=name,
                phone=f'965{random.randint(10000000, 99999999)}',
                civil_id_number=f'281{random.randint(100000000, 999999999)}',
                company_name='sayedna', contract_type='burger_king',
                vehicle_type=v, zone=z,
                civil_id_expiry=today + timedelta(days=random.randint(30, 300)),
                is_active=True
            )
            drivers.append(d)

        # Other contract drivers
        other_drivers = [
            ('Imran Sheikh', 'car', 'Gulf City'),
            ('Naveed Akhtar', 'bike', 'Salmiya'),
        ]
        for name, v, z in other_drivers:
            d = Driver.objects.create(
                full_name=name,
                phone=f'965{random.randint(10000000, 99999999)}',
                civil_id_number=f'282{random.randint(100000000, 999999999)}',
                company_name='sayedna', contract_type='other',
                vehicle_type=v, zone=z,
                civil_id_expiry=today + timedelta(days=random.randint(30, 300)),
                is_active=True
            )
            drivers.append(d)

        # 3. Create Invoices for last 30 days
        self.stdout.write('Creating invoices...')
        for d in drivers:
            for i in range(30):
                idate = today - timedelta(days=i)
                DriverInvoice.objects.create(
                    driver=d,
                    specified_date=idate,
                    cash=Decimal(random.randint(5, 25)),
                    main_orders=random.randint(10, 20),
                    additional_orders=random.randint(0, 5),
                    hours=Decimal(random.randint(8, 12)),
                    created_by=manager_user
                )

        # 4. Create Deductions
        self.stdout.write('Creating deductions...')
        Deduction.objects.create(
            driver=drivers[0],
            reason='Speeding Ticket #123',
            deduction_date=today - timedelta(days=5),
            contracting_company='talabat',
            contractor_deduction_kd=Decimal('15.000'),
            submitted_by=manager_user
        )

        # 5. Create Messages
        self.stdout.write('Creating messages...')
        msg = Message.objects.create(
            sender=manager_user,
            subject='Welcome to SAYEDNA LOGISTICS',
            body='Welcome to the new system. Please ensure your documents are up to date.'
        )
        MessageRecipient.objects.create(message=msg, recipient=employee_user)
        MessageRecipient.objects.create(message=msg, recipient=accountant_user)
        MessageRecipient.objects.create(message=msg, recipient=superadmin_user)

        # 6. Create Tasks
        self.stdout.write('Creating tasks...')
        Task.objects.create(user=superadmin_user, title='System wide audit')
        Task.objects.create(user=manager_user, title='Review monthly reports')
        Task.objects.create(user=manager_user, title='Approve driver leaves')
        Task.objects.create(user=employee_user, title='Check vehicle maintenance')
        Task.objects.create(user=accountant_user, title='Prepare salary sheets')

        self.stdout.write(self.style.SUCCESS('SAYEDNA LOGISTICS data seeded successfully!'))
