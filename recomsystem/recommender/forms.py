from django import forms
from .models import Rating, GenrePreference, Movie


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.5}),
        }



class GenrePreferenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GenrePreferenceForm, self).__init__(*args, **kwargs)
        
        self.fields['genres'] = forms.MultipleChoiceField(
            choices=get_unique_genres(),
            widget=forms.CheckboxSelectMultiple
        )

    class Meta:
        model = GenrePreference
        fields = ['genres']

def get_unique_genres():
    
    combined_genres = Movie.objects.values_list('genres', flat=True)
    unique_genres = set()
    for genres in combined_genres:
        for genre in genres.split('|'):
            unique_genres.add(genre.strip())  

    return [(genre, genre) for genre in sorted(unique_genres)]
class GenrePreferenceForm(forms.ModelForm):
    genres = forms.MultipleChoiceField(
        choices=get_unique_genres(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = GenrePreference
        fields = ['genres']
