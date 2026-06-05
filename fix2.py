import os

file_path = r'c:\Users\Abdul\Documents\Ali\Code\ULS\templates\shared\operation_documents.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

preview_html = """            <!-- Document Preview -->
            <div class="bg-white dark:bg-[#15151e] rounded-2xl p-6 mt-6 border border-gray-100 dark:border-gray-800 shadow-[0_8px_30px_rgb(0,0,0,0.04)] w-full">
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
            </div>"""

# Find all occurrences of the preview block and remove them
start_marker = "<!-- Document Preview -->"
end_marker = "</iframe>\n                </div>\n            </div>"

while start_marker in content:
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)
    # also remove leading whitespace before start_marker
    ws_start = start_idx
    while ws_start > 0 and content[ws_start-1] in (' ', '\t', '\n', '\r'):
        ws_start -= 1
    content = content[:ws_start] + content[end_idx:]

# Now we have no preview sections.
# We want to insert it ABOVE the History Section.
# Let's find <!-- History Section -->
history_marker = "<!-- History Section -->"
if history_marker in content:
    content = content.replace(history_marker, preview_html + "\n\n" + history_marker)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Layout fixed successfully.")
