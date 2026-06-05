import os

file_path = r'c:\Users\Abdul\Documents\Ali\Code\ULS\templates\shared\operation_documents.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the orange gradient line
content = content.replace(
    'bg-gradient-to-r from-[#f97316] to-[#fbcfe8]',
    'bg-brand'
)

# Fix the save button
old_button = 'bg-gradient-to-r from-[#f97316] to-[#ea580c] hover:from-[#ea580c] hover:to-[#c2410c] text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-300 shadow-[0_8px_20px_-6px_rgba(249,115,22,0.6)] transform hover:-translate-y-0.5'
new_button = 'bg-brand hover:brightness-110 text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-300 shadow-md transform hover:-translate-y-0.5'
content = content.replace(old_button, new_button)

# Fix hover:bg-orange-50 for driver dropdown
content = content.replace('hover:bg-orange-50 ', 'hover:bg-brand/10 ')

# Fix hover:bg-orange-50/50 for history table rows
content = content.replace('hover:bg-orange-50/50 ', 'hover:bg-brand/5 ')

# Fix mandatory validation logic
old_validation = """                if (!this.selectedDriver || !this.docType) {
                    alert(this.t('Please select a driver and document type'));
                    return;
                }
                
                // Check mandatory fields
                if (!this.docDate) { alert(this.t('Please fill all mandatory fields')); return; }
                
                if (this.docType === 'deliver_pledge' || this.docType === 'mobile_receiving') {
                    if (!this.modelDetails || !this.serialNumber || !this.phoneNumber) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'ack_receipt') {
                    if (!this.carType || !this.modelDetails || !this.plateNumber || !this.carRegistration || !this.advertisingLicense || !this.municipalityPermit) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'car_receipt') {
                    if (!this.nationality || !this.carType || !this.modelDetails || !this.plateNumber || !this.chassisNumber || !this.carBodyDamage || !this.carTireDamage || !this.carAccessories || !this.otherDamages || !this.otherNotes || !this.fuelCard) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'warning_letter' || this.docType === 'penalty_deduction') {
                    if (!this.violationReason) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'penalty_deduction') {
                    if (!this.deductionAmount) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'warning_letter') {
                    if (!this.warningLevel) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }"""

new_validation = """                if (!this.selectedDriver || !this.docType) {
                    alert(this.t('Please select a driver and document type'));
                    return;
                }
                
                if (!this.companyName) {
                    alert(this.t('Company Name is mandatory.')); return;
                }
                
                // Check mandatory fields
                if (!this.docDate || !this.dueDate) { alert(this.t('Please fill all mandatory fields (Date and Due Date)')); return; }
                
                if (this.docType === 'deliver_pledge' || this.docType === 'mobile_receiving') {
                    if (!this.modelDetails || !this.serialNumber || !this.phoneNumber) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'ack_receipt') {
                    if (!this.carType || !this.modelDetails || !this.plateNumber || !this.carRegistration || !this.advertisingLicense || !this.municipalityPermit) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'car_receipt') {
                    if (!this.nationality || !this.carType || !this.modelDetails || !this.plateNumber || !this.chassisNumber || !this.carBodyDamage || !this.carTireDamage || !this.carAccessories || !this.otherDamages || !this.otherNotes || !this.fuelCard) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'warning_letter' || this.docType === 'penalty_deduction') {
                    if (!this.violationReason) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }
                if (this.docType === 'penalty_deduction') {
                    if (!this.deductionAmount || !this.inst1Month || !this.inst1Amount || !this.inst2Month || !this.inst2Amount || !this.inst3Month || !this.inst3Amount || !this.inst4Month || !this.inst4Amount) {
                        alert(this.t('Please fill all mandatory fields including all installments')); return;
                    }
                }
                if (this.docType === 'warning_letter') {
                    if (!this.warningLevel) {
                        alert(this.t('Please fill all mandatory fields')); return;
                    }
                }"""

content = content.replace(old_validation, new_validation)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Theme and validation updated successfully.")
