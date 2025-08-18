from django.contrib import admin
from .models import (
    Club, ClubMembership, ClubAdmin, Player, Tournament,
    Match, Game, FriendlyGame, Point, Standing, ClubEvent,
    TournamentParticipant, ClubAdminInvite
)


@admin.register(Club)
class ClubAdminPanel(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "club", "is_active")
    list_filter = ("club", "is_active")
    search_fields = ("user__username", "club__name")


@admin.register(ClubAdmin)
class ClubAdminEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "club", "assigned_at")
    search_fields = ("user__username", "club__name")


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "club", "joined_at", "rating", "dominant_hand")
    list_filter = ("club", "dominant_hand")
    search_fields = ("full_name", "club__name")


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "start_date", "tournament_type")
    list_filter = ("club", "tournament_type")
    search_fields = ("name", "club__name")


@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = ("tournament", "player", "seed", "joined_at")
    list_filter = ("tournament",)
    search_fields = ("player__full_name", "tournament__name")


@admin.register(ClubAdminInvite)
class ClubAdminInviteAdmin(admin.ModelAdmin):
    list_display = ("club", "email", "is_active", "created_at", "expires_at", "accepted_at")
    list_filter = ("club", "is_active")
    search_fields = ("email", "club__name")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("tournament", "player1", "player2", "winner", "played_at")
    list_filter = ("tournament",)
    search_fields = ("player1__full_name", "player2__full_name")


@admin.register(FriendlyGame)
class FriendlyGameAdmin(admin.ModelAdmin):
    list_display = ("club", "player1", "player2", "winner", "played_at")
    list_filter = ("club",)
    search_fields = ("player1__full_name", "player2__full_name")


@admin.action(description="Пересчитать счет для выбранных партий")
def recalculate_scores(modeladmin, request, queryset):
    for game in queryset:
        game.recalculate_score()


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("match", "friendly", "created_at", "start_time", "end_time", "score_player1", "score_player2")
    list_filter = ("match", "friendly")
    actions = [recalculate_scores]


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("game", "scored_by", "order", "timestamp")
    list_filter = ("scored_by",)
    search_fields = ("scored_by__full_name",)


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ("tournament", "player", "points", "rank")
    list_filter = ("tournament",)


@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ("title", "club", "date", "created_by")
    list_filter = ("club",)
    search_fields = ("title", "club__name")
