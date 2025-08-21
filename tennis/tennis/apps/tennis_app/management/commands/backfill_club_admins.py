from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tennis_app.models import Club, ClubAdmin, ClubMembership

class Command(BaseCommand):
    help = 'Назначает админов для клубов, где их нет, на базе первого активного участника'

    def handle(self, *args, **options):
        created = 0
        for club in Club.objects.all():
            if not ClubAdmin.objects.filter(club=club).exists():
                membership = ClubMembership.objects.filter(club=club, is_active=True).order_by('id').first()
                if membership:
                    ClubAdmin.objects.get_or_create(club=club, user=membership.user)
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f'Назначен {membership.user} админом клуба {club.name}'))
        self.stdout.write(self.style.NOTICE(f'Готово. Добавлено {created} админов.'))
