# from django.contrib import admin
# from django.urls import path
# from django.conf import settings
# from django.conf.urls.static import static
# from localizationtool.views import localize_files, folder_list, download_folder, delete_folder

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     # This is the URL for the upload form
#     path('', localize_files, name='localize_files'), 
    
#     # New URLs for the folder management
#     path('translations/', folder_list, name='folder_list'),
#     path('translations/download/<str:folder_name>/', download_folder, name='download_folder'),
#     path('translations/delete/<str:folder_name>/', delete_folder, name='delete_folder'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from localizationtool.views import localize_tool_view, download_folder, delete_folder

urlpatterns = [
    path('admin/', admin.site.urls),
    # The main URL now points to the single, unified view
    path('', localize_tool_view, name='localize_tool_view'), 
    
    # Keep these URLs for folder actions, but update the redirect
    path('download/<str:folder_name>/', download_folder, name='download_folder'),
    path('delete/<str:folder_name>/', delete_folder, name='delete_folder'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)