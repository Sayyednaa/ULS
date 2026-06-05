import sys

with open('templates/shared/operation_documents.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'id="printable-area"' in line:
        start_idx = i
    if start_idx != -1 and '<!-- History Section -->' in line:
        end_idx = i - 3
        break

if start_idx != -1 and end_idx != -1:
    printable_area_lines = lines[start_idx:end_idx]
    with open('templates/shared/partials/operation_document_printable_area.html', 'w', encoding='utf-8') as f:
        f.writelines(printable_area_lines)
    
    new_lines = lines[:start_idx] + ['        {% include "shared/partials/operation_document_printable_area.html" %}\n'] + lines[end_idx:]
    with open('templates/shared/operation_documents.html', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print('Successfully extracted printable area.')
else:
    print(f'Failed to find boundaries. start: {start_idx}, end: {end_idx}')
