from django import forms

class LocalizationForm(forms.Form):
    pot_file = forms.FileField(label="Upload .pot File")
    zip_file = forms.FileField(label="Upload .zip File (optional)", required=False)
    csv_file = forms.FileField(label="Upload Glossary .csv File (optional)", required=False)

    LANG_CHOICES = [
        ('ar', 'Arabic'),
        ('it', 'Italian'),
        ('fr', 'French'),
        ('de', 'German'),
        ('pl', 'Polish'),
        ('pt', 'Portuguese'),
        ('ja', 'Japanese'),
        ('nl', 'Dutch'),
        ('ru', 'Russian'),
        ('es', 'Spanish'),
    ]

    target_languages = forms.MultipleChoiceField(
        label="Select Target Languages",
        choices=LANG_CHOICES,
        widget=forms.CheckboxSelectMultiple,
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
