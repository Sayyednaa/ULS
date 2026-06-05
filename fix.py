import os

file_path = r'c:\Users\Abdul\Documents\Ali\Code\ULS\templates\shared\operation_documents.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix input classes
old_class = 'class="w-full px-3 py-2 border border-app-border rounded-xl text-sm focus:ring-2 focus:ring-brand focus:border-brand"'
new_class = 'class="w-full px-3 py-2 border border-app-border bg-gray-50/50 dark:bg-[#1a1a24] text-gray-900 dark:text-white rounded-xl text-sm focus:ring-2 focus:ring-brand focus:border-brand"'
content = content.replace(old_class, new_class)

# Fix textarea
content = content.replace('class="w-full px-3 py-2 border border-app-border rounded-xl text-sm focus:ring-2 focus:ring-brand focus:border-brand"', new_class)

# Fix date inputs that might have different classes
old_class_date = 'class="w-full px-3 py-2 border border-app-border rounded-xl text-sm focus:ring-2 focus:ring-brand focus:border-brand"'
content = content.replace(old_class_date, new_class)

# Fix Select
old_class_select = 'class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand/30 focus:border-brand bg-gray-50/50 dark:bg-[#1a1a24] transition-all duration-200 shadow-sm"'
new_class_select = 'class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-[#1a1a24] text-gray-900 dark:text-white rounded-xl text-sm focus:ring-2 focus:ring-brand/30 focus:border-brand transition-all duration-200 shadow-sm"'
content = content.replace(old_class_select, new_class_select)

# Also fix companyName input text colors
old_comp_name_class = 'class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand/30 focus:border-brand bg-gray-50/50 dark:bg-[#1a1a24] transition-all duration-200 shadow-sm"'
content = content.replace(old_comp_name_class, new_class_select)

# Fix search query input text colors
old_search_class = 'class="w-full pl-9 pr-3 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand/30 focus:border-brand bg-gray-50/50 dark:bg-[#1a1a24] transition-all duration-200 shadow-sm"'
new_search_class = 'class="w-full pl-9 pr-3 py-2.5 border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-[#1a1a24] text-gray-900 dark:text-white rounded-xl text-sm focus:ring-2 focus:ring-brand/30 focus:border-brand transition-all duration-200 shadow-sm"'
content = content.replace(old_search_class, new_search_class)

# 2. Fix placeholders
content = content.replace('placeholder="Yes / نعم"', ':placeholder="t(\'Yes / نعم\')"')
content = content.replace('placeholder="e.g. 50"', ':placeholder="t(\'e.g. 50\')"')
content = content.replace('placeholder="Month 1"', ':placeholder="t(\'Month 1\')"')
content = content.replace('placeholder="Amount 1"', ':placeholder="t(\'Amount 1\')"')
content = content.replace('placeholder="Month 2"', ':placeholder="t(\'Month 2\')"')
content = content.replace('placeholder="Amount 2"', ':placeholder="t(\'Amount 2\')"')
content = content.replace('placeholder="Month 3"', ':placeholder="t(\'Month 3\')"')
content = content.replace('placeholder="Amount 3"', ':placeholder="t(\'Amount 3\')"')
content = content.replace('placeholder="Month 4"', ':placeholder="t(\'Month 4\')"')
content = content.replace('placeholder="Amount 4"', ':placeholder="t(\'Amount 4\')"')

# 3. Fix Warning Levels
content = content.replace('<option value="1">1st Written Warning</option>', '<option value="1" x-text="t(\'1st Written Warning\')"></option>')
content = content.replace('<option value="2">2nd Written Warning</option>', '<option value="2" x-text="t(\'2nd Written Warning\')"></option>')
content = content.replace('<option value="3">3rd Written Warning</option>', '<option value="3" x-text="t(\'3rd Written Warning\')"></option>')

# 4. Preview Section
preview_html = """
            </div>
            
            <!-- Document Preview -->
            <div class="bg-white dark:bg-[#15151e] rounded-2xl p-6 mt-6 border border-gray-100 dark:border-gray-800 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
                <h3 class="text-lg font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                    <svg class="w-5 h-5 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                    <span x-text="t('Live Preview')"></span>
                </h3>
                <div class="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden bg-white relative" style="height: 600px;">
                    <div x-show="isPreviewLoading" class="absolute inset-0 bg-white/80 dark:bg-black/50 z-10 flex items-center justify-center">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div>
                    </div>
                    <iframe x-ref="previewFrame" class="w-full h-full border-0"></iframe>
                </div>
            </div>
"""
content = content.replace('            </div>\n        </div>\n    </div>', preview_html + '\n        </div>\n    </div>')


# Add @input / @change trigger on the wrapper to update preview
wrapper_start = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4"'
new_wrapper_start = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4" @input.debounce.500ms="updatePreview()"'
content = content.replace(wrapper_start, new_wrapper_start)

# Similarly update on select type
content = content.replace('x-model="docType"', 'x-model="docType" @change="updatePreview()"')

# Add isPreviewLoading
content = content.replace("dropdownOpen: false,", "dropdownOpen: false,\n            isPreviewLoading: false,")

# 5. Add updatePreview JS logic
preview_script = """
            async updatePreview() {
                if (!this.selectedDriver || !this.docType) return;
                
                this.isPreviewLoading = true;
                
                const payload = {
                    driver_id: this.selectedDriver.id,
                    doc_type: this.docType,
                    due_date: this.dueDate || null,
                    doc_date: this.docDate,
                    company_name: this.companyName,
                    company_name_ar: this.companyNameAr,
                    model_details: this.modelDetails,
                    model_details_ar: this.modelDetailsAr,
                    serial_number: this.serialNumber,
                    phone_number: this.phoneNumber,
                    car_registration: this.carRegistration,
                    advertising_license: this.advertisingLicense,
                    municipality_permit: this.municipalityPermit,
                    violation_reason: this.violationReason,
                    violation_reason_ar: this.violationReasonAr,
                    deduction_amount: this.deductionAmount,
                    warning_level: this.warningLevel,
                    inst1_month: this.inst1Month,
                    inst1_month_ar: this.inst1MonthAr,
                    inst1_amount: this.inst1Amount,
                    inst2_month: this.inst2Month,
                    inst2_month_ar: this.inst2MonthAr,
                    inst2_amount: this.inst2Amount,
                    inst3_month: this.inst3Month,
                    inst3_month_ar: this.inst3MonthAr,
                    inst3_amount: this.inst3Amount,
                    inst4_month: this.inst4Month,
                    inst4_month_ar: this.inst4MonthAr,
                    inst4_amount: this.inst4Amount,
                    driver_name_ar: this.driverNameAr,
                    car_type: this.carType,
                    car_type_ar: this.carTypeAr,
                    plate_number: this.plateNumber,
                    chassis_number: this.chassisNumber,
                    car_body_damage: this.carBodyDamage,
                    car_tire_damage: this.carTireDamage,
                    car_accessories: this.carAccessories,
                    other_damages: this.otherDamages,
                    other_notes: this.otherNotes,
                    fuel_card: this.fuelCard,
                    nationality: this.nationality,
                    nationality_ar: this.nationalityAr
                };
                
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '{{ csrf_token }}';
                
                try {
                    const response = await fetch("{% url 'preview_operation_document' %}", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify(payload)
                    });
                    
                    if (response.ok) {
                        const html = await response.text();
                        const doc = this.$refs.previewFrame.contentWindow.document;
                        doc.open();
                        doc.write(html);
                        doc.close();
                    }
                } catch(e) {
                    console.error('Preview failed', e);
                } finally {
                    this.isPreviewLoading = false;
                }
            },
"""

content = content.replace("async saveDocument() {", preview_script + "\n            async saveDocument() {")

# Call updatePreview when selecting driver
content = content.replace("this.dropdownOpen = false;", "this.dropdownOpen = false;\n                this.updatePreview();")

# Validation logic
validation_script = """
                if (!this.selectedDriver || !this.docType) {
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
                }
"""

content = content.replace("""                if (!this.selectedDriver || !this.docType) {
                    alert(this.t('Please select a driver and document type'));
                    return;
                }""", validation_script)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML modified successfully.")
