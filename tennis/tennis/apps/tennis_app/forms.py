from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Электронная почта или имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')



    

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите адрес эл. почты'
        })
    )
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите имя пользователя'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Придумайте пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


from .models import Tournament, ClubEvent, Player, TournamentParticipant, ClubAdminInvite, Match

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        exclude = ['club', 'created_by']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TournamentParticipantForm(forms.ModelForm):
    class Meta:
        model = TournamentParticipant
        fields = ['player', 'seed']

class AdminInviteForm(forms.ModelForm):
    class Meta:
        model = ClubAdminInvite
        fields = ['email']

class AcceptInviteForm(forms.Form):
    token = forms.CharField(max_length=64, label='Токен приглашения')


class TournamentMatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['player1', 'player2']

class ClubEventForm(forms.ModelForm):
    class Meta:
        model = ClubEvent
        exclude = ['club', 'created_by']

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ['club']