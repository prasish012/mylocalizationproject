from django import forms

class LocalizationForm(forms.Form):
    upload_po_file = forms.FileField(label='Upload .po File:', required=False)
    upload_zip_file = forms.FileField(label='Upload .zip File (optional):', required=False)
    upload_glossary_file = forms.FileField(label='Upload Glossary .csv File (optional):', required=False)

    LANGUAGES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('de', 'German'),
        ('fr', 'French'),
        ('pt', 'Portuguese'),
        ('hi', 'Hindi'),
        ('ne', 'Nepali'),
        ('ar', 'Arabic'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('pl', 'Polish'),
        ('ru', 'Russian'),
        ('nl', 'Dutch'),
    ]

    target_languages = forms.MultipleChoiceField(
        choices=LANGUAGES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )


# from django import forms

# class LocalizationForm(forms.Form):
#     pot_file = forms.FileField(label="Upload .pot File")
#     zip_file = forms.FileField(label="Upload .zip File (optional)", required=False)
#     csv_file = forms.FileField(label="Upload Glossary .csv File (optional)", required=False)

#     LANG_CHOICES = [
#         ('ar', 'Arabic'),
#         ('it', 'Italian'),
#         ('fr', 'French'),
#         ('de', 'German'),
#         ('pl', 'Polish'),
#         ('pt', 'Portuguese'),
#         ('ja', 'Japanese'),
#         ('nl', 'Dutch'),
#         ('ru', 'Russian'),
#         ('es', 'Spanish'),
#     ]

#     target_languages = forms.MultipleChoiceField(
#         label="Select Target Languages",
#         choices=LANG_CHOICES,
#         widget=forms.CheckboxSelectMultiple,
#     )
