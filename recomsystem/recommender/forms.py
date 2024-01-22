from django import forms
from .models import Rating, GenrePreference, Movie


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.5}),
        }

'''#
def get_unique_genres():
    # Fetch all combined genre strings from the Movie model
    combined_genres = Movie.objects.values_list('genres', flat=True)
    
    # Split each string into individual genres and create a set to remove duplicates
    unique_genres = set(genre for combined in combined_genres for genre in combined.split('|'))
    
    # Sort genres alphabetically if desired
    return sorted(unique_genres)
'''


class GenrePreferenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GenrePreferenceForm, self).__init__(*args, **kwargs)
        # Assuming you have a function to fetch unique genres
        self.fields['genres'] = forms.MultipleChoiceField(
            choices=get_unique_genres(),
            widget=forms.CheckboxSelectMultiple
        )

    class Meta:
        model = GenrePreference
        fields = ['genres']

def get_unique_genres():
    # Fetch all combined genre strings from the Movie model and create a unique set
    combined_genres = Movie.objects.values_list('genres', flat=True)
    unique_genres = set()
    for genres in combined_genres:
        for genre in genres.split('|'):
            unique_genres.add(genre.strip())  # Strip to remove any leading/trailing whitespace

    return [(genre, genre) for genre in sorted(unique_genres)]
class GenrePreferenceForm(forms.ModelForm):
    genres = forms.MultipleChoiceField(
        choices=get_unique_genres(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = GenrePreference
        fields = ['genres']
