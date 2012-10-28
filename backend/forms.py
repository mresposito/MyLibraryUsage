from django import forms

class LibraryForm(forms.Form):
  library  = forms.FileField(
      label="Upload you iTunes library"
      )
