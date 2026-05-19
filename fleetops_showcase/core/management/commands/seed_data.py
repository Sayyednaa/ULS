import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import (
    Profile, Driver, DriverInvoice, Deduction, DeductionInstallment, Message, MessageRecipient, Task,
    Company,
)

class Command(BaseCommand):
    help = 'Seed the database with ULS showcase data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding ULS (Unpredictable Logistics Solutions) data...'))

        if Profile.objects.exists():
            self.stdout.write(self.style.SUCCESS('Data already exists. Skipping seed.'))
            return

        # 0. Create Default Company
        uls_company = Company.objects.create(
            name="Unpredictable Logistics Solutions",
             
        )

        # 1. Create Users
        self.stdout.write('Creating users...')

        superadmin_user = Profile.objects.create_user(
            username='admin@uls.com',
            email='admin@uls.com',
            password='admin123',
            first_name='Super',
            last_name='Admin',
            role='superadmin',
            position='Administrative',
            company=uls_company
        )

        manager_user = Profile.objects.create_user(
            username='manager@uls.com',
            email='manager@uls.com',
            password='manager123',
            first_name='Sara',
            last_name='Al-Mutairi',
            role='manager',
            position='Operations Manager',
            company=uls_company
        )

        employee_user = Profile.objects.create_user(
            username='employee@uls.com',
            email='employee@uls.com',
            password='employee123',
            first_name='Khalid',
            last_name='Al-Enezi',
            role='employee',
            position='Administrative',
            company=uls_company
        )

        accountant_user = Profile.objects.create_user(
            username='accountant@uls.com',
            email='accountant@uls.com',
            password='accountant123',
            first_name='Fatima',
            last_name='Al-Sabah',
            role='accountant',
            position='Accountant',
            company=uls_company
        )

        # 2. Create Drivers with proper company link
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
                company=uls_company,
                company_name='sayedna', # Legacy choice field
                contract_type='talabat',
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
                company=uls_company,
                company_name='sayedna',
                contract_type='pharmazone',
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
                company=uls_company,
                company_name='sayedna',
                contract_type='burger_king',
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
                    company=uls_company,
                    specified_date=idate,
                    main_orders=random.randint(10, 25),
                    hours=Decimal(random.randint(8, 12)),
                    created_by=manager_user
                )

        # 4. Create Deductions
        self.stdout.write('Creating deductions...')
        d1 = Deduction.objects.create(
            driver=drivers[0],
            company=uls_company,
            reason='Speeding Ticket #123',
            deduction_date=today - timedelta(days=5),
            contracting_company='talabat',
            contractor_deduction_kd=Decimal('15.000'),
            submitted_by=manager_user
        )
        DeductionInstallment.objects.create(
            deduction=d1,
            amount=d1.total_amount,
            due_date=d1.deduction_date,
            status='pending'
        )

        # 5. Create Messages
        self.stdout.write('Creating messages...')
        msg = Message.objects.create(
            sender=manager_user,
            company=uls_company,
            subject='Welcome to ULS',
            body='Welcome to the Unpredictable Logistics Solutions system. Please ensure your documents are up to date.'
        )
        MessageRecipient.objects.create(message=msg, recipient=employee_user)
        MessageRecipient.objects.create(message=msg, recipient=accountant_user)
        MessageRecipient.objects.create(message=msg, recipient=superadmin_user)

        # 6. Create Tasks
        self.stdout.write('Creating tasks...')
        Task.objects.create(user=superadmin_user, company=uls_company, title='System wide audit')
        Task.objects.create(user=manager_user, company=uls_company, title='Review monthly reports')
        Task.objects.create(user=manager_user, company=uls_company, title='Approve driver leaves')
        Task.objects.create(user=employee_user, company=uls_company, title='Check vehicle maintenance')
        Task.objects.create(user=accountant_user, company=uls_company, title='Prepare salary sheets')

        self.stdout.write(self.style.SUCCESS('ULS showcase data seeded successfully!'))
