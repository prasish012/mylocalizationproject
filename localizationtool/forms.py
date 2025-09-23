from django import forms

class LocalizationForm(forms.Form):
    upload_po_file = forms.FileField(label='Upload .po File:', required=False)
    upload_zip_file = forms.FileField(label='Upload .zip File (optional):', required=False)
    upload_glossary_file = forms.FileField(label='Upload Glossary .csv File (optional):', required=False)

    LANGUAGES = [
        ('en-us', 'American English'),
        ('en-gb', 'British English'),
        ('en-ca', 'Canadian English'),
        ('en-au', 'Australian English'),
        ('es', 'Spanish'),
        ('es-es', 'Spanish (Spain)'),
        ('es-mx', 'Spanish (Mexico)'),
        ('es-ar', 'Spanish (Argentina)'),
        ('de', 'German'),
        ('de-de', 'German (Germany)'),
        ('de-at', 'German (Austria)'),
        ('de-ch', 'German (Switzerland)'),
        ('fr', 'French'),
        ('fr-fr', 'French (France)'),
        ('fr-ca', 'French (Canada)'),
        ('fr-be', 'French (Belgium)'),
        ('pt', 'Portuguese'),
        ('pt-br', 'Portuguese (Brazil)'),
        ('pt-pt', 'Portuguese (Portugal)'),
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
