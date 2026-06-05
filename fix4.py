import os

file_path = r'c:\Users\Abdul\Documents\Ali\Code\ULS\templates\shared\operation_documents.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Current validation block in the file (from fix3.py new_validation)
current_validation = """                if (!this.selectedDriver || !this.docType) {
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

# New target validation (reverted to old, but with dueDate added)
new_validation = """                if (!this.selectedDriver || !this.docType) {
                    alert(this.t('Please select a driver and document type'));
                    return;
                }
                
                // Check mandatory fields
                if (!this.docDate || !this.dueDate) { alert(this.t('Please fill all mandatory fields')); return; }
                
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

# A small sanity check: if the user's instructions "make this field manadatory only:Duration / Due Date whereever forms its present in operations docs section. and make other as they was previously" means EXACTLY what I'm writing.

content = content.replace(current_validation, new_validation)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Validation updated.")
