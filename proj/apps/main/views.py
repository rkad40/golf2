from django.contrib import messages
# from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
# from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from cronos import epoch

import json
import ru
import fs

from .util import TestData

from rex import Rex

from .models import Team, TeamAccess

r"""
 _   _
| | | | ___  _ __ ___   ___
| |_| |/ _ \| '_ ` _ \ / _ \
|  _  | (_) | | | | | |  __/
|_| |_|\___/|_| |_| |_|\___|

"""

def Home(request):
    test = TestData(view='Home')
    from book.models import Article
    rex = Rex()
    articles = Article.objects.filter(Q(active=True) & Q(featured=True)).order_by('priority').all()

    test.add('articles', [])
    for article in articles:
        parts = article.content.partition('---')
        if len(parts[1]) > 0:
            part0 = rex.s(parts[0], r'(\<br\>|\<p\>|\s){0,}$', '', 'g=')
            part2 = rex.s(parts[2], r'^(\<br\>|\<\/p\>|\s){0,}', '', 'g=')
            ms = min(0.5*len(part2), 1000)
            article.content = f'''<div class="intro">{part0}</div>''' + \
                f'''<div class="cont">{part2}</div>''' + \
                f'''<div class="button"><a class="btn btn-primary btn-sm" data-name="read-more" href="javascript:articleAction('{article.slug}', {ms});">Read more<a></div>'''
        else:
            article.content = f'''<div class="intro">{parts[0]}</div>'''
        # test.add('articles', article.content)
        test.add('articles', '')

    hero_url = None
    hero_index = 0
    try:
        hero_index = 0
        hero_images = request.session['cache']['hero-images']
        hero_image_cnt = len(hero_images)
        if hero_image_cnt > 0:
            if 'hero-index' in request.session: 
                hero_index = request.session['hero-index']
            if 'hero-prev' in request.session:
                hero_index -= 1
                if hero_index < 0: 
                    hero_index = hero_image_cnt - 1
                del request.session['hero-prev']
            else:
                hero_index += 1
                if hero_index >= hero_image_cnt:
                    hero_index = 0
            request.session['hero-index'] = hero_index
            hero_url = hero_images[hero_index]
    except:
        hero_url = settings.STATIC_URL + 'main/site/img/hero/HeroDefault.jpg'
    
    test.add('hero-url', hero_url)

    context = dict(
        hero_image_file=hero_url,
        articles=articles,
    )
    test.save()
    return render(request, template_name='home.html', context=context)

r"""
 ____
|  _ \ _ __ _____   __
| |_) | '__/ _ \ \ / /
|  __/| | |  __/\ V /
|_|   |_|  \___| \_/

"""

def Prev(request):
    request.session['hero-prev'] = True
    return redirect('home')

r"""
 ____                      ____              _
/ ___|  ___ ___  _ __ ___ / ___|__ _ _ __ __| |
\___ \ / __/ _ \| '__/ _ \ |   / _` | '__/ _` |
 ___) | (_| (_) | | |  __/ |__| (_| | | | (_| |
|____/ \___\___/|_|  \___|\____\__,_|_|  \__,_|

"""

def ScoreCard(request):
    test = TestData(view='ScoreCard')
    from .forms import ScoreCardForm
    if request.method == 'POST':
        form = ScoreCardForm(request.POST)
        if form.is_valid():
            pass
        else:
            pass
    else:
        form = ScoreCardForm()
    update_url = reverse('update-scores')
    try:
        team = Team.objects.get(id=request.session['team']['id'])
        test.add('team-player1', team.player1)
    except:
        request.session['error'] = 'You must be logged in before you can access a team scorecard. Please go to <a href="/team/login">Team Login</a> and enter your team credentials to gain access.'
        return redirect('error')
    setattr(team, 'str_handicap', f'+{team.handicap}' if team.handicap >= 0 else team.handicap)
    context = dict(
        title='Scorecard',
        can_edit = request.user.is_authenticated or (request.session['cache']['tournament']['enable_team_access'] and request.session['cache']['tournament']['enable_team_input']),
        team=team,
        update_url=update_url, 
        form=form
    )
    test.save()
    return render(request, template_name='score-card.html', context=context)

r"""
 ____                      ____              _ ____  _         __  __
/ ___|  ___ ___  _ __ ___ / ___|__ _ _ __ __| / ___|| |_ __ _ / _|/ _|
\___ \ / __/ _ \| '__/ _ \ |   / _` | '__/ _` \___ \| __/ _` | |_| |_
 ___) | (_| (_) | | |  __/ |__| (_| | | | (_| |___) | || (_| |  _|  _|
|____/ \___\___/|_|  \___|\____\__,_|_|  \__,_|____/ \__\__,_|_| |_|

"""

@login_required
@staff_member_required
def ScoreCardStaff(request, team_name):
    from .util import team_login
    team = Team.objects.get(name=team_name)
    team_login(request, team)
    return redirect('score-card')

r"""
  ____                _      _____     _     _
 / ___|_ __ ___  __ _| |_ __|_   _|_ _| |__ | | ___
| |   | '__/ _ \/ _` | __/ _ \| |/ _` | '_ \| |/ _ \
| |___| | |  __/ (_| | ||  __/| | (_| | |_) | |  __/
 \____|_|  \___|\__,_|\__\___||_|\__,_|_.__/|_|\___|

"""

@login_required
@staff_member_required
def CreateTable(request):
    from .forms import CreateTableForm
    if request.method == 'POST':
        form = CreateTableForm(request.POST)
        if form.is_valid():
            from .util import DatabaseTableSpreadsheet
            data = form.cleaned_data
            validate = DatabaseTableSpreadsheet(data)
            if validate.is_valid:
                request.session['initial_data'] = data
                return redirect('verify-table')
            else:
                messages.error(request, validate.message)
        else:
            messages.error(request, 'One or more errors detected on form submission.')
    else:
        form = CreateTableForm()
    context = dict(
        title='Create Table', 
        form=form,
    )
    return render(request, template_name='create-table.html', context=context)   

r"""
__     __        _  __      _____     _     _
\ \   / /__ _ __(_)/ _|_   |_   _|_ _| |__ | | ___
 \ \ / / _ \ '__| | |_| | | || |/ _` | '_ \| |/ _ \
  \ V /  __/ |  | |  _| |_| || | (_| | |_) | |  __/
   \_/ \___|_|  |_|_|  \__, ||_|\__,_|_.__/|_|\___|
                       |___/
"""

@login_required
@staff_member_required
def VerifyTable(request):
    from .forms import VerifyTableForm
    from .util import DatabaseTableSpreadsheet
    columns = []
    table_data = []
    if request.method == 'POST':
        form = VerifyTableForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            validate = DatabaseTableSpreadsheet(data)
            if validate.is_valid:
                validate.create_table()
                columns = validate.columns
                table_data = validate.table_data
                try:
                    validate.save()
                    messages.success(request, "Data saved.")
                except Exception as err:
                    messages.error(request, f"Data not saved. {err}")
            else:
                messages.error(request, validate.message)
        else:
            messages.error(request, 'One or more errors detected on form submission.')
    else:
        if 'initial_data' in request.session:
            data = ru.clone(request.session['initial_data'])
            del request.session['initial_data']
            form = VerifyTableForm(initial=data)
            validate = DatabaseTableSpreadsheet(data)
            if validate.is_valid:
                validate.create_table()
                columns = validate.columns
                table_data = validate.table_data
                messages.success(request, validate.message)
            else:
                messages.error(request, validate.message)
        else:
            messages.error(request, 'Expected initial data, but found none.')

    context = dict(
        title='Verify Table Data', 
        form=form,
        columns=columns, 
        table_data=table_data,
    )
    return render(request, template_name='verify-table.html', context=context)   

r"""
    _       _           _          _        _   _
   / \   __| |_ __ ___ (_)_ __    / \   ___| |_(_) ___  _ __  ___
  / _ \ / _` | '_ ` _ \| | '_ \  / _ \ / __| __| |/ _ \| '_ \/ __|
 / ___ \ (_| | | | | | | | | | |/ ___ \ (__| |_| | (_) | | | \__ \
/_/   \_\__,_|_| |_| |_|_|_| |_/_/   \_\___|\__|_|\___/|_| |_|___/

"""

@login_required
@staff_member_required
def AdminActions(request):
    test = TestData(view='AdminActions')
    from .forms import AdminActionsForm
    if request.method == 'POST':
        form = AdminActionsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # print(data)
            if data['action'] == 'create-random-passwords':
                from .util import create_random_passwords
                create_random_passwords(request)
            
            elif data['action'] == 'compile-cache':
                from .util import compile_cache
                compile_cache(request)
            
            elif data['action'] == 'make-results-visible':
                from .util import make_results_visible
                make_results_visible(request)
                return redirect('admin-actions')
            elif data['action'] == 'make-results-invisible':
                from .util import make_results_invisible
                make_results_invisible(request)
                return redirect('admin-actions')
            
            elif data['action'] == 'enable-scorecard-editing':
                from .util import enable_scorecard_editing
                enable_scorecard_editing(request)
                return redirect('admin-actions')
            elif data['action'] == 'disable-scorecard-editing':
                from .util import disable_scorecard_editing
                disable_scorecard_editing(request)
                return redirect('admin-actions')
            
            elif data['action'] == 'enable-team-access':
                from .util import enable_team_access
                enable_team_access(request)
                return redirect('admin-actions')
            elif data['action'] == 'disable-team-access':
                from .util import disable_team_access
                disable_team_access(request)
                return redirect('admin-actions')
            
            elif data['action'] == 'enable-leader-board':
                from .util import enable_leader_board
                enable_leader_board(request)
                return redirect('admin-actions')
            elif data['action'] == 'disable-leader-board':
                from .util import disable_leader_board
                disable_leader_board(request)
                return redirect('admin-actions')
            
            elif data['action'] == 'archive-tournament':
                from .util import archive_tournament
                archive_tournament(request)

            # elif data['action'] == 'debug-action':
            #     from .util import debug_action
            #     debug_action(request)
        else:
            messages.error(request, 'An error occurred while trying to complete the requested action.')
    else:
        form = AdminActionsForm()
    context = dict(
        title='Admin Actions', 
        form=form,
    )
    test.save()
    return render(request, template_name='admin-actions.html', context=context)       

r"""
 _____                    _                _
|_   _|__  __ _ _ __ ___ | |    ___   __ _(_)_ __
  | |/ _ \/ _` | '_ ` _ \| |   / _ \ / _` | | '_ \
  | |  __/ (_| | | | | | | |__| (_) | (_| | | | | |
  |_|\___|\__,_|_| |_| |_|_____\___/ \__, |_|_| |_|
                                     |___/
"""

def TeamLogin(request):
    r'''
    Team login view.  
    '''
    test = TestData(view='TeamLogin')
    from .forms import TeamLoginForm
    if request.method == 'POST':
        form = TeamLoginForm(request.POST)
        if settings.TESTING and hasattr(request, 'test_form_debug'):
            form = getattr(request, 'test_form_debug')
        if form.is_valid():
            test.add('form-is-valid', True)
            data = form.cleaned_data
            if settings.DEBUG: print('Login attempt:')
            try:
                name = data['team'].upper().strip()
                while len(name) < 3: name = '0' + name
                password = data['password'].lower().strip()
                if settings.DEBUG: print(f'- User specified name:     "{name}"')
                if settings.DEBUG: print(f'- User specified password: "{password}"')
                team = Team.objects.get(name=name)
                if settings.DEBUG: print(f'- User expected password:  "{team.password.lower()}"')
                if team.password.lower() == password:
                    if settings.DEBUG: print(f'- Login successful')
                    from .util import team_login
                    team_login(request, team)
                    # Get a list of players on the team...
                    players = []
                    if team.player1 is not None and len(team.player1) > 0: 
                        players.append(team.player1)
                    if team.player2 is not None and len(team.player2) > 0: 
                        players.append(team.player2)
                    if team.player3 is not None and len(team.player3) > 0: 
                        players.append(team.player3)
                    if len(players) == 0:
                        players.append('TBD')
                    # Print flash message for successful login.  Include link for players to update
                    # their profiles.  
                    url = reverse('player-select')
                    if not settings.TESTING:
                        messages.success(request, f"""Team {team.name} login was successful.  Welcome {ru.join_items(players, last_join=" and ")}!<br>&nbsp;<br>Click <strong>News &amp; Info</strong> below, or scroll down the page for further instructions.<br>&nbsp;<br>At some point today, please <a href="{url}">update contact information</a> for all players on your team.""")
                    # If we get here, login was successful.  Redirect to home page.
                    test.add('players', players)
                    test.save()
                    return redirect('home')
                else:
                    raise Exception('Password incorrect.  Please try again.')
            except:
                messages.error(request, 'Invalid team name or password.  Please try again.')
        else:
            messages.error(request, 'Invalid team name or password.  Please try again.')
    else:
        form = TeamLoginForm()
    context = dict(
        title='Team Login', 
        button='Log In',
        icon='check',
        form=form,
    )
    test.save()
    return render(request, template_name='simple-form.html', context=context)    

r"""
 _____                    _                            _
|_   _|__  __ _ _ __ ___ | |    ___   __ _  ___  _   _| |_
  | |/ _ \/ _` | '_ ` _ \| |   / _ \ / _` |/ _ \| | | | __|
  | |  __/ (_| | | | | | | |__| (_) | (_| | (_) | |_| | |_
  |_|\___|\__,_|_| |_| |_|_____\___/ \__, |\___/ \__,_|\__|
                                     |___/
"""

def TeamLogout(request):
    if 'team' not in request.session:
        request.session['team'] = {'access': False}
    if 'token' in request.session['team']:
        team_token = request.session['team']['token']
        try:
            team_access = TeamAccess.objects.get(token=team_token)
            team_access.delete()
        except:
            pass
    for key in ['token', 'name', 'id']:
        if key in request.session['team']:
            del request.session['team'][key]
    request.session['team']['access'] = False
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')

r"""
    _     _            _____                    ___        __
   / \   (_) __ ___  _|_   _|__  __ _ _ __ ___ |_ _|_ __  / _| ___
  / _ \  | |/ _` \ \/ / | |/ _ \/ _` | '_ ` _ \ | || '_ \| |_ / _ \
 / ___ \ | | (_| |>  <  | |  __/ (_| | | | | | || || | | |  _| (_) |
/_/   \_\/ |\__,_/_/\_\ |_|\___|\__,_|_| |_| |_|___|_| |_|_|  \___/
       |__/
"""

def AjaxTeamInfo(request):
    from main.util import dictate
    from main.models import Team
    send_data = {'teams': {}}
    for team in Team.objects.filter(active=True).order_by('name').all():
        d = dictate(team)
        send_data['teams'][str(team.name).upper()] = dictate(team)
    rex = Rex()
    matching_letter_lookup = {'A':'B', 'B':'A', 'C':'D', 'D':'C', 'E':'F', 'F':'E'}
    for name in send_data['teams']:
        name_to_start_hole = rex.s(name, r'\D', '', 'g=')
        name_to_letter = str(rex.s(name, r'\d', '', 'g=')).upper()
        matching_letter = matching_letter_lookup[name_to_letter]
        paired_with = name_to_start_hole + matching_letter
        if paired_with in send_data['teams']:
            send_data['teams'][name]['paired_with'] = paired_with
        else:
            send_data['teams'][name]['paired_with'] = ''
    return JsonResponse(send_data)


r"""
    _     _            _   _           _       _
   / \   (_) __ ___  _| | | |_ __   __| | __ _| |_ ___
  / _ \  | |/ _` \ \/ / | | | '_ \ / _` |/ _` | __/ _ \
 / ___ \ | | (_| |>  <| |_| | |_) | (_| | (_| | ||  __/
/_/   \_\/ |\__,_/_/\_\\___/| .__/ \__,_|\__,_|\__\___|
       |__/                 |_|
 ____
/ ___|  ___ ___  _ __ ___  ___
\___ \ / __/ _ \| '__/ _ \/ __|
 ___) | (_| (_) | | |  __/\__ \
|____/ \___\___/|_|  \___||___/

"""

def AjaxUpdateScores(request):
    from .util import update_team_scores, get_leader_board, get_hole_awards, update_special_award
    from .models import Tournament
    # All Ajax requests must be of type POST.  If not, go scorched earth.
    if request.method != 'POST':
        post_data = dict(valid=False, error='Invalid request.')
        return JsonResponse(post_data)
    # Get POST post_data 
    try:
        post_data = request.POST.dict()
        post_data = json.loads(post_data['Data'])
        team_session = request.session['team']
        site_team_name = team_session['name']
        team_id = team_session['id']
        data_team_name = post_data['TeamInfo']['Name']
    except Exception:
        return JsonResponse(dict(valid=False, error='Invalid scorecard request. Please refresh the page and try again.'))
    notes = []
    warnings = []
    tournament = Tournament.objects.filter(active=True).first()
    if tournament is None:
        return JsonResponse(dict(valid=False, error='No active tournament found.'))
    can_write = request.user.is_authenticated or (tournament.enable_team_access and tournament.enable_team_input)
    enable_write = post_data.get('EnableWrite', 0)
    if isinstance(enable_write, str):
        enable_write = enable_write.lower() in ['1', 'true', 'yes']
    else:
        enable_write = bool(enable_write)
    if enable_write and not can_write:
        enable_write = False
        warnings.append('Data not saved.  Write access to team scorecard data is not currently enabled.')
    if data_team_name != site_team_name:
        send_error_data = dict(
            valid=False,
            error=f"""You submitted data for team "{data_team_name}". But your credentials identify you as belonging to team "{site_team_name}".  Data not saved."""
        )
        return JsonResponse(send_error_data)
    team = Team.objects.get(pk=team_id)
    write_occurred = False
    if 'Award' in post_data: 
        txt = update_special_award(request, team, post_data['Award'])
        notes.append(txt)
    write_occurred = update_team_scores(request, team, post_data, enable_write)
    awards = get_hole_awards(request)
    leader_board, our_team_data = get_leader_board(request, team)
    send_data = dict(awards=awards, leaderBoard=leader_board, ourTeamData=our_team_data, writeOccurred=write_occurred, valid=True)
    if len(warnings) > 0:
        send_data['warning'] = ' '.join(warnings)
    if len(notes) > 0:
        send_data['notes'] = ' '.join(notes)
    return JsonResponse(send_data)

r"""
 _____ _             _ _         ____                 _ _
|  ___(_)_ __   __ _| (_)_______|  _ \ ___  ___ _   _| | |_ ___
| |_  | | '_ \ / _` | | |_  / _ \ |_) / _ \/ __| | | | | __/ __|
|  _| | | | | | (_| | | |/ /  __/  _ <  __/\__ \ |_| | | |_\__ \
|_|   |_|_| |_|\__,_|_|_/___\___|_| \_\___||___/\__,_|_|\__|___/

"""

def FinalizeResults(request):
    try:
        from .util import finalize_tournament_results
        data = finalize_tournament_results(request)
        context = dict(
            title='Tournament Results', 
            data=data,
        )
        return render(request, template_name='tournament-results.html', context=context)    
    except Exception:
        return redirect('past-results')

r"""
 _____
| ____|_ __ _ __ ___  _ __
|  _| | '__| '__/ _ \| '__|
| |___| |  | | | (_) | |
|_____|_|  |_|  \___/|_|

"""

def Error(request):
    try:
        msg = request.session['error']
        del request.session['error']
    except:
        msg = f"<p>Sorry, it seams this request has resulted in an unforeseen error.</p><p>Please go back and try your requested action again.  If the problem persists, please contact the tournament organizer, <strong>{settings.ADMIN_NAME}</strong> at {settings.ADMIN_PHONE}.</p>"
    context = dict(
        title='Error',
        message=msg
    )
    return render(request, template_name='error.html', context=context)

r"""
 ____           _
|  _ \ __ _ ___| |_
| |_) / _` / __| __|
|  __/ (_| \__ \ |_
|_|   \__,_|___/\__|

 _____                                                 _
|_   _|__  _   _ _ __ _ __   __ _ _ __ ___   ___ _ __ | |_ ___
  | |/ _ \| | | | '__| '_ \ / _` | '_ ` _ \ / _ \ '_ \| __/ __|
  | | (_) | |_| | |  | | | | (_| | | | | | |  __/ | | | |_\__ \
  |_|\___/ \__,_|_|  |_| |_|\__,_|_| |_| |_|\___|_| |_|\__|___/

"""

def PastTouraments(request):
    from .forms import PastTournamentsForm
    from .models import History, Tournament
    teams = None
    tournament = None
    if request.method == 'POST':
        form = PastTournamentsForm(request.POST)
        if form.is_valid():
            tournament = Tournament.objects.get(id=form.cleaned_data['tournament'])
            teams = History.objects.filter(tournament=tournament).order_by('sortable_score').all()
    else:
        form = PastTournamentsForm()
    # print(tournament)
    context = dict(
        title='Past Tournaments', 
        tournament=tournament,
        teams=teams,
        form=form,
    )
    return render(request, template_name='past-tournament-results.html', context=context)    

r"""
 _____                        _     _     _
|_   _|__  __ _ _ __ ___  ___| |   (_)___| |_
  | |/ _ \/ _` | '_ ` _ \/ __| |   | / __| __|
  | |  __/ (_| | | | | | \__ \ |___| \__ \ |_
  |_|\___|\__,_|_| |_| |_|___/_____|_|___/\__|

"""

def TeamsList(request):
    from .models import Team
    teams = Team.objects.filter(active=True).order_by('name').all()
    context = dict(
        title='Teams', 
        teams=teams,
    )
    return render(request, template_name='teams-list.html', context=context)    

r"""
 ____  _                       ____       _           _
|  _ \| | __ _ _   _  ___ _ __/ ___|  ___| | ___  ___| |_
| |_) | |/ _` | | | |/ _ \ '__\___ \ / _ \ |/ _ \/ __| __|
|  __/| | (_| | |_| |  __/ |   ___) |  __/ |  __/ (__| |_
|_|   |_|\__,_|\__, |\___|_|  |____/ \___|_|\___|\___|\__|
               |___/
"""

def PlayerSelect(request):
    try:
        team_id = request.session['team']['id']
    except:
        request.session['error'] = 'You must be logged in before you can edit a player profile. Please go to <a href="/team/login">Team Login</a> and enter your team credentials to gain access.'
        return redirect('error')
    from .models import Team
    context = dict(
        title='Player Select', 
        players=request.session['team']['player_list'],
    )
    return render(request, template_name='player-select.html', context=context)    

r"""
 ____  _                       ____             __ _ _
|  _ \| | __ _ _   _  ___ _ __|  _ \ _ __ ___  / _(_) | ___
| |_) | |/ _` | | | |/ _ \ '__| |_) | '__/ _ \| |_| | |/ _ \
|  __/| | (_| | |_| |  __/ |  |  __/| | | (_) |  _| | |  __/
|_|   |_|\__,_|\__, |\___|_|  |_|   |_|  \___/|_| |_|_|\___|
               |___/
 _   _
| \ | | __ _ _ __ ___   ___
|  \| |/ _` | '_ ` _ \ / _ \
| |\  | (_| | | | | | |  __/
|_| \_|\__,_|_| |_| |_|\___|

"""

def PlayerProfileName(request, name):
    from .models import Player
    from .forms import PlayerProfileForm
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST)
        if form.is_valid():
            player = form.save()
            return redirect('player-profile-id', player.id)
        else:
            messages.error(request, f'Form not saved.  Please correct the errors first. {form.errors.as_data()}')
    else:
        try:
            player = Player.objects.filter(name=name).first()
            return redirect('player-profile-id', player.id)
        except:
            pass
        form = PlayerProfileForm(initial={'name': name})
    context = dict(
        title=f'Player Profile', 
        name=name,
        form=form,
    )
    return render(request, template_name='player-profile.html', context=context)    

r"""
 ____  _                       ____             __ _ _      ___ ____
|  _ \| | __ _ _   _  ___ _ __|  _ \ _ __ ___  / _(_) | ___|_ _|  _ \
| |_) | |/ _` | | | |/ _ \ '__| |_) | '__/ _ \| |_| | |/ _ \| || | | |
|  __/| | (_| | |_| |  __/ |  |  __/| | | (_) |  _| | |  __/| || |_| |
|_|   |_|\__,_|\__, |\___|_|  |_|   |_|  \___/|_| |_|_|\___|___|____/
               |___/
"""

def PlayerProfileID(request, id):
    from .models import Player
    from .forms import PlayerProfileForm
    player = Player.objects.get(pk=id)
    name = player.name
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            player.__dict__.update(**data)
            player.save()
            # Player.objects.update(**data)
            messages.success(request, f'Profile for {name} saved.')
            return redirect('player-profile-id', id)
    else:
        form = PlayerProfileForm(instance=player)
    context = dict(
        title=f'Player Profile',
        name=name, 
        form=form,
    )
    return render(request, template_name='player-profile.html', context=context)    
    
