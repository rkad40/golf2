from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.http import HttpResponse
from .models import Team, TeamAccess, Course, Hole, Tournament, Cache, Award, History, Player
from .util import update_team_scores
import csv
import datetime
import random
import ru

from .forms import TournamentAdminForm
from .util import create_random_password

from django_summernote.utils import get_attachment_model
from django.utils import timezone

try:
    admin.site.unregister(get_attachment_model())
except NotRegistered:
    pass

admin.site.site_header = 'Rockne Invitational Golf Tournament'
admin.site.index_title = 'Admin Dashboard'
admin.site.site_title = 'Site Administration'

def get_queryset_data(meta, queryset):
    opts = meta
    data = []
    fields = [field for field in opts.get_fields() \
        if not field.many_to_many and not field.one_to_many]
    for obj in queryset:
        row = {}
        for field in fields:
            value = getattr(obj, field.name)
            if value is None or isinstance(value, (int, bool, str, float)):
                pass
            elif field.many_to_one:
                value = dict(model=ru.stype(value), id=value.id, value=str(value))
            elif isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                raise Exception(f'Invalid export type "{type(value)}".')
            row[field.name] = value
        data.append(row)
    return data

def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}Data.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response) #, delimiter='\t')
    fields = [field for field in opts.get_fields() \
        if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'

def export_to_json(modeladmin, request, queryset):
    import json
    data = get_queryset_data(modeladmin.model._meta, queryset)
    content_disposition = f'attachment; filename={modeladmin.model._meta.object_name}.json'
    txt = json.dumps(data, indent=2)
    response = HttpResponse(txt, content_type="text/json")
    response['Content-Disposition'] = content_disposition
    return response
export_to_json.short_description = 'Export to JSON'

def export_to_yaml(modeladmin, request, queryset):
    import yaml
    data = get_queryset_data(modeladmin.model._meta, queryset)
    content_disposition = f'attachment; filename={modeladmin.model._meta.object_name}.yml'
    txt = yaml.safe_dump(data)
    response = HttpResponse(txt, content_type="application/yaml")
    response['Content-Disposition'] = content_disposition
    return response
export_to_yaml.short_description = 'Export to YAML'

def clear_team_scores(modeladmin, request, queryset):
    queryset.update(
        hole1=None, 
        hole2=None, 
        hole3=None, 
        hole4=None, 
        hole5=None, 
        hole6=None, 
        hole7=None, 
        hole8=None, 
        hole9=None, 
        hole10=None,
        hole11=None,
        hole12=None,
        hole13=None,
        hole14=None,
        hole15=None,
        hole16=None,
        hole17=None,
        hole18=None,
        holes_played=0,
        current_raw_score=0,
        current_rel_score=0,
        final_adj_raw_score=0,
        final_adj_rel_score=0,
        proj_adj_rel_score=0,
        updated_on=None,
        sortable_score='',
        rank=None,
        score_calculated=False,
    )
    clear_team_awards(queryset)
clear_team_scores.short_description = 'Clear team scores'

def clear_team_awards(queryset):
    affected_award_types = set(Award.objects.filter(team__in=queryset).values_list('award_type', flat=True))
    Award.objects.filter(team__in=queryset).delete()
    for award_type in affected_award_types:
        Award.objects.filter(award_type=award_type).update(is_best=False)
        latest_award = Award.objects.filter(award_type=award_type).order_by('-created_on').first()
        if latest_award is not None:
            latest_award.is_best = True
            latest_award.save()

def clear_sortable_scores(modeladmin, request, queryset):
    queryset.update(
        sortable_score='',
        score_calculated=False,
    )
clear_sortable_scores.short_description = 'Clear sortable scores'

def recalculate_team_scores(modeladmin, request, queryset):
    ensure_score_cache(request)
    for team in queryset:
        update_team_scores(request, team)
recalculate_team_scores.short_description = 'Recalculate team scores'

def ensure_score_cache(request):
    if 'team' not in request.session:
        request.session['team'] = {}
    if 'cache' in request.session and 'course' in request.session['cache'] and 'hole' in request.session['cache']:
        missing_holes = [str(hole) for hole in range(1, 19) if str(hole) not in request.session['cache']['hole']]
        if len(missing_holes) > 0:
            raise Exception(f'Course data is missing {ru.join_items(missing_holes)}.')
        return
    tournament = Tournament.objects.filter(active=True).first()
    if tournament is None:
        raise Exception('No active tournament found.')
    holes = Hole.objects.filter(course=tournament.course).all()
    request.session['cache'] = {
        'course': {'par': tournament.course.par},
        'hole': {},
    }
    for hole in holes:
        request.session['cache']['hole'][str(hole.hole)] = {
            'par': hole.par,
            'handicap': hole.handicap,
        }
    missing_holes = [str(hole) for hole in range(1, 19) if str(hole) not in request.session['cache']['hole']]
    if len(missing_holes) > 0:
        raise Exception(f'Course data is missing {ru.join_items(missing_holes)}.')

def random_golf_score(par):
    score_delta = random.choices(
        [-1, 0, 1, 2, 3],
        weights=[8, 45, 31, 13, 3],
        k=1,
    )[0]
    return max(1, min(10, par + score_delta))

def add_random_data(modeladmin, request, queryset):
    ensure_score_cache(request)
    hole_data = request.session['cache']['hole']
    team_count = queryset.count()
    for team in queryset:
        for hole_int in range(1, 19):
            par = hole_data[str(hole_int)]['par']
            setattr(team, f'hole{hole_int}', random_golf_score(par))
        if team.handicap is None:
            team.handicap = random.randint(0, 18)
        if team.start_hole is None:
            team.start_hole = random.randint(1, 18)
        update_team_scores(request, team)
    messages.success(request, f'Random score data added for {team_count} {ru.pluralize("team", team_count)}.')
add_random_data.short_description = 'Add random data'

def team_player_list(team):
    players = []
    for player in [team.player1, team.player2, team.player3]:
        if player is not None and len(player.strip()) > 0 and player.strip().upper() != 'TBD':
            players.append(player.strip())
    return players

def add_award_data(modeladmin, request, queryset):
    tournament = Tournament.objects.filter(active=True).first()
    if tournament is None:
        messages.error(request, 'No active tournament found. Random award data not added.')
        return

    special_holes = Hole.objects.filter(course=tournament.course).exclude(special__isnull=True).exclude(special__exact='').order_by('hole')
    if special_holes.count() == 0:
        messages.error(request, 'No special holes found. Random award data not added.')
        return

    teams = [team for team in queryset if len(team_player_list(team)) > 0]
    if len(teams) == 0:
        messages.error(request, 'No selected teams have player names. Random award data not added.')
        return

    base_time = tournament.date_time if tournament.date_time is not None else timezone.now()
    awards_added = 0
    for hole in special_holes:
        award_type = f'{hole.special} : Hole # {hole.hole}'
        shuffled_teams = teams[:]
        random.shuffle(shuffled_teams)
        best_count = random.randint(1, min(len(shuffled_teams), 5))
        for index, team in enumerate(shuffled_teams[:best_count]):
            Award.objects.filter(award_type=award_type, is_best=True).update(is_best=False)
            player = random.choice(team_player_list(team))
            Award.objects.create(
                award_type=award_type,
                team=team,
                player=player,
                created_on=base_time + datetime.timedelta(minutes=(awards_added * 7) + index),
                is_best=True,
            )
            awards_added += 1

    messages.success(request, f'Random award data added for {awards_added} {ru.pluralize("award", awards_added)}.')
add_award_data.short_description = 'Add award data'

def add_random_passwords(modeladmin, request, queryset):
    for team in queryset:
        password = create_random_password()
        team.password = password
        team.save()
add_random_passwords.short_description = 'Add random passwords'

def add_debug_passwords(modeladmin, request, queryset):
    for team in queryset:
        password = '1234'
        team.password = password
        team.save()
add_debug_passwords.short_description = 'Add debug passwords'

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'player1', 'player2', 'player3', 'start_hole', 'handicap', 'password', 'final_adj_raw_score', 'sortable_score', 'active']
    ordering = ['name']
    actions = [clear_sortable_scores, clear_team_scores, recalculate_team_scores, add_random_data, add_award_data, add_random_passwords, add_debug_passwords, export_to_csv, export_to_json, export_to_yaml]
    list_editable = ['start_hole', 'handicap', 'active']

@admin.register(TeamAccess)
class TeamAccessAdmin(admin.ModelAdmin):
    list_display = ['token', 'team']
    ordering = ['team']
    actions = [export_to_csv, export_to_json, export_to_yaml]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'par', 'rating', 'slope', 'active']
    actions = [export_to_csv, export_to_json, export_to_yaml]

@admin.register(Hole)
class HoleAdmin(admin.ModelAdmin):
    list_display = ['course', 'hole', 'par', 'handicap', 'special']
    list_filter = ['course__name']
    ordering = ['course', 'hole']
    actions = [export_to_csv, export_to_json, export_to_yaml]

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    form = TournamentAdminForm
    list_display = ['name', 'date_time', 'archived', 'active']
    actions = [export_to_csv, export_to_json, export_to_yaml]

@admin.register(Cache)
class CacheAdmin(admin.ModelAdmin):
    list_display = ['epoch', 'data']
    actions = [export_to_csv, export_to_json, export_to_yaml]

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['award_type', 'team', 'player', 'created_on', 'is_best']
    list_filter = ['award_type', 'is_best', 'player']
    ordering = ['award_type', '-created_on']
    actions = [export_to_csv, export_to_json, export_to_yaml]

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'name', 'player1', 'player2', 'player3', 'handicap', 'final_adj_raw_score', 'sortable_score', 'active']
    ordering = ['tournament', 'sortable_score']
    list_filter  = ['tournament']
    actions = [export_to_csv, export_to_json, export_to_yaml]

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'handicap', 'score']
    ordering = ['name']
    actions = [export_to_csv, export_to_json, export_to_yaml]


