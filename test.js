
    const driversData = {{ drivers_json|safe }};
    
    function documentGenerator() {
        return {
            initialData: {{ initial_data_json|safe }},
            drivers: driversData,
            searchQuery: '',
            dropdownOpen: false,
            isPreviewLoading: false,
            selectedDriver: null,
            
            docType: 'penalty_deduction',
            companyName: '',
            companyNameAr: '',
            driverNameAr: '',
            
            // Document Form Fields
            docDate: new Date().toISOString().split('T')[0],
            dueDate: '',
            modelDetails: '',
            modelDetailsAr: '',
            carRegistration: '',
            advertisingLicense: '',
            municipalityPermit: '',
            violationReason: '',
            violationReasonAr: '',
            deductionAmount: '',
            warningLevel: '1',
            
            serialNumber: '',
            phoneNumber: '',
            
            carType: '',
            carTypeAr: '',
            plateNumber: '',
            chassisNumber: '',
            carBodyDamage: '',
            carTireDamage: '',
            carAccessories: '',
            otherDamages: '',
            otherNotes: '',
            fuelCard: '',
            nationality: '',
            nationalityAr: '',
            isInstallment: false,
            totalInstallments: 1,
            
            inst1Month: '', inst1MonthAr: '', inst1Amount: '',
            inst2Month: '', inst2MonthAr: '', inst2Amount: '',
            inst3Month: '', inst3MonthAr: '', inst3Amount: '',
            inst4Month: '', inst4MonthAr: '', inst4Amount: '',
            
            get filteredDrivers() {
                if (this.searchQuery === '') return this.drivers;
                const lowerCaseQuery = this.searchQuery.toLowerCase();
                return this.drivers.filter(driver => 
                    driver.full_name.toLowerCase().includes(lowerCaseQuery) ||
                    driver.civil_id.includes(lowerCaseQuery)
                );
            },
            
            init() {
                if (this.initialData) {
                    const mapping = {
                        doc_type: 'docType', due_date: 'dueDate', doc_date: 'docDate',
                        company_name: 'companyName', company_name_ar: 'companyNameAr',
                        model_details: 'modelDetails', model_details_ar: 'modelDetailsAr',
                        serial_number: 'serialNumber', phone_number: 'phoneNumber',
                        car_registration: 'carRegistration', advertising_license: 'advertisingLicense',
                        municipality_permit: 'municipalityPermit', violation_reason: 'violationReason',
                        violation_reason_ar: 'violationReasonAr', deduction_amount: 'deductionAmount',
                        warning_level: 'warningLevel', inst1_month: 'inst1Month', inst1_month_ar: 'inst1MonthAr',
                        inst1_amount: 'inst1Amount', inst2_month: 'inst2Month', inst2_month_ar: 'inst2MonthAr',
                        inst2_amount: 'inst2Amount', inst3_month: 'inst3Month', inst3_month_ar: 'inst3MonthAr',
                        inst3_amount: 'inst3Amount', inst4_month: 'inst4Month', inst4_month_ar: 'inst4MonthAr',
                        inst4_amount: 'inst4Amount', driver_name_ar: 'driverNameAr'
                    };
                    // Pre-fill state from history
                    for (let key in this.initialData) {
                        let mappedKey = mapping[key] || key;
                        if (this.hasOwnProperty(mappedKey)) {
                            this[mappedKey] = this.initialData[key];
                        }
                    }
                    // Select driver
                    if (this.initialData.driver_id) {
                        const drv = this.drivers.find(d => String(d.id) === String(this.initialData.driver_id));
                        if (drv) {
                            this.selectedDriver = drv;
                            this.searchQuery = drv.full_name;
                        }
                    }
                    // Check for print flag
                    if (new URLSearchParams(window.location.search).get('print') === 'true') {
                        setTimeout(() => window.print(), 500);
                    }
                }
            },
            
            async translateText(text) {
                if (!text) return '';
                const dict = {
                    'sayedna': 'سيدنا',
                    'talabat': 'طلبات',
                    'pharma zone': 'فارما زون',
                    'pharmazone': 'فارمازون',
                    'burger king': 'برجر كنج',
                    'burgerking': 'برجر كنج',
                };
                if (dict[text.toLowerCase()]) return dict[text.toLowerCase()];
                
                try {
                    const res = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|ar`);
                    const data = await res.json();
                    if (data && data.responseData && data.responseData.translatedText) {
                        return data.responseData.translatedText;
                    }
                    return text;
                } catch(e) {
                    return text;
                }
            },
            
            toArabicDigits(str) {
                if (!str) return '';
                const id = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
                return str.toString().replace(/[0-9]/g, function(w){
                    return id[+w];
                });
            },
            
            get formattedDate() {
                if (!this.docDate) return '';
                const d = new Date(this.docDate);
                return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
            },
            
            get formattedDateMonth() {
                if (!this.docDate) return '';
                const d = new Date(this.docDate);
                return d.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
            },
            
            get formattedDateAr() {
                if (!this.docDate) return '';
                const d = new Date(this.docDate);
                const enFormat = d.toLocaleDateString('ar-EG', { day: 'numeric', month: 'long', year: 'numeric' });
                return this.toArabicDigits(enFormat);
            },
            
            get formattedDateMonthAr() {
                if (!this.docDate) return '';
                const d = new Date(this.docDate);
                const enFormat = d.toLocaleDateString('ar-EG', { month: 'long', year: 'numeric' });
                return this.toArabicDigits(enFormat);
            },
            
            async selectDriver(driver) {
                this.selectedDriver = driver;
                this.searchQuery = driver.full_name;
                this.companyName = driver.company_name;
                this.dropdownOpen = false;
                this.updatePreview();
                
                // Auto-translate values
                this.driverNameAr = await this.translateText(driver.full_name);
                this.companyNameAr = await this.translateText(driver.company_name);
            },
            
            
            async calculateInstallments() {
                if (this.docType === 'penalty_deduction') {
                    let amt = parseFloat(this.deductionAmount) || 0;
                    let count = this.isInstallment ? parseInt(this.totalInstallments) : 1;
                    let instAmt = (amt / count).toFixed(2);
                    let startDate = new Date(this.docDate || new Date());
                    
                    // Reset all installments
                    this.inst1Month = ''; this.inst1MonthAr = ''; this.inst1Amount = '';
                    this.inst2Month = ''; this.inst2MonthAr = ''; this.inst2Amount = '';
                    this.inst3Month = ''; this.inst3MonthAr = ''; this.inst3Amount = '';
                    this.inst4Month = ''; this.inst4MonthAr = ''; this.inst4Amount = '';
                    
                    for(let i=0; i<count && i<4; i++) {
                        let d = new Date(startDate.getFullYear(), startDate.getMonth() + i + 1, 1);
                        let mEn = d.toLocaleDateString('en-US', {month:'long', year:'numeric'});
                        let mAr = this.toArabicDigits(d.toLocaleDateString('ar-EG', {month:'long', year:'numeric'}));
                        
                        if (i === 0) { this.inst1Month = mEn; this.inst1MonthAr = mAr; this.inst1Amount = instAmt; }
                        else if (i === 1) { this.inst2Month = mEn; this.inst2MonthAr = mAr; this.inst2Amount = instAmt; }
                        else if (i === 2) { this.inst3Month = mEn; this.inst3MonthAr = mAr; this.inst3Amount = instAmt; }
                        else if (i === 3) { this.inst4Month = mEn; this.inst4MonthAr = mAr; this.inst4Amount = instAmt; }
                    }
                }
            },
            
            async updatePreview() {
                if (!this.selectedDriver || !this.docType) return;
                
                this.isPreviewLoading = true;
                
                await this.calculateInstallments();
                
                
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
                    is_installment: this.isInstallment,
                    total_installments: this.totalInstallments,
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

            async saveDocument() {

                if (!this.selectedDriver || !this.docType) {
                    alert(this.t('Please select a driver and document type'));
                    return;
                }
                
                await this.calculateInstallments();
                
                // Check mandatory fields
                if (this.docType !== 'penalty_deduction' && (!this.docDate || !this.dueDate)) { 
                    alert(this.t('Please fill all mandatory fields')); return; 
                } else if (this.docType === 'penalty_deduction' && !this.docDate) {
                    alert(this.t('Please fill all mandatory fields')); return;
                }
                
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

                this.isSaving = true;
                
                // Save document history
                try {
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
                        is_installment: this.isInstallment,
                        total_installments: this.totalInstallments,
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
                    
                    const response = await fetch("{% url 'save_operation_document' %}", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify(payload)
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        alert(this.t('Document saved successfully!'));
                        if (data.history_id) {
                            window.open(`{% url 'print_operation_document' %}?history_id=${data.history_id}&print=true`, '_blank');
                        }
                        window.location.href = "{% url 'operation_documents' %}";
                    } else {
                        try {
                            const errData = await response.json();
                            alert(this.t('Failed to save document. Error: ') + (errData.error || response.statusText));
                        } catch (e) {
                            alert(this.t('Failed to save document. Status: ') + response.status);
                        }
                    }
                } catch(e) {
                    console.error('Failed to save document history', e);
                    alert(this.t('An error occurred while saving.'));
                }
            }
        }
    }
