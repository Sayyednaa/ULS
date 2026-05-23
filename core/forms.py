from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    Profile, Driver, DriverInvoice, Deduction, DeductionInstallment, Message,
    ROLE_CHOICES, POSITION_CHOICES, BANK_CHOICES, COMPANY_CHOICES,
    CONTRACT_CHOICES, VEHICLE_CHOICES, Task, CompanyFile, Company,
    DriverReceiving, CURRENCY_CHOICES
)


# ─── Tailwind form widget helper (Najmat Style) ──────────────────────────────
TW_INPUT = 'block w-full rounded-md border border-app-border bg-app-bg py-2 px-3 text-app-text sm:text-sm sm:leading-6 transition-colors shadow-sm outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand placeholder-app-text-muted disabled:opacity-60'
TW_INPUT_AUTH = 'w-full pl-12 pr-4 py-4 bg-black/40 border border-white/5 rounded-2xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 focus:bg-black/60 transition-all'
TW_SELECT = TW_INPUT + ' cursor-pointer'
TW_TEXTAREA = TW_INPUT + ' min-h-[100px]'
TW_FILE = 'block w-full text-sm text-app-text-muted file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-brand/10 file:text-brand hover:file:bg-brand/20 border border-app-border rounded-md bg-app-bg'
TW_DATE = TW_INPUT
TW_CHECKBOX = 'w-4 h-4 rounded border-app-border text-brand focus:ring-brand'


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': TW_INPUT_AUTH,
            'placeholder': 'Email address',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TW_INPUT_AUTH,
            'placeholder': 'Password',
            'x-bind:type': "showPass ? 'text' : 'password'",
        })
    )


class ProfileForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password', required=False,
        widget=forms.PasswordInput(attrs={'class': TW_INPUT, 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password', required=False,
        widget=forms.PasswordInput(attrs={'class': TW_INPUT, 'placeholder': 'Confirm Password'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.role == 'manager':
                self.fields['role'].choices = [('employee', 'Employee'), ('accountant', 'Accountant')]
            elif user.role == 'admin':
                self.fields['role'].choices = [('manager', 'Manager'), ('employee', 'Employee'), ('accountant', 'Accountant')]
            # Superadmin can see all (including superadmin role)

    role = forms.ChoiceField(
        choices=[('superadmin', 'Super Admin'), ('manager', 'Manager'), ('employee', 'Employee'), ('accountant', 'Accountant')],
        widget=forms.Select(attrs={'class': TW_SELECT}),
        initial='manager'
    )

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'identification_number', 'passport',
            'contract_expiry_date', 'base_salary_kd', 'iban_number', 'bank_name',
            'role', 'position', 'avatar', 'supporting_document',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': TW_INPUT, 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Phone Number'}),
            'identification_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Identification Number'}),
            'passport': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Passport'}),
            'contract_expiry_date': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'base_salary_kd': forms.NumberInput(attrs={'class': TW_INPUT, 'step': '0.001', 'placeholder': 'Base Salary (KD)'}),
            'iban_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'IBAN Number'}),
            'bank_name': forms.Select(attrs={'class': TW_SELECT}),
            'position': forms.Select(attrs={'class': TW_SELECT}),
            'supporting_document': forms.FileInput(attrs={'class': TW_FILE}),
            'avatar': forms.FileInput(attrs={'class': TW_FILE}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.username:
            user.username = self.cleaned_data['email']
        p1 = self.cleaned_data.get('password1')
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
        return user


class ProfileSelfUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='New Password', required=False,
        widget=forms.PasswordInput(attrs={'class': TW_INPUT, 'placeholder': 'New Password (Leave blank to keep current)'})
    )
    password2 = forms.CharField(
        label='Confirm New Password', required=False,
        widget=forms.PasswordInput(attrs={'class': TW_INPUT, 'placeholder': 'Confirm New Password'})
    )

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone', 'position', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TW_INPUT}),
            'last_name': forms.TextInput(attrs={'class': TW_INPUT}),
            'email': forms.EmailInput(attrs={'class': TW_INPUT}),
            'phone': forms.TextInput(attrs={'class': TW_INPUT}),
            'position': forms.Select(attrs={'class': TW_SELECT}),
            'avatar': forms.FileInput(attrs={'class': TW_FILE}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
        return user


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            # Identity & Contact
            'full_name', 'working_id', 'phone', 'email',
            'civil_id_number', 'civil_id_expiry',
            'passport_number', 'passport_expiry',
            
            # Compliance
            'working_permit_expiry',
            'driver_license_expiry',
            'health_insurance_expiry',
            'criminal_certificate_expiry',
            
            # Vehicle
            'vehicle_registration', 'vehicle_registration_expiry',
            'vehicle_plate_number', 'vehicle_name', 'vehicle_type',
            
            # Work Info
            'zone', 'petrol_card_number',
            'company_name', 'contract_type', 'position',
            'iban_number', 'bank_name', 'basic_salary_wp',
            'file_status',

            # File Uploads (at the end)
            'civil_id_file', 'passport_file', 'work_permit_file', 
            'driving_license_file', 'health_card_file', 'vehicle_rc_file',
            'criminal_pcc_file', 'photo_selfie', 'other_docs_file',
            'received_equipments_file',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': TW_INPUT, 'placeholder': 'Email Address (Optional)'}),
            'civil_id_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Civil ID Number'}),
            'civil_id_expiry': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'passport_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Passport Number'}),
            'passport_expiry': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'working_permit_expiry': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'driver_license_expiry': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'health_insurance_expiry': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'vehicle_registration': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Vehicle Registration Number'}),
            'vehicle_registration_expiry': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'vehicle_plate_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Vehicle Plate Number'}),
            'vehicle_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Vehicle Name'}),
            'vehicle_type': forms.Select(attrs={'class': TW_SELECT}),
            'zone': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Zone / Working Area'}),
            'petrol_card_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Petrol Card Number'}),
            'working_id': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Working ID'}),
            'company_name': forms.Select(attrs={'class': TW_SELECT}),
            'contract_type': forms.Select(attrs={'class': TW_SELECT}),
            'position': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Profession'}),
            'iban_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'IBAN Number'}),
            'bank_name': forms.Select(attrs={'class': TW_SELECT}),
            'basic_salary_wp': forms.NumberInput(attrs={'class': TW_INPUT, 'step': '0.001', 'placeholder': 'Basic Salary (WP)'}),
            'criminal_certificate_expiry': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'file_status': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'File Status'}),
            
            # File widgets
            'civil_id_file': forms.FileInput(attrs={'class': TW_FILE}),
            'passport_file': forms.FileInput(attrs={'class': TW_FILE}),
            'work_permit_file': forms.FileInput(attrs={'class': TW_FILE}),
            'driving_license_file': forms.FileInput(attrs={'class': TW_FILE}),
            'health_card_file': forms.FileInput(attrs={'class': TW_FILE}),
            'vehicle_rc_file': forms.FileInput(attrs={'class': TW_FILE}),
            'criminal_pcc_file': forms.FileInput(attrs={'class': TW_FILE}),
            'photo_selfie': forms.FileInput(attrs={'class': TW_FILE}),
            'other_docs_file': forms.FileInput(attrs={'class': TW_FILE}),
            'received_equipments_file': forms.FileInput(attrs={'class': TW_FILE}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Mandatory fields list
        mandatory_fields = [
            ('civil_id_number', 'Civil ID Number'),
            ('civil_id_expiry', 'Civil ID Expiry'),
            ('civil_id_file', 'Civil ID File'),
            ('passport_number', 'Passport Number'),
            ('passport_expiry', 'Passport Expiry'),
            ('passport_file', 'Passport File'),
            ('working_permit_expiry', 'Work Permit Expiry'),
            ('work_permit_file', 'Work Permit File'),
            ('driver_license_expiry', 'Driving License Expiry'),
            ('driving_license_file', 'Driving License File'),
            ('health_insurance_expiry', 'Health Card Expiry'),
            ('health_card_file', 'Health Card File'),
            ('vehicle_registration', 'VEHICLE REGISTRATION NUMBER'),
            ('vehicle_registration_expiry', 'VEHICLE REGISTRATION NUMBER EXPIRY'),
            ('vehicle_rc_file', 'Vehicle RC File'),
            ('photo_selfie', 'Photo/Selfie'),
        ]

        # Check each mandatory field
        for field_name, field_label in mandatory_fields:
            value = cleaned_data.get(field_name)
            
            # If it's a file field and we are editing, check if the instance already has a file
            if field_name.endswith('_file') or field_name == 'photo_selfie':
                if not value:
                    if self.instance and self.instance.pk:
                        existing_file = getattr(self.instance, field_name, None)
                        if not existing_file:
                            self.add_error(field_name, f"{field_label} is compulsory.")
                    else:
                        self.add_error(field_name, f"{field_label} is compulsory.")
            else:
                if not value:
                    self.add_error(field_name, f"{field_label} is compulsory.")

        return cleaned_data

    def save(self, commit=True):
        driver = super().save(commit=False)
        email = self.cleaned_data.get('email', '')
        
        if email:
            # Create or update profile
            profile, created = Profile.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': self.cleaned_data.get('full_name', '').split(' ')[0],
                    'last_name': ' '.join(self.cleaned_data.get('full_name', '').split(' ')[1:]),
                    'role': 'driver',
                    'company': driver.company,
                }
            )
            
            if created:
                profile.set_password('driver123')
                profile.save()
            elif not profile.company:
                profile.company = driver.company
                profile.save()

            driver.profile = profile

        if commit:
            driver.save()
        return driver


class DriverReceivingForm(forms.ModelForm):
    class Meta:
        model = DriverReceiving
        fields = ['driver', 'item_type', 'custom_label', 'document', 'received_date']
        widgets = {
            'driver': forms.Select(attrs={'class': TW_SELECT}),
            'item_type': forms.Select(attrs={'class': TW_SELECT, 'x-model': 'itemType'}),
            'custom_label': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Custom Item Name', 'x-show': 'itemType === "custom"'}),
            'document': forms.FileInput(attrs={'class': TW_FILE}),
            'received_date': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
        }



class DriverInvoiceForm(forms.ModelForm):
    class Meta:
        model = DriverInvoice
        fields = ['driver', 'cash', 'main_orders', 'additional_orders', 'hours', 'specified_date']
        widgets = {
            'driver': forms.Select(attrs={'class': TW_SELECT}),
            'cash': forms.NumberInput(attrs={'class': TW_INPUT, 'step': '0.001', 'placeholder': '0.000'}),
            'main_orders': forms.NumberInput(attrs={'class': TW_INPUT, 'placeholder': '0'}),
            'additional_orders': forms.NumberInput(attrs={'class': TW_INPUT, 'placeholder': '0'}),
            'hours': forms.NumberInput(attrs={'class': TW_INPUT, 'step': '0.01', 'placeholder': '0.00'}),
            'specified_date': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
        }


class DeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = [
            'driver', 'employee', 'reason', 'deduction_date',
            'contracting_company', 'contractor_deduction_kd',
            'company_deduction_kd', 'is_installment_plan', 
            'total_installments', 'pdf_proof',
        ]
        widgets = {
            'driver': forms.Select(attrs={'class': TW_SELECT}),
            'employee': forms.Select(attrs={'class': TW_SELECT}),
            'reason': forms.Textarea(attrs={'class': TW_TEXTAREA, 'rows': 3}),
            'deduction_date': forms.DateInput(attrs={'class': TW_DATE, 'type': 'date'}),
            'contracting_company': forms.Select(attrs={'class': TW_SELECT}),
            'contractor_deduction_kd': forms.NumberInput(attrs={'class': TW_INPUT, 'step': '0.001'}),
            'company_deduction_kd': forms.NumberInput(attrs={'class': TW_INPUT, 'step': '0.001'}),
            'pdf_proof': forms.FileInput(attrs={'class': TW_FILE}),
            'is_installment_plan': forms.CheckboxInput(attrs={'class': TW_CHECKBOX}),
            'total_installments': forms.NumberInput(attrs={'class': TW_INPUT, 'min': 1}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('driver') and not cleaned.get('employee'):
            raise forms.ValidationError('At least one of Driver or Employee must be selected.')
        return cleaned


class DeductionInstallmentForm(forms.ModelForm):
    class Meta:
        model = DeductionInstallment
        fields = ['status', 'signature_image']
        widgets = {
            'status': forms.Select(attrs={'class': TW_SELECT}),
            'signature_image': forms.FileInput(attrs={'class': TW_FILE}),
        }


class EmployeeDeductionForm(DeductionForm):
    """Employee version — no employee field, only driver deductions."""
    class Meta(DeductionForm.Meta):
        fields = [
            'driver', 'reason', 'deduction_date',
            'contracting_company', 'contractor_deduction_kd',
            'company_deduction_kd', 'is_installment_plan', 
            'total_installments', 'pdf_proof',
        ]

    def clean(self):
        cleaned = super(forms.ModelForm, self).clean()
        if not cleaned.get('driver'):
            raise forms.ValidationError('Driver must be selected.')
        return cleaned


class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=Profile.objects.all(),
        widget=forms.Select(attrs={'class': TW_SELECT}),
        label='To',
    )

    class Meta:
        model = Message
        fields = ['subject', 'body', 'attachment']
        widgets = {
            'subject': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Subject'}),
            'body': forms.Textarea(attrs={'class': TW_TEXTAREA, 'placeholder': 'Write your message...', 'rows': 5}),
            'attachment': forms.FileInput(attrs={'class': TW_FILE}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': TW_INPUT,
                'placeholder': 'Add a new task...',
            }),
        }

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['user', 'title']
        widgets = {
            'user': forms.Select(attrs={'class': TW_SELECT}),
            'title': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Task description...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow assigning to staff (exclude drivers and superusers maybe)
        self.fields['user'].queryset = Profile.objects.exclude(role='driver').order_by('first_name')
        self.fields['user'].label = "Assign To"

class CompanyFileForm(forms.ModelForm):
    class Meta:
        model = CompanyFile
        fields = ['title', 'file', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'File Title'}),
            'file': forms.FileInput(attrs={'class': TW_FILE}),
            'description': forms.Textarea(attrs={'class': TW_TEXTAREA, 'placeholder': 'Optional description...'}),
            'category': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Category (e.g. Legal, HR)'}),
        }

from .models import SystemSettings

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['brand_name', 'logo', 'max_excel_size_mb', 'max_other_size_mb', 'currency']
        widgets = {
            'brand_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Enter Brand Name'}),
            'logo': forms.FileInput(attrs={'class': TW_FILE}),
            'max_excel_size_mb': forms.NumberInput(attrs={'class': TW_INPUT, 'min': 1}),
            'max_other_size_mb': forms.NumberInput(attrs={'class': TW_INPUT, 'min': 1}),
            'currency': forms.Select(attrs={'class': TW_SELECT}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'max_excel_size_mb', 'max_other_size_mb', 'currency']
        widgets = {
            'name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Company Name'}),
            'logo': forms.FileInput(attrs={'class': TW_FILE}),
            'max_excel_size_mb': forms.NumberInput(attrs={'class': TW_INPUT, 'min': 1}),
            'max_other_size_mb': forms.NumberInput(attrs={'class': TW_INPUT, 'min': 1}),
            'currency': forms.Select(attrs={'class': TW_SELECT}),
        }



POPULAR_EMAIL_DOMAINS = {
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
    'aol.com', 'proton.me', 'protonmail.com', 'zoho.com', 'gmx.com', 
    'yandex.com', 'mail.com', 'live.com', 'msn.com'
}

class CompanyRegistrationForm(forms.Form):
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': TW_INPUT_AUTH, 'placeholder': 'Company Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': TW_INPUT_AUTH, 'placeholder': 'Admin Email Address'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': TW_INPUT_AUTH, 
            'placeholder': 'Password',
            'x-bind:type': "showPass ? 'text' : 'password'",
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': TW_INPUT_AUTH, 
            'placeholder': 'Confirm Password',
            'x-bind:type': "showPass ? 'text' : 'password'",
        })
    )
    logo = forms.ImageField(
        label='Company Logo',
        widget=forms.FileInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 bg-black/40 border border-white/5 rounded-2xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 focus:bg-black/60 transition-all text-sm file:mr-4 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-emerald-500/10 file:text-emerald-400 hover:file:bg-emerald-500/20',
            'accept': 'image/*',
        }),
        required=True
    )
    currency = forms.ChoiceField(
        label='Currency',
        choices=CURRENCY_CHOICES,
        initial='KWD',
        widget=forms.Select(attrs={
            'class': 'w-full pl-12 pr-4 py-4 bg-black/40 border border-white/5 rounded-2xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 focus:bg-black/60 transition-all cursor-pointer',
        }),
        required=True
    )

    def clean_company_name(self):
        name = self.cleaned_data.get('company_name')
        if Company.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A company with this name already exists.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        
        # Restrict domain
        if email:
            parts = email.split('@')
            if len(parts) == 2:
                domain = parts[1].lower()
                if domain not in POPULAR_EMAIL_DOMAINS:
                    raise forms.ValidationError(
                        "Registration is restricted to popular email providers (e.g. Gmail, Yahoo, Outlook, Hotmail, iCloud)."
                    )
            else:
                raise forms.ValidationError("Invalid email address format.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class CompanyVerificationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'owner_name',
            'owner_mobile_number',
            'description',
            'owner_signature',
            'registration_certificate',
            'commercial_certificate',
            'authorized_signature_certificate',
            'authorized_signature_only',
        ]
        widgets = {
            'owner_name': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Enter Owner Name'}),
            'owner_mobile_number': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Enter Owner Mobile Number'}),
            'description': forms.Textarea(attrs={'class': TW_TEXTAREA, 'placeholder': 'Describe About Your Company'}),
            'owner_signature': forms.FileInput(attrs={'class': TW_FILE}),
            'registration_certificate': forms.FileInput(attrs={'class': TW_FILE}),
            'commercial_certificate': forms.FileInput(attrs={'class': TW_FILE}),
            'authorized_signature_certificate': forms.FileInput(attrs={'class': TW_FILE}),
            'authorized_signature_only': forms.FileInput(attrs={'class': TW_FILE}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        mandatory_fields = [
            ('owner_name', 'Owner Name'),
            ('owner_mobile_number', 'Owner Mobile Number'),
            ('description', 'Company Description'),
            ('owner_signature', 'Owner Signature'),
            ('registration_certificate', 'Company Registration Certificate'),
            ('commercial_certificate', 'Company Registered Commercial Certificate'),
            ('authorized_signature_certificate', 'Authorised Signature Certificate'),
            ('authorized_signature_only', 'Authorised Signature Only'),
        ]
        
        for field_name, field_label in mandatory_fields:
            val = cleaned_data.get(field_name)
            if field_name.endswith('_certificate') or field_name in ['authorized_signature_only', 'owner_signature']:
                if not val:
                    if self.instance and self.instance.pk:
                        existing_file = getattr(self.instance, field_name, None)
                        if not existing_file:
                            self.add_error(field_name, f"{field_label} is required.")
                    else:
                        self.add_error(field_name, f"{field_label} is required.")
            else:
                if not val:
                    self.add_error(field_name, f"{field_label} is required.")
                    
        return cleaned_data

