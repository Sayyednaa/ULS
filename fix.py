import os

def fix_talabat():
    with open('templates/accountant_portal/talabat.html', 'r', encoding='utf-8') as f:
        t_html = f.read()

    # 1. Modify the form
    t_html = t_html.replace(
        '<form method="post" action="{% url \'accountant_talabat\' %}" enctype="multipart/form-data" class="space-y-6">',
        '<form method="post" action="{% url \'accountant_talabat\' %}" enctype="multipart/form-data" class="space-y-6" @submit.prevent="openSignatureModal()" id="salaryForm">'
    )

    # 2. Add hidden inputs after csrf
    t_html = t_html.replace(
        '{% csrf_token %}',
        '{% csrf_token %}\n            <input type="hidden" name="installment_id" x-model="installmentId">\n            <input type="hidden" name="signature_data" id="signature_data">'
    )

    # 3. Add driver change event
    t_html = t_html.replace(
        '<select name="driver_id" x-model="selectedDriverId" @change="updateDriverDetails" class="w-full',
        '<select name="driver_id" x-model="selectedDriverId" @change="updateDriverDetails($event); checkPendingDeduction()" class="w-full'
    )

    # 4. Add month change event
    t_html = t_html.replace(
        '<input type="month" name="month" class="w-full',
        '<input type="month" name="month" x-model="month" @change="checkPendingDeduction()" class="w-full'
    )

    # 5. Add Deduction binding
    t_html = t_html.replace(
        '<input type="number" step="0.001" name="deduction" class="w-full',
        '<input type="number" step="0.001" name="deduction" x-model.number="deduction" class="w-full'
    )

    # 6. Add Signature Modal (INSIDE the x-data div)
    modal = '''
    <!-- Signature Modal -->
    <div id="signatureModal" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="bg-gray-900 border border-white/10 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl">
            <div class="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                <h2 class="text-xl font-bold text-white" x-text="t('Digital Signature Required')"></h2>
                <button type="button" @click="closeSignatureModal()" class="text-gray-400 hover:text-white">✕</button>
            </div>
            <div class="p-6 space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-2">
                        <label class="text-sm font-medium text-gray-300" x-text="t('Digital Signature')"></label>
                        <div class="relative bg-white rounded-xl border border-gray-700 overflow-hidden" style="height: 200px;">
                            <canvas id="signaturePad" class="w-full h-full cursor-crosshair"></canvas>
                            <button type="button" onclick="clearSignature()" class="absolute top-2 right-2 px-2 py-1 bg-gray-200 hover:bg-gray-300 text-gray-800 text-xs rounded border border-gray-400">Clear</button>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <label class="text-sm font-medium text-gray-300" x-text="t('Or Upload Signature Image')"></label>
                        <div class="h-[200px] flex flex-col items-center justify-center border-2 border-dashed border-gray-700 rounded-xl hover:border-emerald-500 transition-colors cursor-pointer group relative bg-gray-800/30">
                            <input type="file" name="signature_image" form="salaryForm" class="absolute inset-0 opacity-0 cursor-pointer">
                            <span class="text-xs text-gray-400" x-text="t('Click to upload image')"></span>
                        </div>
                    </div>
                </div>
                <div class="flex justify-end pt-4">
                    <button type="button" @click="submitForm()" class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl transition-all" x-text="t('Confirm & Save')"></button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    # Replace the end of block (the original closing div)
    t_html = t_html.replace('</div>\n{% endblock %}', modal)

    # 7. Add Alpine JS Methods
    methods = '''
            installmentId: '',
            month: '',
            
            checkPendingDeduction() {
                if (!this.selectedDriverId || !this.month) return;
                fetch(`/accountant-portal/api/check-pending-deduction/?driver_id=${this.selectedDriverId}&month=${this.month}`)
                .then(res => res.json())
                .then(data => {
                    if (data.amount > 0) {
                        this.deduction = data.amount;
                        this.installmentId = data.installment_id;
                    } else {
                        this.deduction = 0;
                        this.installmentId = '';
                    }
                });
            },
            
            openSignatureModal() {
                document.getElementById('signatureModal').classList.remove('hidden');
                setTimeout(() => {
                    if(typeof resizeCanvas === 'function') resizeCanvas();
                }, 100);
            },
            
            closeSignatureModal() {
                document.getElementById('signatureModal').classList.add('hidden');
            },
            
            submitForm() {
                document.getElementById('salaryForm').submit();
            },
'''
    t_html = t_html.replace('driverId: \'\',', 'driverId: \'\',' + methods)

    # 8. Add vanilla signature JS
    signature_js = '''
<script>
    let canvas, ctx, drawing = false;
    document.addEventListener('DOMContentLoaded', () => {
        canvas = document.getElementById('signaturePad');
        if(!canvas) return;
        ctx = canvas.getContext('2d');
        window.resizeCanvas = function() {
            const ratio = Math.max(window.devicePixelRatio || 1, 1);
            canvas.width = canvas.offsetWidth * ratio;
            canvas.height = canvas.offsetHeight * ratio;
            ctx.scale(ratio, ratio);
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
        };
        
        function startDrawing(e) { drawing = true; draw(e); }
        function stopDrawing() { drawing = false; ctx.beginPath(); document.getElementById('signature_data').value = canvas.toDataURL(); }
        function draw(e) {
            if (!drawing) return;
            const rect = canvas.getBoundingClientRect();
            const x = (e.clientX || (e.touches && e.touches[0].clientX)) - rect.left;
            const y = (e.clientY || (e.touches && e.touches[0].clientY)) - rect.top;
            ctx.lineTo(x, y); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x, y);
        }
        
        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('touchstart', (e) => { e.preventDefault(); startDrawing(e); }, {passive: false});
        canvas.addEventListener('touchmove', (e) => { e.preventDefault(); draw(e); }, {passive: false});
        canvas.addEventListener('touchend', stopDrawing);
        
        window.clearSignature = function() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            document.getElementById('signature_data').value = '';
        };
    });
</script>
{% endblock %}
'''
    t_html = t_html.replace('</script>\n{% endblock %}', '</script>\n' + signature_js)

    with open('templates/accountant_portal/talabat.html', 'w', encoding='utf-8') as f:
        f.write(t_html)

def fix_contract():
    with open('templates/accountant_portal/contract_salary.html', 'r', encoding='utf-8') as f:
        c_html = f.read()

    # Move the modal inside the x-data scope:
    # 1. find the end block
    # 2. remove the closing div that was above the modal
    
    # We will just replace "    </div>\n</div>\n\n<!-- Signature Modal -->"
    # with "    <!-- Signature Modal -->"
    # and then replace "{% endblock %}" with "    </div>\n</div>\n{% endblock %}"
    
    c_html = c_html.replace(
        '    </div>\n</div>\n\n<!-- Signature Modal -->',
        '    <!-- Signature Modal -->'
    )
    
    c_html = c_html.replace(
        '</div>\n{% endblock %}',
        '</div>\n    </div>\n</div>\n{% endblock %}'
    )

    with open('templates/accountant_portal/contract_salary.html', 'w', encoding='utf-8') as f:
        f.write(c_html)

fix_talabat()
fix_contract()
