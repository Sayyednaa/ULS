import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_file_extension


# ─── Choices ─────────────────────────────────────────────────────────────────

ROLE_CHOICES = [
    ('superadmin', 'Super Admin'),
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('employee', 'Employee'),
    ('accountant', 'Accountant Department'),
    ('driver', 'Driver'),
]

POSITION_CHOICES = [
    ('Administrative', 'Administrative'),
    ('Engineer', 'Engineer'),
    ('Accountant', 'Accountant'),
    ('Representative', 'Representative'),
    ('MarketingManager', 'Marketing Manager'),
    ('SalesManager', 'Sales Manager'),
    ('HRManager', 'HR Manager'),
    ('ProjectManager', 'Project Manager'),
    ('ProductManager', 'Product Manager'),
    ('BusinessAnalyst', 'Business Analyst'),
    ('SoftwareEngineer', 'Software Engineer'),
    ('WebDeveloper', 'Web Developer'),
    ('GraphicDesigner', 'Graphic Designer'),
    ('ContentWriter', 'Content Writer'),
    ('CustomerSupportRepresentative', 'Customer Support Representative'),
    ('DataAnalyst', 'Data Analyst'),
    ('OperationsManager', 'Operations Manager'),
    ('AdminAssistant', 'Admin Assistant'),
    ('TeamLeader', 'Team Leader'),
    ('MarketingSpecialist', 'Marketing Specialist'),
    ('LegalAdvisor', 'Legal Advisor'),
    ('ITSupportSpecialist', 'IT Support Specialist'),
    ('Receptionist', 'Receptionist'),
    ('Intern', 'Intern'),
]

BANK_CHOICES = [
    ('nbk', 'National Bank of Gulf (NBK)'),
    ('kfh', 'Gulf Finance House (KFH)'),
    ('gulf_bank', 'Gulf Bank'),
    ('burgan', 'Burgan Bank'),
    ('al_ahli', 'Al Ahli Bank of Gulf'),
    ('commercial', 'Commercial Bank of Gulf'),
    ('boubyan', 'Boubyan Bank'),
    ('other', 'Other'),
]

COMPANY_CHOICES = [
    ('sayedna', 'SAYEDNA LOGISTICS'),
    ('speedy', 'Speedy'),
    ('other', 'Other'),
]

CONTRACT_CHOICES = [
    ('talabat', 'Talabat'),
    ('burger_king', 'Burger King'),
    ('pharmazone', 'Pharmazone'),
    ('other', 'Other'),
]

VEHICLE_CHOICES = [
    ('car', 'Car'),
    ('bike', 'Bike'),
    ('motorcycle', 'Motorcycle'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('document_expiry', 'Document Expiry'),
    ('invoice_action', 'Invoice Action'),
    ('new_message', 'New Message'),
    ('deduction', 'Deduction'),
    ('system', 'System'),
]


# ─── Profile (AUTH_USER_MODEL) ──────────────────────────────────────────────

class Profile(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='superadmin')
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default='Administrative')
    identification_number = models.CharField(max_length=50, blank=True)
    passport = models.CharField(max_length=50, blank=True)
    contract_expiry_date = models.DateField(null=True, blank=True)
    base_salary_kd = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    iban_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=30, choices=BANK_CHOICES, default='nbk')
    supporting_document = models.FileField(upload_to='profile_docs/', null=True, blank=True, validators=[validate_file_extension])
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'superadmin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


# ─── Driver ─────────────────────────────────────────────────────────────────

class Driver(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Identity
    civil_id_number = models.CharField(max_length=50)
    civil_id_expiry = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)

    # Work Compliance
    working_permit_expiry = models.DateField(null=True, blank=True)
    driver_license_expiry = models.DateField(null=True, blank=True)
    health_insurance_expiry = models.DateField(null=True, blank=True)
    criminal_certificate_expiry = models.DateField(null=True, blank=True)

    # Vehicle
    vehicle_registration = models.CharField(max_length=100, blank=True, verbose_name="VEHICLE REGISTRATION NUMBER")
    vehicle_registration_expiry = models.DateField(null=True, blank=True, verbose_name="VEHICLE REGISTRATION NUMBER EXPIRY")
    vehicle_plate_number = models.CharField(max_length=30, blank=True)
    vehicle_name = models.CharField(max_length=100, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='car')

    # Work Assignment
    zone = models.CharField(max_length=100, blank=True)
    petrol_card_number = models.CharField(max_length=50, blank=True)
    employee_serial_number = models.CharField(max_length=50, blank=True)
    working_id = models.CharField(max_length=50, blank=True)
    company_name = models.CharField(max_length=50, choices=COMPANY_CHOICES, default='sayedna')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default='talabat')
    position = models.CharField(max_length=100, default='Car Driver')

    # Financial
    iban_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=30, choices=BANK_CHOICES, blank=True)
    basic_salary_wp = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    # Documents
    supporting_document = models.FileField(upload_to='driver_docs/', null=True, blank=True, validators=[validate_file_extension])
    civil_id_file = models.FileField(upload_to='driver_docs/civil_id/', null=True, blank=True, validators=[validate_file_extension])
    driving_license_file = models.FileField(upload_to='driver_docs/driving_license/', null=True, blank=True, validators=[validate_file_extension])
    work_permit_file = models.FileField(upload_to='driver_docs/work_permit/', null=True, blank=True, validators=[validate_file_extension])
    health_card_file = models.FileField(upload_to='driver_docs/health_card/', null=True, blank=True, validators=[validate_file_extension])
    criminal_pcc_file = models.FileField(upload_to='driver_docs/criminal_pcc/', null=True, blank=True, validators=[validate_file_extension])
    passport_file = models.FileField(upload_to='driver_docs/passport/', null=True, blank=True, validators=[validate_file_extension])
    vehicle_rc_file = models.FileField(upload_to='driver_docs/vehicle_rc/', null=True, blank=True, validators=[validate_file_extension])
    photo_selfie = models.ImageField(upload_to='driver_docs/photo/', null=True, blank=True, validators=[validate_file_extension])
    other_docs_file = models.FileField(upload_to='driver_docs/other/', null=True, blank=True, validators=[validate_file_extension])
    received_equipments_file = models.FileField(upload_to='driver_docs/received_equipments/', null=True, blank=True, validators=[validate_file_extension])

    # Meta
    is_active = models.BooleanField(default=True)
    file_status = models.CharField(max_length=50, blank=True, default='Active')
    created_by = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, related_name='created_drivers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Link to login account (optional)
    profile = models.OneToOneField(
        Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_profile'
    )

    def __str__(self):
        return self.full_name

    @property
    def get_full_name(self):
        return self.full_name

    def get_expiring_documents(self, days=30):
        from datetime import date, timedelta
        today = date.today()
        warning_date = today + timedelta(days=days)
        docs = [
            ('Civil ID', self.civil_id_expiry),
            ('Passport', self.passport_expiry),
            ('Working Permit', self.working_permit_expiry),
            ('Driver License', self.driver_license_expiry),
            ('Health Insurance', self.health_insurance_expiry),
            ('Criminal Certificate', self.criminal_certificate_expiry),
            ('Vehicle Registration', self.vehicle_registration_expiry),
        ]
        results = []
        for label, expiry in docs:
            if not expiry:
                status = 'missing'
                days_remaining = None
            elif expiry < today:
                status = 'expired'
                days_remaining = (today - expiry).days
            elif expiry <= warning_date:
                status = 'warning'
                days_remaining = (expiry - today).days
            else:
                status = 'ok'
                days_remaining = (expiry - today).days
            results.append({
                'label': label,
                'expiry': expiry,
                'status': status,
                'days_remaining': days_remaining,
            })
        return results

    def has_expiry_warning(self):
        return any(d['status'] in ['warning', 'expired'] for d in self.get_expiring_documents())

    def get_warning_summary(self):
        warnings = []
        for d in self.get_expiring_documents():
            if d['status'] == 'expired':
                warnings.append(f"{d['label']} Expired")
            elif d['status'] == 'warning':
                warnings.append(f"{d['label']} Expiring Soon")
        return ", ".join(warnings)

    class Meta:
        ordering = ['full_name']


# ─── DriverInvoice ──────────────────────────────────────────────────────────

class DriverInvoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='invoices')
    cash = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    main_orders = models.IntegerField(default=0)
    additional_orders = models.IntegerField(default=0)
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    specified_date = models.DateField()
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-specified_date']
        indexes = [models.Index(fields=['driver', 'specified_date'])]
        unique_together = ('driver', 'specified_date')

    def __str__(self):
        return f"{self.driver} - {self.specified_date}"

    @property
    def total_orders(self):
        return self.main_orders


# ─── InvoiceArchive ─────────────────────────────────────────────────────────

class InvoiceArchive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='archives')
    driver_name = models.CharField(max_length=200)
    cash = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    main_orders = models.IntegerField(default=0)
    additional_orders = models.IntegerField(default=0)
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    archive_date = models.DateField()
    archived_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    salary_slip_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-archive_date']
        indexes = [models.Index(fields=['driver', 'archive_date'])]

    def __str__(self):
        return f"{self.driver_name} - Archive {self.archive_date}"

    @property
    def total_orders(self):
        return self.main_orders


# ─── Deduction ──────────────────────────────────────────────────────────────

class Deduction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='deductions'
    )
    employee = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='deductions'
    )
    reason = models.TextField()
    deduction_date = models.DateField()
    contracting_company = models.CharField(max_length=20, choices=CONTRACT_CHOICES)
    contractor_deduction_kd = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    company_deduction_kd = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    # New fields for installment plans
    is_installment_plan = models.BooleanField(default=False)
    total_installments = models.IntegerField(default=1)
    
    pdf_proof = models.FileField(upload_to='deduction_pdfs/', null=True, blank=True, validators=[validate_file_extension])
    submitted_by = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, related_name='submitted_deductions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-deduction_date']

    def __str__(self):
        target = self.driver or self.employee
        return f"Deduction: {target} - {self.deduction_date}"

    @property
    def total_amount(self):
        return self.contractor_deduction_kd + self.company_deduction_kd

    @property
    def paid_amount(self):
        return sum(i.amount for i in self.installments.filter(status='paid'))

    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount


class DeductionInstallment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deduction = models.ForeignKey(Deduction, on_delete=models.CASCADE, related_name='installments')
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('paid', 'Paid')], 
        default='pending'
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_payments'
    )
    
    # Digital Signature
    signature_data = models.TextField(blank=True, null=True, help_text="Base64 signature data")
    signature_image = models.ImageField(upload_to='signatures/', null=True, blank=True, validators=[validate_file_extension])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"Installment {self.amount} for {self.deduction}"


# ─── Message / MessageRecipient ─────────────────────────────────────────────

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True, validators=[validate_file_extension])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} (from {self.sender})"


class MessageRecipient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='recipients')
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_messages')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['recipient', 'is_read'])]

    def __str__(self):
        return f"{self.message.subject} → {self.recipient}"


# ─── Notification ───────────────────────────────────────────────────────────

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField()
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    related_driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read'])]

    def __str__(self):
        return f"{self.title} ({self.user})"


# ─── Task ───────────────────────────────────────────────────────────────────

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tasks', verbose_name='Assigned To')
    assigned_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['user'])]
        ordering = ['status', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"

# ─── CompanyFile ────────────────────────────────────────────────────────────

class CompanyFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='company_files/', validators=[validate_file_extension])
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


# ─── Accountant Portal Models ───────────────────────────────────────────────

class TalabatSalaryDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='talabat_salaries')
    month = models.DateField()
    
    # Batch 1 to 7
    batch_1_orders = models.IntegerField(default=0)
    batch_1_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    batch_1_net_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    batch_2_orders = models.IntegerField(default=0)
    batch_2_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    batch_2_net_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    batch_3_orders = models.IntegerField(default=0)
    batch_3_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    batch_3_net_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    batch_4_orders = models.IntegerField(default=0)
    batch_4_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    batch_4_net_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    batch_5_orders = models.IntegerField(default=0)
    batch_5_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    batch_5_net_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    batch_6_orders = models.IntegerField(default=0)
    batch_6_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    batch_6_net_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    batch_7_orders = models.IntegerField(default=0)
    batch_7_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    batch_7_net_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    deduction = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    attachment = models.FileField(upload_to='talabat_attachments/', null=True, blank=True, validators=[validate_file_extension])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month', 'driver__full_name']
        unique_together = ('driver', 'month')

    @property
    def total_orders(self):
        return (
            self.batch_1_orders + self.batch_2_orders + self.batch_3_orders +
            self.batch_4_orders + self.batch_5_orders + self.batch_6_orders + self.batch_7_orders
        )

    @property
    def total_amount(self):
        return (
            self.batch_1_amount + self.batch_2_amount + self.batch_3_amount +
            self.batch_4_amount + self.batch_5_amount + self.batch_6_amount + self.batch_7_amount
        )

    @property
    def total_net_amount(self):
        return (
            self.batch_1_net_amount + self.batch_2_net_amount + self.batch_3_net_amount +
            self.batch_4_net_amount + self.batch_5_net_amount + self.batch_6_net_amount + self.batch_7_net_amount
        )

    @property
    def net_salary(self):
        return self.total_net_amount - self.deduction

    def __str__(self):
        return f"Talabat Salary: {self.driver} - {self.month.strftime('%B %Y')}"


class ContractSalaryDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES)
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='contract_salaries')
    name = models.CharField(max_length=200)
    total_salary = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    absent = models.IntegerField(default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    attachment = models.FileField(upload_to='contract_attachments/', null=True, blank=True, validators=[validate_file_extension])
    remark = models.TextField(blank=True)
    month = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month', 'name']

    @property
    def net_salary(self):
        return self.total_salary - self.deduction

    def __str__(self):
        return f"{self.get_contract_type_display()} Salary: {self.name} - {self.month.strftime('%B %Y')}"


class MonthlyProfitLoss(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=200)
    contract_name = models.CharField(max_length=200)
    expense = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    month = models.DateField()
    report_pdf = models.FileField(upload_to='monthly_reports/', null=True, blank=True, validators=[validate_file_extension])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month', 'company_name']

    def __str__(self):
        return f"P&L: {self.company_name} - {self.contract_name} ({self.month.strftime('%B %Y')})"
