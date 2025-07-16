from django.shortcuts import render
from django.core.files.storage import default_storage
from django.http import HttpResponse
import pandas as pd
import os
from .forms import UploadFileForm

def process_file(file_path):
    df = pd.read_csv(file_path)
    df.columns = [col.strip() for col in df.columns]
    df = df[df['Object Code'].astype(str).str.strip().str.lower() != 'total']

    bu_columns = df.columns[2:]  
    grouped_rows = []

    for bu in bu_columns:
        filtered = df[df[bu].notnull()]  
        for _, row in filtered.iterrows():
            bu_name = bu
            object_code = row['Object Code']
            gl_name = row['GL Name']
            value = row[bu]
            grouped_rows.append([bu_name, object_code, gl_name, value])

    output_df = pd.DataFrame(grouped_rows, columns=["BU name", "Object Code", "GL Name", "BU unit"])
    
    output_file_path = os.path.join('media', 'grouped_output.xlsx')
    output_df.to_excel(output_file_path, index=False)
    return output_file_path

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_path = default_storage.save(f"media/{uploaded_file.name}", uploaded_file)
            output_path = process_file(file_path)

            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=grouped_output.xlsx'
                return response
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
