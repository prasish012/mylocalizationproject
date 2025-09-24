# import os
# import shutil
# import datetime
# from django.shortcuts import render, redirect
# from django.http import FileResponse, Http404
# from django.core.files.storage import FileSystemStorage
# from django.urls import reverse
# from django.conf import settings
# from django.contrib import messages  # Import the messages framework
# from .forms import LocalizationForm
# from .localization_logic import ColabLocalizationTool

# # The main view to handle file uploads and start the localization process
# def localize_files(request):
#     if request.method == 'POST':
#         form = LocalizationForm(request.POST, request.FILES)
#         if form.is_valid():
#             pot_file = form.cleaned_data['pot_file']
#             zip_file = form.cleaned_data['zip_file']
#             csv_file = form.cleaned_data['csv_file']
#             target_langs = form.cleaned_data['target_languages']

#             # Step 1: Get the text domain and create a timestamped folder
#             text_domain = os.path.splitext(pot_file.name)[0].split('.')[0]
#             # Updated timestamp format for better readability
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#             folder_name = f"{text_domain}"
            
#             # Define the base directory for translations
#             translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#             new_dir_path = os.path.join(translations_root, folder_name)

#             os.makedirs(new_dir_path, exist_ok=True)

#             # Save uploaded files temporarily to process them
#             fs = FileSystemStorage(location=new_dir_path)
#             pot_file_path = fs.save(pot_file.name, pot_file)
#             zip_file_path = fs.save(zip_file.name, zip_file) if zip_file else None
#             csv_file_path = fs.save(csv_file.name, csv_file) if csv_file else None

#             # Step 2: Use your localization logic to generate files in the new folder
#             tool = ColabLocalizationTool()
#             # The run method is modified to take the output directory as an argument
#             tool.run(
#                 os.path.join(new_dir_path, pot_file_path),
#                 os.path.join(new_dir_path, zip_file_path) if zip_file_path else None,
#                 os.path.join(new_dir_path, csv_file_path) if csv_file_path else None,
#                 target_langs,
#                 new_dir_path
#             )

#             # Clean up the temporary uploaded files from inside the folder,
#             # but leave the generated .po and .mo files
#             os.remove(os.path.join(new_dir_path, pot_file.name))
#             if zip_file: os.remove(os.path.join(new_dir_path, zip_file.name))
#             if csv_file: os.remove(os.path.join(new_dir_path, csv_file.name))
            
#             # Add a success message and redirect back to the form page
#             messages.success(request, 'Translation process is complete! You can view the files by clicking on the "View Translated Files" button.')
#             return redirect('localize_files')
#     else:
#         form = LocalizationForm()
#     return render(request, 'localizationtool/form.html', {'form': form})

# # New view to list all translation folders
# def folder_list(request):
#     translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#     if not os.path.isdir(translations_root):
#         folders = []
#     else:
#         folders = [d for d in os.listdir(translations_root) if os.path.isdir(os.path.join(translations_root, d))]
    
#     folder_data = [{'id': i + 1, 'name': folder} for i, folder in enumerate(folders)]
#     return render(request, 'localizationtool/folder_list.html', {'folders': folder_data})

# # New view to download a folder as a ZIP file
# def download_folder(request, folder_name):
#     translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#     folder_path = os.path.join(translations_root, folder_name)
    
#     if not os.path.isdir(folder_path):
#         raise Http404("Folder not found.")
    
#     zip_path = shutil.make_archive(
#         base_name=os.path.join(settings.BASE_DIR, 'temp', folder_name),
#         format='zip',
#         root_dir=translations_root,
#         base_dir=folder_name
#     )
    
#     response = FileResponse(open(zip_path, 'rb'), as_attachment=True, filename=f"{folder_name}.zip")
#     response['Content-Length'] = os.path.getsize(zip_path)
#     os.remove(zip_path)

#     return response

# # New view to delete a folder
# def delete_folder(request, folder_name):
#     if request.method == 'POST':
#         translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#         folder_path = os.path.join(translations_root, folder_name)
        
#         if os.path.isdir(folder_path):
#             shutil.rmtree(folder_path)
            
#     return redirect('folder_list')

# import os
# import shutil
# import datetime
# from django.shortcuts import render, redirect
# from django.http import FileResponse, Http404
# from django.core.files.storage import FileSystemStorage
# from django.urls import reverse
# from django.conf import settings
# from django.contrib import messages
# from .forms import LocalizationForm
# from .localization_logic import ColabLocalizationTool

# # The main view to handle file uploads and start the localization process
# def localize_files(request):
#     if request.method == 'POST':
#         form = LocalizationForm(request.POST, request.FILES)
#         if form.is_valid():
#             pot_file = form.cleaned_data['pot_file']
#             zip_file = form.cleaned_data['zip_file']
#             csv_file = form.cleaned_data['csv_file']
#             target_langs = form.cleaned_data['target_languages']

#             # Step 1: Get the text domain and define the folder name
#             text_domain = os.path.splitext(pot_file.name)[0].split('.')[0]
#             folder_name = f"{text_domain}"
            
#             # Define the base directory for translations
#             translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#             new_dir_path = os.path.join(translations_root, folder_name)

#             os.makedirs(new_dir_path, exist_ok=True)

#             # Save uploaded files temporarily to process them
#             fs = FileSystemStorage(location=new_dir_path)
#             pot_file_path = fs.save(pot_file.name, pot_file)
#             zip_file_path = fs.save(zip_file.name, zip_file) if zip_file else None
#             csv_file_path = fs.save(csv_file.name, csv_file) if csv_file else None

#             # Step 2: Use your localization logic to generate files in the new folder
#             tool = ColabLocalizationTool()
#             tool.run(
#                 os.path.join(new_dir_path, pot_file_path),
#                 os.path.join(new_dir_path, zip_file_path) if zip_file_path else None,
#                 os.path.join(new_dir_path, csv_file_path) if csv_file_path else None,
#                 target_langs,
#                 new_dir_path
#             )

#             # Clean up the temporary uploaded files
#             os.remove(os.path.join(new_dir_path, pot_file.name))
#             if zip_file: os.remove(os.path.join(new_dir_path, zip_file.name))
#             if csv_file: os.remove(os.path.join(new_dir_path, csv_file.name))
            
#             # Add a success message and redirect back to the form page
#             messages.success(request, 'Translation process is complete! You can view the files by clicking on the "View Translated Files" button.')
#             return redirect('localize_files')
#     else:
#         form = LocalizationForm()
#     return render(request, 'localizationtool/form.html', {'form': form})

# # New view to list all translation folders
# def folder_list(request):
#     translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#     if not os.path.isdir(translations_root):
#         folders = []
#     else:
#         folders = [d for d in os.listdir(translations_root) if os.path.isdir(os.path.join(translations_root, d))]
    
#     folder_data = [{'id': i + 1, 'name': folder} for i, folder in enumerate(folders)]
#     return render(request, 'localizationtool/folder_list.html', {'folders': folder_data})

# # New view to download a folder as a ZIP file
# def download_folder(request, folder_name):
#     translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#     folder_path = os.path.join(translations_root, folder_name)
    
#     if not os.path.isdir(folder_path):
#         raise Http404("Folder not found.")
    
#     zip_path = shutil.make_archive(
#         base_name=os.path.join(settings.BASE_DIR, 'temp', folder_name),
#         format='zip',
#         root_dir=translations_root,
#         base_dir=folder_name
#     )
    
#     response = FileResponse(open(zip_path, 'rb'), as_attachment=True, filename=f"{folder_name}.zip")
#     response['Content-Length'] = os.path.getsize(zip_path)
#     os.remove(zip_path)

#     return response

# # New view to delete a folder
# def delete_folder(request, folder_name):
#     if request.method == 'POST':
#         translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#         folder_path = os.path.join(translations_root, folder_name)
        
#         if os.path.isdir(folder_path):
#             shutil.rmtree(folder_path)
            
#     return redirect('folder_list')



# import os
# import shutil
# import datetime
# from django.shortcuts import render, redirect
# from django.http import FileResponse, Http404
# from django.core.files.storage import FileSystemStorage
# from django.urls import reverse
# from django.conf import settings
# from django.contrib import messages
# from .forms import LocalizationForm
# from .localization_logic import ColabLocalizationTool

# # The unified view to handle everything
# def localize_tool_view(request):
#     """
#     Handles file uploads, runs localization, and displays the list of translated folders
#     on a single page.
#     """
#     # 1. Handle POST request for form submission
#     if request.method == 'POST':
#         form = LocalizationForm(request.POST, request.FILES)
#         if form.is_valid():
#             pot_file = form.cleaned_data['pot_file']
#             zip_file = form.cleaned_data['zip_file']
#             csv_file = form.cleaned_data['csv_file']
#             target_langs = form.cleaned_data['target_languages']

#             # Step 1: Get the text domain and define the folder name
#             text_domain = os.path.splitext(pot_file.name)[0].split('.')[0]
#             folder_name = f"{text_domain}"
            
#             # Define the base directory for translations
#             translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#             new_dir_path = os.path.join(translations_root, folder_name)

#             os.makedirs(new_dir_path, exist_ok=True)

#             # Save uploaded files temporarily to process them
#             fs = FileSystemStorage(location=new_dir_path)
#             pot_file_path = fs.save(pot_file.name, pot_file)
#             zip_file_path = fs.save(zip_file.name, zip_file) if zip_file else None
#             csv_file_path = fs.save(csv_file.name, csv_file) if csv_file else None

#             # Step 2: Use your localization logic to generate files in the new folder
#             tool = ColabLocalizationTool()
#             tool.run(
#                 os.path.join(new_dir_path, pot_file_path),
#                 os.path.join(new_dir_path, zip_file_path) if zip_file_path else None,
#                 os.path.join(new_dir_path, csv_file_path) if csv_file_path else None,
#                 target_langs,
#                 new_dir_path
#             )

#             # Clean up the temporary uploaded files
#             os.remove(os.path.join(new_dir_path, pot_file.name))
#             if zip_file: os.remove(os.path.join(new_dir_path, zip_file.name))
#             if csv_file: os.remove(os.path.join(new_dir_path, csv_file.name))
            
#             # Add a success message and redirect back to the same page
#             messages.success(request, 'Translation process is complete! You can view the files in the table below.')
#             return redirect('localize_tool_view')
#     else:
#         form = LocalizationForm()
        
#     # 2. Retrieve the list of folders (for both GET and POST requests)
#     translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#     if not os.path.isdir(translations_root):
#         folders = []
#     else:
#         folders = [d for d in os.listdir(translations_root) if os.path.isdir(os.path.join(translations_root, d))]
    
#     folder_data = [{'id': i + 1, 'name': folder} for i, folder in enumerate(folders)]

#     # 3. Render the single, combined template with all context
#     context = {
#         'form': form,
#         'folders': folder_data,
#     }
#     return render(request, 'localizationtool/combined_view.html', context)

# # Keep these views as they are because they handle separate actions (download, delete)
# def download_folder(request, folder_name):
#     translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#     folder_path = os.path.join(translations_root, folder_name)
#     if not os.path.isdir(folder_path):
#         raise Http404("Folder not found.")
#     zip_path = shutil.make_archive(
#         base_name=os.path.join(settings.BASE_DIR, 'temp', folder_name),
#         format='zip',
#         root_dir=translations_root,
#         base_dir=folder_name
#     )
#     response = FileResponse(open(zip_path, 'rb'), as_attachment=True, filename=f"{folder_name}.zip")
#     response['Content-Length'] = os.path.getsize(zip_path)
#     os.remove(zip_path)
#     return response

# def delete_folder(request, folder_name):
#     if request.method == 'POST':
#         translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
#         folder_path = os.path.join(translations_root, folder_name)
#         if os.path.isdir(folder_path):
#             shutil.rmtree(folder_path)
#         messages.success(request, f'Folder "{folder_name}" has been deleted.')
#     # Redirect to the main view to show the updated list
#     return redirect('localize_tool_view')


import os
import shutil
from django.shortcuts import render, redirect
from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib import messages
from .forms import LocalizationForm
from .localization_logic import ColabLocalizationTool


def localize_tool_view(request):
    """
    Handles file uploads, runs localization, and displays the list of translated folders
    on a single page.
    """
    if request.method == 'POST':
        form = LocalizationForm(request.POST, request.FILES)
        if form.is_valid():
            # Use .get() to safely retrieve files. This prevents KeyErrors if a file is not uploaded.
            pot_file = form.cleaned_data.get('upload_po_file')
            zip_file = form.cleaned_data.get('upload_zip_file')
            glossary_file = form.cleaned_data.get('upload_glossary_file')
            target_languages = form.cleaned_data['target_languages']

            # Ensure a .po or .pot file is uploaded
            if not pot_file:
                messages.error(request, 'Please upload a .po or .pot file to translate.')
                return redirect('localize_tool_view')

            # Step 1: Get text domain and define project folder
            text_domain = os.path.splitext(pot_file.name)[0].split('.')[0]
            folder_name = f"{text_domain}"

            translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
            new_dir_path = os.path.join(translations_root, folder_name)
            os.makedirs(new_dir_path, exist_ok=True)

            # Step 2: Save uploaded files manually
            pot_save_path = os.path.join(new_dir_path, pot_file.name)
            with open(pot_save_path, 'wb+') as dest:
                for chunk in pot_file.chunks():
                    dest.write(chunk)

            zip_save_path = None
            if zip_file:
                zip_save_path = os.path.join(new_dir_path, zip_file.name)
                with open(zip_save_path, 'wb+') as dest:
                    for chunk in zip_file.chunks():
                        dest.write(chunk)

            glossary_save_path = None
            if glossary_file:
                glossary_save_path = os.path.join(new_dir_path, glossary_file.name)
                with open(glossary_save_path, 'wb+') as dest:
                    for chunk in glossary_file.chunks():
                        dest.write(chunk)

            # Step 3: Run localization tool
            tool = ColabLocalizationTool()
            tool.run(
                pot_save_path,
                zip_save_path,
                glossary_save_path,
                target_languages,
                new_dir_path
            )

            messages.success(
                request,
                'Translation process is complete! You can view the files in the table below.'
            )
            return redirect('localize_tool_view')
    else:
        form = LocalizationForm()

    # Step 4: Retrieve list of folders
    translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
    if not os.path.isdir(translations_root):
        folders = []
    else:
        folders = [
            d for d in os.listdir(translations_root)
            if os.path.isdir(os.path.join(translations_root, d))
        ]

    folder_data = [{'id': i + 1, 'name': folder} for i, folder in enumerate(folders)]

    context = {
        'form': form,
        'folders': folder_data,
    }
    return render(request, 'localizationtool/combined_view.html', context)


def download_folder(request, folder_name):
    translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
    folder_path = os.path.join(translations_root, folder_name)
    if not os.path.isdir(folder_path):
        raise Http404("Folder not found.")

    temp_dir = os.path.join(settings.BASE_DIR, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    zip_path = shutil.make_archive(
        base_name=os.path.join(temp_dir, folder_name),
        format='zip',
        root_dir=translations_root,
        base_dir=folder_name
    )

    response = FileResponse(
        open(zip_path, 'rb'),
        as_attachment=True,
        filename=f"{folder_name}.zip"
    )
    response['Content-Length'] = os.path.getsize(zip_path)

    os.remove(zip_path)
    return response


def delete_folder(request, folder_name):
    if request.method == 'POST':
        translations_root = os.path.join(settings.MEDIA_ROOT, 'translations')
        folder_path = os.path.join(translations_root, folder_name)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        messages.success(request, f'Folder "{folder_name}" has been deleted.')
    return redirect('localize_tool_view')