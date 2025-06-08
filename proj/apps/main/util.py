import json, csv
import ru
from rex import Rex
from django.apps import apps
from main.models import Course, Team
from django.db.models import Q
from django.contrib import messages
from cronos import epoch
import unchained
from django.conf import settings
import fs

GOLF_WORDS = ['ace', 'backspin', 'birdie', 'blade', 'blue', 'break', 'bogey', 'bunker', 'cart', 
    'chip', 'course', 'divot', 'dogleg', 'draw', 'drive', 'driver', 'range', 'eagle', 'fade', 
    'fairway', 'flag', 'flight', 'fore', 'green', 'grip', 'hacker', 'handicap', 'hazard', 'hole', 
    'hook', 'hybrid', 'irons', 'layup', 'line', 'links', 'marker', 'mulligan', 'par', 'pickup', 
    'pitch', 'putt', 'putter', 'red', 'rough', 'round', 'shaft', 'shank', 'scratch', 'shoot', 
    'shot', 'slice', 'slope', 'stroke', 'swing', 'tee', 'trap', 'waggle', 'wedge', 'whiff', 'woods']

r"""
                     _                             _
  ___ _ __ ___  __ _| |_ ___   _ __ __ _ _ __   __| | ___  _ __ ___
 / __| '__/ _ \/ _` | __/ _ \ | '__/ _` | '_ \ / _` |/ _ \| '_ ` _ \
| (__| | |  __/ (_| | ||  __/ | | | (_| | | | | (_| | (_) | | | | | |
 \___|_|  \___|\__,_|\__\___| |_|  \__,_|_| |_|\__,_|\___/|_| |_| |_|

                                           _
 _ __   __ _ ___ _____      _____  _ __ __| |
| '_ \ / _` / __/ __\ \ /\ / / _ \| '__/ _` |
| |_) | (_| \__ \__ \\ V  V / (_) | | | (_| |
| .__/ \__,_|___/___/ \_/\_/ \___/|_|  \__,_|
|_|

"""

def create_random_password():
    password = ru.ritem(GOLF_WORDS) + str(ru.rint(100, 999))
    return password

r"""
                     _                             _
  ___ _ __ ___  __ _| |_ ___   _ __ __ _ _ __   __| | ___  _ __ ___
 / __| '__/ _ \/ _` | __/ _ \ | '__/ _` | '_ \ / _` |/ _ \| '_ ` _ \
| (__| | |  __/ (_| | ||  __/ | | | (_| | | | | (_| | (_) | | | | | |
 \___|_|  \___|\__,_|\__\___| |_|  \__,_|_| |_|\__,_|\___/|_| |_| |_|

                                           _
 _ __   __ _ ___ _____      _____  _ __ __| |___
| '_ \ / _` / __/ __\ \ /\ / / _ \| '__/ _` / __|
| |_) | (_| \__ \__ \\ V  V / (_) | | | (_| \__ \
| .__/ \__,_|___/___/ \_/\_/ \___/|_|  \__,_|___/
|_|
"""

def create_random_passwords(request):
    teams = Team.objects.filter(active=True).filter(Q(password='') | Q(password__isnull=True)).all()
    cnt = len(teams)
    if cnt > 0:
        for team in teams:
            password = create_random_password()
            team.password = password
            team.save()
        messages.success(request, f'Random passwords added for {cnt} {ru.pluralize("team", cnt)}.')
    else:
        messages.success(request, f'All valid teams already have passwords defined. No passwords added.')

r"""
     _ _      _        _
  __| (_) ___| |_ __ _| |_ ___
 / _` | |/ __| __/ _` | __/ _ \
| (_| | | (__| || (_| | ||  __/
 \__,_|_|\___|\__\__,_|\__\___|

"""

def dictate(obj):
    if type(obj) == dict:
        data = obj
    else:
        data = obj.__dict__
    d = {}
    for key in data:
        if key.startswith('_'): continue
        val = data[key]
        if val is not None:
            stype = ru.stype(data[key])
            if stype not in ['int', 'str', 'bool', 'float']:
                val = str(val)
        d[key] = val
    return d

r"""
           _            _       _         _
  ___ __ _| | ___ _   _| | __ _| |_ ___  | |_ ___  __ _ _ __ ___
 / __/ _` | |/ __| | | | |/ _` | __/ _ \ | __/ _ \/ _` | '_ ` _ \
| (_| (_| | | (__| |_| | | (_| | ||  __/ | ||  __/ (_| | | | | | |
 \___\__,_|_|\___|\__,_|_|\__,_|\__\___|  \__\___|\__,_|_| |_| |_|

 _                     _ _
| |__   __ _ _ __   __| (_) ___ __ _ _ __    _ __   ___ _ __
| '_ \ / _` | '_ \ / _` | |/ __/ _` | '_ \  | '_ \ / _ \ '__|
| | | | (_| | | | | (_| | | (_| (_| | |_) | | |_) |  __/ |
|_| |_|\__,_|_| |_|\__,_|_|\___\__,_| .__/  | .__/ \___|_|
                                    |_|     |_|
 _           _
| |__   ___ | | ___
| '_ \ / _ \| |/ _ \
| | | | (_) | |  __/
|_| |_|\___/|_|\___|

"""

def calculate_team_handicap_per_hole(request, team):
    # Initialize variables.
    hole_rank_list = [] # Hole rank (handicaps) list.  Just a list from 1 to 18.
    team_hole_rank_to_handicap_adder = {}  # Create a team hole rank to score adder dict.
    team_handicap = team.handicap # Get the team handicap.

    # Stuff `hole_rank_list` and set all `team_hole_rank_to_handicap_adder` entries to 0.
    for i in range(1, 19):
        hole_rank_list.append(i)
        team_hole_rank_to_handicap_adder[str(i)] = 0

    # Value `score_adder` is the number of strokes we will add or substract from a score based 
    # on handicap.  We assume a positive number, for a positive handicap.  But it may be negative,
    # for a negative handicap.
    score_adder = 1
    if team_handicap < 0: 
        # As noted, it is possible to have a negative handicap.  
        score_adder = -1
        # Make sure `team_handicap` is positive.  We'll deal with the sign change later.
        team_handicap = abs(team_handicap)
        # Reverse the `hole_rank_list`.  The idea is that we will SUBTRACT positive handicap stokes 
        # from the hardest holes or ADD negative handicap strokes to the easiest holes.  So 
        # direction very much matters.
        hole_rank_list.reverse()

    # Create `rolling_hole_rank_list`.  This is just the `hole_rank_list` repeated as many times as
    # necessary to account for all handicap strokes.  For example, if a team has a +20 handicap, 
    # they will get a +1 handicap on holes ranked 1 to 18 on the first iteration through the 
    # `rolling_hole_rank_list` and an additional +1 handicap (so, +2) for the holes ranked the 
    # first and second hardest.  Total handicap will be +20.  
    rolling_hole_rank_list = []
    rolling_hole_rank_list.extend(hole_rank_list)
    for i in range(0, (team_handicap//18)):
        rolling_hole_rank_list.extend(hole_rank_list)

    # Save a copy of `team_handicap` as `team_handicap_rolling`.  We'll decrement this value every
    # time we cycle through a new hole ranking in `rolling_hole_rank_list`.  We'll stop when we hit
    # 0.
    team_handicap_rolling = team_handicap
    while team_handicap_rolling > 0:
        # Pull the current hole rank from the `rolling_hole_rank_list` list.  Note, we convert to 
        # a string because `request.session['cache']['hole']`, which we will use later to convert
        # hole rank into a hole number, is deserialized JSON.  JSON will convert *all* keys to 
        # strings.  So we have to type match here. 
        current_hole_rank = str(rolling_hole_rank_list.pop(0))
        team_hole_rank_to_handicap_adder[current_hole_rank] += score_adder
        team_handicap_rolling -= 1

    # Finally, we want to compute `team_hole_to_handicap`.  We have `team_hole_rank_to_handicap_adder`,
    # but we want our lookup to be based on hole, not handicap.  Makes it simpler down the road.
    team_hole_to_handicap = {}
    hole_info = request.session['cache']['hole']
    for hole_key in hole_info:
        hole_rank = str(hole_info[hole_key]['handicap']) 
        team_hole_to_handicap[hole_key] = team_hole_rank_to_handicap_adder[hole_rank]
    request.session['team']['hole_handicap'] = team_hole_to_handicap

    # print(json.dumps(team_hole_rank_to_handicap_adder, indent=None))

r"""
                           _ _                       _
  ___ ___  _ __ ___  _ __ (_) | ___    ___ __ _  ___| |__   ___
 / __/ _ \| '_ ` _ \| '_ \| | |/ _ \  / __/ _` |/ __| '_ \ / _ \
| (_| (_) | | | | | | |_) | | |  __/ | (_| (_| | (__| | | |  __/
 \___\___/|_| |_| |_| .__/|_|_|\___|  \___\__,_|\___|_| |_|\___|
                    |_|
"""

def compile_cache(request):
    r'''
    Compile cached content as JSON data and save to Cache table.

    Example:

    ```json
        {
        "hero-images": [
            "/media/Hero/hero1.jpg",
            "/media/Hero/hero10.jpg",
            "/media/Hero/hero2.jpg",
            "/media/Hero/hero3.jpg",
            "/media/Hero/hero4.jpg",
            "/media/Hero/hero5.jpg",
            "/media/Hero/hero6.jpg",
            "/media/Hero/hero7.jpg",
            "/media/Hero/hero8.jpg",
            "/media/Hero/hero9.jpg"
        ],
        "tournament": {
            "id": 3,
            "name": "Rockne Invitational",
            "date_time": "2022-06-18 13:00:00+00:00",
            "course_id": 1,
            "play_from": "white",
            "enable_team_access": false,
            "enable_team_input": false,
            "show_leader_board": false,
            "show_results": false,
            "archived": false,
            "archive_notes": "None",
            "active": true
        },
        "course": {
            "id": 1,
            "name": "ColoVista",
            "par": 72,
            "rating": 74.1,
            "slope": 129.0,
            "active": true
        },
        "hole": {
            "1": {
                "hole": 1,
                "par": 4,
                "handicap": 1,
                "special": "",
                "yards": 398
            },
            "2": {
                "hole": 2,
                "par": 4,
                "handicap": 13,
                "special": "",
                "yards": 374
            },
            ...
            "18": {
                "hole": 18,
                "par": 4,
                "handicap": 16,
                "special": "",
                "yards": 333
            }
        },
        "team": {}
        }
    ```
    '''
    # Get the models to be used in this function. 
    from main.models import Team, Hole, Course, Tournament, Team, Cache
    data = {}

    # Cache hero images. 
    hero_dir = fs.join(settings.MEDIA_ROOT, 'Hero')
    hero_url = settings.MEDIA_URL + 'Hero/'
    hero_images = list(fs.files(hero_dir, regx=r'(?i)\.(jpg|png)$', rec=False))
    data['hero-images'] = [hero_url + fs.filename(hero_file) for hero_file in hero_images]

    # Cache tournament data.
    tournament = Tournament.objects.filter(active=True)[0]
    data['tournament'] = dictate(tournament.__dict__)

    # Cache course data.
    data['course'] = dictate(tournament.course.__dict__)

    # Cache hole data.
    data['hole'] = {}
    for hole in Hole.objects.filter(course_id=data['tournament']['course_id']).all().values():
        hole['yards'] = hole[tournament.play_from]
        num = int(hole['hole'])
        for key in ['id', 'course_id', 'gold', 'blue', 'white', 'red']:
            try: del hole[key]
            except: pass
        data['hole'][num] = dictate(hole)

    # Cache team data.
    data['team'] = {}
    for team in Team.objects.filter(active=True).all().values():
        name = team['name']
        data['team'][name] = {}
        for key in ['player1', 'player2', 'player3', 'handicap', 'start_hole']:
            data['team'][name][key] = team[key]
        data['team'][name]['str_handicap'] = f"""+{data['team'][name]['handicap']}""" if data['team'][name]['handicap'] >= 0 else f"""{data['team'][name]['handicap']}"""
    
    # Print data (for debug).
    # print(json.dumps(data, indent=2))
    
    # Get JSON text data to cache.
    json_txt = json.dumps(data, indent=None, separators=(',', ':'))

    cache = None
    try: cache = Cache.objects.first()
    except: pass

    # Only save one cache record.  So if a record exists.  Delete it.
    if cache is not None:
        Cache.objects.filter(~Q(id=cache.id)).delete()
        cache.data = json_txt
        cache.epoch = epoch(int)
        cache.save()
    else:
        Cache.objects.create(data=json_txt, epoch=epoch(int))

    # Indicate that the cache was successfully saved.  
    messages.success(request, f'Cache successfully compiled.')

r"""
 ____        _        _                   _____     _     _
|  _ \  __ _| |_ __ _| |__   __ _ ___  __|_   _|_ _| |__ | | ___
| | | |/ _` | __/ _` | '_ \ / _` / __|/ _ \| |/ _` | '_ \| |/ _ \
| |_| | (_| | || (_| | |_) | (_| \__ \  __/| | (_| | |_) | |  __/
|____/ \__,_|\__\__,_|_.__/ \__,_|___/\___||_|\__,_|_.__/|_|\___|

 ____                           _     _               _
/ ___| _ __  _ __ ___  __ _  __| |___| |__   ___  ___| |_
\___ \| '_ \| '__/ _ \/ _` |/ _` / __| '_ \ / _ \/ _ \ __|
 ___) | |_) | | |  __/ (_| | (_| \__ \ | | |  __/  __/ |_
|____/| .__/|_|  \___|\__,_|\__,_|___/_| |_|\___|\___|\__|
      |_|
"""
class DatabaseTableSpreadsheet():
    r'''
    Render data in Tabulator.

    ## Arguments

    - `form_data`: Dict object with keys "data_type" (either "json" or "tab") and "data" (containing
        the raw text table data)

    ## Usage

    ```python
    # In view function:
    from .util import DatabaseTableSpreadsheet
    form_data = form.cleaned_data
    validate = DatabaseTableSpreadsheet(form_data)
    if validate.is_valid:
        request.session['initial_data'] = form_data
        return redirect('verify-table')
    else:
        messages.error(request, validate.message)
    ```
    '''
    def __init__(self, form_data):
        self.is_valid = False
        self.message = ''
        self.form_data = form_data
        self.table_data = None
        self.columns = []
        if form_data['data_type'] == 'json':
            try:
                self.table_data = json.loads(form_data['data'])
                self.is_valid = True
                self.message = 'Data looks good!'
            except json.JSONDecodeError as err:
                self.is_valid = False
                self.message = f"JSON decode error detected in raw text. {err}.  Please fix this first."
        elif form_data['data_type'] == 'tab':
            txt = form_data['data']
            reader = csv.reader(txt.splitlines(), delimiter='\t')
            lines = list(reader)
            if len(lines) == 0:
                self.is_valid = False
                self.message = f"TAB decode error.  No data."
                return
            fields = lines.pop(0)
            rows = []
            for line in lines:
                row = dict(zip(fields, line))
                rows.append(row)
            self.table_data = rows
            self.is_valid = True
            self.message = 'Data looks good!'

    def create_table(self):
        self.is_valid = False
        self.message = ''
        try:
            # Create some local variables.
            rex = Rex()
            columns = []
            size = {}
            form_data = self.form_data
            field_type = {}
            table_name = form_data['table']
            
            # Get all table fields.
            model = apps.get_model('main', table_name)
            fields = model._meta.get_fields()
            
            # Cycle through all fields and update `columns` list.  Each item in list will be a column dict
            # with keys 'title', 'field', 'width' and 'editor'.  Also update `size` dict.
            for field in fields:
                field_name = field.name
                field_type_value = str(field.get_internal_type())
                field_type[field_name] = field_type_value
                verbose_name = field.name
                try: 
                    verbose_name = field.verbose_name
                    verbose_name = rex.s(verbose_name, r'\s+(\S{3,})', r'<br>\1', 'g=')
                    column = dict(title=verbose_name, field=field.name, width=150, sorter='string', editor='input')
                    if field_name == 'id':
                        continue
                    if table_name == 'Hole' and field_name == 'course':
                        continue
                    if field_type_value == 'IntegerField':
                        column['hozAlign'] = 'center'
                        column['sorter'] = 'number'
                    elif field_type_value == 'FloatField':
                        column['hozAlign'] = 'center'
                        column['sorter'] = 'number'
                    elif field_type_value == 'BooleanField':
                        column['sorter'] = 'boolean'
                        column['formatter'] = 'tickCross'
                        column['editor'] = 'tickCross'
                        column['editorParams'] = {'tristate': False, 'elementAttributes': {'maxlength': 10}}
                        column['hozAlign'] = 'center'
                    columns.append(column)
                    size[field.name] = 10
                except:
                    pass

            # Get the rows data from the session.
            rows_data = self.table_data

            # Cycle through each row in `rows_data`.  Therein, cycle through each key in the individual 
            # row data and get the length of the data value.  Use to update `size` dict.
            for row in rows_data:
                temp_row = ru.clone(row)
                for field_name in temp_row:
                    value = row[field_name]
                    str_value = str(value)
                    if field_name == 'id':
                        del row[field_name]
                        continue
                    if table_name == 'Hole' and field_name == 'course':
                        del row[field_name]
                        continue
                    if field_type[field_name] == 'IntegerField':
                        row[field_name] = int(value)
                    elif field_type[field_name] == 'FloatField':
                        row[field_name] = float(value)
                    elif field_type[field_name] == 'BooleanField':
                        row[field_name] = bool(value)
                    elif field_type_value == 'DateTimeField':
                        print("**DateTime**")
                        print(value)
                        print(str(value))
                    # else:
                    #     row[field_name] = str(value)
                    size[field_name] = max(size[field_name], len(str_value))

            # Update the 'width' attribute for each column in `columns` list.
            for column in columns:
                field_name = column['field']
                column['width'] = max(50, 11 * size[field_name])
            self.columns = columns
            self.is_valid = True

        except Exception as err:
            self.is_valid = False
            self.message = f"JSON decode error detected in raw text. {err}.  Please fix this first."

    def save(self):

        # Create some local variables.
        rex = Rex()
        form_data = self.form_data
        table_name = form_data['table']
        course_obj = None
        course_id = None
        
        # Get all table fields.
        model = apps.get_model('main', table_name)

        if table_name == 'Hole':
            course_id = form_data['course']
            course_obj = Course.objects.get(pk=course_id)
            model.objects.filter(course=course_obj).delete()
        else:
            model.objects.all().delete()
        
        for row in self.table_data:
            inst_data = {}
            for key in row:
                if row[key] is not None:
                    inst_data[key] = row[key]
                if key == 'updated_on' and rex.m(inst_data[key], r'(\d+)/(\d+)/(\d+)\s+(\d+):(\d+)'):
                    dt = f'{int(rex.d(3)):04d}-{int(rex.d(1)):02d}-{int(rex.d(2)):02d} {int(rex.d(4)):02d}:{int(rex.d(5)):02d}:00'
                    inst_data[key] = dt
                    print(f'** updated_on = "{inst_data[key]}" = "{dt}" **')
            if table_name == 'Hole':
                inst_data['course'] = course_obj
            inst = model.objects.create(**inst_data)
            inst.save()

r"""
                 _       _                             _       _
 _   _ _ __   __| | __ _| |_ ___   ___ _ __   ___  ___(_) __ _| |
| | | | '_ \ / _` |/ _` | __/ _ \ / __| '_ \ / _ \/ __| |/ _` | |
| |_| | |_) | (_| | (_| | ||  __/ \__ \ |_) |  __/ (__| | (_| | |
 \__,_| .__/ \__,_|\__,_|\__\___| |___/ .__/ \___|\___|_|\__,_|_|
      |_|                             |_|
                             _
  __ ___      ____ _ _ __ __| |
 / _` \ \ /\ / / _` | '__/ _` |
| (_| |\ V  V / (_| | | | (_| |
 \__,_| \_/\_/ \__,_|_|  \__,_|

"""

def update_special_award(request, team, data):
    r"""
    If AjaxUpdateScores() is called and post_data['Award'] is defined, the asynchronous scorecard submission has award 
    data of the form: 

    ```python
    post_data['Award'] = {
        'AwardType': award_long,   # e.g. "Closest to the Hole : Hole # 5" or "Longest Drive : Hole # 11"
        'Team': team_name',        # e.g. "01A"
        'Player': player_name,     # e.g. "John Doe"
    };
    ```

    Under these conditions update_special_award() is called and the Award model is updated with the closest to the hole
    or longest drive data.

    ## Arguments 
    - `request`: Django request object
    - `team`: Team data object of the selected team
    - `data`: `post_data['Award']`

    ## Returns 
    Alert message to be printed.
    """
    from .models import Award
    # Argument `data` is `post_data['Award']`.
    prev_awards = Award.objects.filter(award_type=data['AwardType']).all()
    for award in prev_awards:
        award.is_best = False
        award.save()
    Award.objects.create(
        award_type=data['AwardType'], 
        team=team, 
        player=data['Player'], 
        created_on=unchained.get_localized_datetime_now(),
        is_best=True
    )
    return f"""<strong>{data['Player']}</strong> is now the top name on the list for <strong>{data['AwardType']}</strong>."""

r"""
                 _       _         _
 _   _ _ __   __| | __ _| |_ ___  | |_ ___  __ _ _ __ ___
| | | | '_ \ / _` |/ _` | __/ _ \ | __/ _ \/ _` | '_ ` _ \
| |_| | |_) | (_| | (_| | ||  __/ | ||  __/ (_| | | | | | |
 \__,_| .__/ \__,_|\__,_|\__\___|  \__\___|\__,_|_| |_| |_|
      |_|

 ___  ___ ___  _ __ ___  ___
/ __|/ __/ _ \| '__/ _ \/ __|
\__ \ (_| (_) | | |  __/\__ \
|___/\___\___/|_|  \___||___/

"""

def update_team_scores(request, team, data=None, write=True):
    r"""
    Update team scores.

    If `data` is None, then the function is being called from the admin, meaning data is not being 
    sourced from the scorecard.  In that case, be sure and call `calculate_team_handicap_per_hole()`
    for the team.  
    """
    # Clear out auto-calculated fields.
    team.holes_played = 0
    team.current_raw_score = 0
    team.current_rel_score = 0
    team.proj_adj_rel_score = 0
    team.final_adj_raw_score = 0
    team.final_adj_rel_score = 0
    team.sortable_score = ''
    team.rank = 0

    if data is not None:
        # Update team score data from scorecard input data.
        if bool(data["TeamInfo"]["Score"]["1"]["Valid"]): team.hole1 = data["TeamInfo"]["Score"]["1"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["2"]["Valid"]): team.hole2 = data["TeamInfo"]["Score"]["2"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["3"]["Valid"]): team.hole3 = data["TeamInfo"]["Score"]["3"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["4"]["Valid"]): team.hole4 = data["TeamInfo"]["Score"]["4"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["5"]["Valid"]): team.hole5 = data["TeamInfo"]["Score"]["5"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["6"]["Valid"]): team.hole6 = data["TeamInfo"]["Score"]["6"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["7"]["Valid"]): team.hole7 = data["TeamInfo"]["Score"]["7"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["8"]["Valid"]): team.hole8 = data["TeamInfo"]["Score"]["8"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["9"]["Valid"]): team.hole9 = data["TeamInfo"]["Score"]["9"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["10"]["Valid"]): team.hole10 = data["TeamInfo"]["Score"]["10"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["11"]["Valid"]): team.hole11 = data["TeamInfo"]["Score"]["11"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["12"]["Valid"]): team.hole12 = data["TeamInfo"]["Score"]["12"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["13"]["Valid"]): team.hole13 = data["TeamInfo"]["Score"]["13"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["14"]["Valid"]): team.hole14 = data["TeamInfo"]["Score"]["14"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["15"]["Valid"]): team.hole15 = data["TeamInfo"]["Score"]["15"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["16"]["Valid"]): team.hole16 = data["TeamInfo"]["Score"]["16"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["17"]["Valid"]): team.hole17 = data["TeamInfo"]["Score"]["17"]["RawScore"]
        if bool(data["TeamInfo"]["Score"]["18"]["Valid"]): team.hole18 = data["TeamInfo"]["Score"]["18"]["RawScore"]
    else:
        # If `data` is None, then the function is being called from the admin, meaning data is not 
        # being sourced from the scorecard so be sure and call `calculate_team_handicap_per_hole()`
        # for the team.  This is needed because we need to access `request.session['team']['hole_handicap']`.
        calculate_team_handicap_per_hole(request, team)

    # Get variables from session.
    cache_session = request.session['cache']
    team_session = request.session['team']
    team_hole_handicap = team_session['hole_handicap']

    # Sortable score begins as a list of handicap rated holes, 1 to 18.  Initial value is set to
    # " " for all handicap holes.  As a hole is played and its value recorded, the " " will be 
    # replaced by the raw score minus 1.  Why?  Because we will then end up with an array of 
    # numbers 0 to 9 representing the handicap of the hole, hardest to easiest.  The values are 
    # joined to form an 18 character string.  Later, we will append the adjusted score, append the 
    # team name.  The result is a sortable column that gives us the team ranking. In the event of 
    # ties, where multiple teams have the same adjusted scored, the field allows us to do a simple
    # scorecard playoff. 
    sortable_score = [' ' for i in range(0, 18)]

    # Cycle through each hole.  Get the team's score, if defined, and update the current and 
    # projected team scores.  
    for hole_int in range(1, 19):
        # Get some keys.
        hole_str = str(hole_int)
        hole_rank = cache_session['hole'][hole_str]['handicap']
        field_name = f'hole{hole_int}'
        # In Django, this is how we access the field data without using the instance attribute i.e.
        # hole1, hole2, etc., etc.
        field_object = team._meta.get_field(field_name)
        field_value = field_object.value_from_object(team)
        # Get the score for the hole.
        score = field_value
        # If the score is defined and greater than 0, process it.
        if score is not None and score > 0:
            sortable_score[hole_rank-1] = str(score - 1)
            team.holes_played += 1
            par_rel_score = score - cache_session['hole'][hole_str]['par']
            handicap_adjust_this_hole = team_hole_handicap[hole_str]
            team.current_raw_score += score
            team.current_rel_score += par_rel_score
            team.proj_adj_rel_score += par_rel_score - handicap_adjust_this_hole
    
    # If team has played all 18 holes, they are done.  
    if team.holes_played == 18:
        team.final_adj_raw_score = team.current_raw_score - team.handicap
        team.final_adj_rel_score = team.current_raw_score - team.handicap - cache_session['course']['par']
        team.sortable_score = f"""{team.final_adj_raw_score:03d}:{team.history:03d}:{''.join(sortable_score)}:{team.current_raw_score:03d}:{team.name}"""
        team.score_calculated = True

    # Save the data.
    if write:
        team.updated_on = unchained.get_localized_datetime_now()
        team.save()
        return True

    return False

r"""
            _     _           _                                    _
  __ _  ___| |_  | |__   ___ | | ___    __ ___      ____ _ _ __ __| |___
 / _` |/ _ \ __| | '_ \ / _ \| |/ _ \  / _` \ \ /\ / / _` | '__/ _` / __|
| (_| |  __/ |_  | | | | (_) | |  __/ | (_| |\ V  V / (_| | | | (_| \__ \
 \__, |\___|\__| |_| |_|\___/|_|\___|  \__,_| \_/\_/ \__,_|_|  \__,_|___/
 |___/

"""

def get_hole_awards(request):
    from .models import Award
    from django.utils.timezone import localtime
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    show_leader_board = False
    if request.user.is_authenticated and request.user.is_staff:
        show_leader_board = True
    elif tournament.show_leader_board:
        show_leader_board = True
    if not show_leader_board:
        return None
    awards = Award.objects.order_by('award_type', '-created_on').all()
    data = {}
    for award in awards:
        if award.award_type not in data: data[award.award_type] = []
        created_at = localtime(award.created_on)
        data[award.award_type].append(dict(
            team=award.team.name,
            player=award.player,
            # createdOn=str(created_at),
            createdOn=str(created_at.strftime("%I:%M:%S")),
            isBest=award.is_best
        ))
    return data

r"""
            _     _                _             _                         _
  __ _  ___| |_  | | ___  __ _  __| | ___ _ __  | |__   ___   __ _ _ __ __| |
 / _` |/ _ \ __| | |/ _ \/ _` |/ _` |/ _ \ '__| | '_ \ / _ \ / _` | '__/ _` |
| (_| |  __/ |_  | |  __/ (_| | (_| |  __/ |    | |_) | (_) | (_| | | | (_| |
 \__, |\___|\__| |_|\___|\__,_|\__,_|\___|_|    |_.__/ \___/ \__,_|_|  \__,_|
 |___/

"""

def get_leader_board(request, my_team):
    r"""
    Get the leader board data.
    """
    our_data = {}
    # Get `tournament` info.
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    # Initialize `show_leader_board` to false.
    show_leader_board = False
    # Always show leader board for staff...
    if request.user.is_authenticated and request.user.is_staff:
        show_leader_board = True
    # ... otherwise only show leader board if `tournament.show_leader_board` is true.
    elif tournament.show_leader_board:
        show_leader_board = True
    # Get all teams data.
    teams = Team.objects.filter(active=True).all()
    # Update `our_data` dictionary.
    for team in teams:
        if team == my_team:
            our_data = dict(
                name=team.name,
                player1=team.player1,
                player2=team.player2,
                player3=team.player3,
                handicap=f'+{team.handicap}' if team.handicap >= 0 else f'{team.handicap}',
                holes_played=team.holes_played,
                current_rel_score=f'+{team.current_rel_score}' if team.current_rel_score >= 0 else f'{team.current_rel_score}',
                proj_adj_rel_score=f'+{team.proj_adj_rel_score}' if team.proj_adj_rel_score >= 0 else f'{team.proj_adj_rel_score}',
            )
    # If `show_leader_board` is False, return None.
    if not show_leader_board:
        return None, our_data
    # Variable `data` will hold all team data, later to be sorted and saved as `sorted_data`.
    data = {}
    # Cycle through all teams...
    for team in teams:
        # Set `is_my_team` to True if processing data for the user's team.
        is_my_team = True if team == my_team else False
        # If the data has already been entered on at least one hole...
        if team.holes_played is not None and team.holes_played > 0:
            key = f'{300+team.proj_adj_rel_score}.{0 if is_my_team else 1}.{team.name}'
            data[key] = dict(
                name=team.name,
                player1=team.player1,
                player2=team.player2,
                player3=team.player3,
                handicap=f'+{team.handicap}' if team.handicap >= 0 else f'{team.handicap}',
                holes_played=team.holes_played,
                current_rel_score=f'+{team.current_rel_score}' if team.current_rel_score >= 0 else f'{team.current_rel_score}',
                proj_adj_rel_score=f'+{team.proj_adj_rel_score}' if team.proj_adj_rel_score >= 0 else f'{team.proj_adj_rel_score}',
                is_my_team=is_my_team,
            )
        # ...else if data has not already been entered for team on at least one hole...
        else:
            key = f'{600+team.proj_adj_rel_score}.{0 if is_my_team else 1}.{team.name}'
            data[key] = dict(
                name=team.name,
                player1=team.player1,
                player2=team.player2,
                player3=team.player3,
                handicap=f'+{team.handicap}' if team.handicap >= 0 else f'{team.handicap}',
                holes_played=team.holes_played,
                current_rel_score='-',
                proj_adj_rel_score='-',
                is_my_team=is_my_team,
            )
    # Sort the team `data` and return as `sorted_data`.
    cnt = 1
    rank = 1
    last_proj_adj_rel_score = -1000
    sorted_data = []
    for key in sorted(data):
        if last_proj_adj_rel_score == data[key]['proj_adj_rel_score']:
            data[key]['rank'] = rank
        else:
            rank = cnt
            data[key]['rank'] = rank
        sorted_data.append(data[key])
        cnt += 1
        last_proj_adj_rel_score = data[key]['proj_adj_rel_score']
    return sorted_data, our_data

r"""
  __ _             _ _
 / _(_)_ __   __ _| (_)_______
| |_| | '_ \ / _` | | |_  / _ \
|  _| | | | | (_| | | |/ /  __/
|_| |_|_| |_|\__,_|_|_/___\___|

 _                                                    _
| |_ ___  _   _ _ __ _ __   __ _ _ __ ___   ___ _ __ | |_
| __/ _ \| | | | '__| '_ \ / _` | '_ ` _ \ / _ \ '_ \| __|
| || (_) | |_| | |  | | | | (_| | | | | | |  __/ | | | |_
 \__\___/ \__,_|_|  |_| |_|\__,_|_| |_| |_|\___|_| |_|\__|

                     _ _
 _ __ ___  ___ _   _| | |_ ___
| '__/ _ \/ __| | | | | __/ __|
| | |  __/\__ \ |_| | | |_\__ \
|_|  \___||___/\__,_|_|\__|___/

"""

def finalize_tournament_results(request):
    data = {'teams': [], 'award': {}}
    teams = Team.objects.filter(Q(active=True) & Q(holes_played=18)).order_by('sortable_score').all()
    for team in teams:
        d = dictate(team.__dict__)
        data['teams'].append(d)
    data['award'] = get_hole_awards(request)
    return data

r"""
 _                         _             _
| |_ ___  __ _ _ __ ___   | | ___   __ _(_)_ __
| __/ _ \/ _` | '_ ` _ \  | |/ _ \ / _` | | '_ \
| ||  __/ (_| | | | | | | | | (_) | (_| | | | | |
 \__\___|\__,_|_| |_| |_| |_|\___/ \__, |_|_| |_|
                                   |___/
"""

def team_login(request, team):
    from .models import TeamAccess
    token = f'{team.name}.{team.id:08d}.{epoch()}.{ru.rint(10000, 99999)}'
    TeamAccess.objects.create(token=token, team=team)
    if 'team' not in request.session:
        request.session['team'] = {}
    request.session['team']['token'] = token
    from .util import calculate_team_handicap_per_hole
    calculate_team_handicap_per_hole(request, team)

r"""
                 _                              _ _
 _ __ ___   __ _| | _____   _ __ ___  ___ _   _| | |_ ___
| '_ ` _ \ / _` | |/ / _ \ | '__/ _ \/ __| | | | | __/ __|
| | | | | | (_| |   <  __/ | | |  __/\__ \ |_| | | |_\__ \
|_| |_| |_|\__,_|_|\_\___| |_|  \___||___/\__,_|_|\__|___/

       _     _ _     _
__   _(_)___(_) |__ | | ___
\ \ / / / __| | '_ \| |/ _ \
 \ V /| \__ \ | |_) | |  __/
  \_/ |_|___/_|_.__/|_|\___|

"""

def make_results_visible(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.show_results = True
    tournament.save()
    compile_cache(request)

r"""
                 _                              _ _
 _ __ ___   __ _| | _____   _ __ ___  ___ _   _| | |_ ___
| '_ ` _ \ / _` | |/ / _ \ | '__/ _ \/ __| | | | | __/ __|
| | | | | | (_| |   <  __/ | | |  __/\__ \ |_| | | |_\__ \
|_| |_| |_|\__,_|_|\_\___| |_|  \___||___/\__,_|_|\__|___/

 _            _     _ _     _
(_)_ ____   _(_)___(_) |__ | | ___
| | '_ \ \ / / / __| | '_ \| |/ _ \
| | | | \ V /| \__ \ | |_) | |  __/
|_|_| |_|\_/ |_|___/_|_.__/|_|\___|

"""

def make_results_invisible(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.show_results = False
    tournament.save()
    compile_cache(request)

r"""
                  _     _                                                 _
  ___ _ __   __ _| |__ | | ___   ___  ___ ___  _ __ ___  ___ __ _ _ __ __| |
 / _ \ '_ \ / _` | '_ \| |/ _ \ / __|/ __/ _ \| '__/ _ \/ __/ _` | '__/ _` |
|  __/ | | | (_| | |_) | |  __/ \__ \ (_| (_) | | |  __/ (_| (_| | | | (_| |
 \___|_| |_|\__,_|_.__/|_|\___| |___/\___\___/|_|  \___|\___\__,_|_|  \__,_|

          _ _ _   _
  ___  __| (_) |_(_)_ __   __ _
 / _ \/ _` | | __| | '_ \ / _` |
|  __/ (_| | | |_| | | | | (_| |
 \___|\__,_|_|\__|_|_| |_|\__, |
                          |___/

"""

def enable_scorecard_editing(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.enable_team_input = True
    tournament.save()
    compile_cache(request)

r"""
     _ _           _     _                                                 _
  __| (_)___  __ _| |__ | | ___   ___  ___ ___  _ __ ___  ___ __ _ _ __ __| |
 / _` | / __|/ _` | '_ \| |/ _ \ / __|/ __/ _ \| '__/ _ \/ __/ _` | '__/ _` |
| (_| | \__ \ (_| | |_) | |  __/ \__ \ (_| (_) | | |  __/ (_| (_| | | | (_| |
 \__,_|_|___/\__,_|_.__/|_|\___| |___/\___\___/|_|  \___|\___\__,_|_|  \__,_|

          _ _ _   _
  ___  __| (_) |_(_)_ __   __ _
 / _ \/ _` | | __| | '_ \ / _` |
|  __/ (_| | | |_| | | | | (_| |
 \___|\__,_|_|\__|_|_| |_|\__, |
                          |___/
"""

def disable_scorecard_editing(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.enable_team_input = False
    tournament.save()
    compile_cache(request)

r"""
                  _     _        _
  ___ _ __   __ _| |__ | | ___  | |_ ___  __ _ _ __ ___
 / _ \ '_ \ / _` | '_ \| |/ _ \ | __/ _ \/ _` | '_ ` _ \
|  __/ | | | (_| | |_) | |  __/ | ||  __/ (_| | | | | | |
 \___|_| |_|\__,_|_.__/|_|\___|  \__\___|\__,_|_| |_| |_|


  __ _  ___ ___ ___  ___ ___
 / _` |/ __/ __/ _ \/ __/ __|
| (_| | (_| (_|  __/\__ \__ \
 \__,_|\___\___\___||___/___/

"""

def enable_team_access(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.enable_team_access = True
    tournament.save()
    compile_cache(request)

r"""
     _ _           _     _        _
  __| (_)___  __ _| |__ | | ___  | |_ ___  __ _ _ __ ___
 / _` | / __|/ _` | '_ \| |/ _ \ | __/ _ \/ _` | '_ ` _ \
| (_| | \__ \ (_| | |_) | |  __/ | ||  __/ (_| | | | | | |
 \__,_|_|___/\__,_|_.__/|_|\___|  \__\___|\__,_|_| |_| |_|


  __ _  ___ ___ ___  ___ ___
 / _` |/ __/ __/ _ \/ __/ __|
| (_| | (_| (_|  __/\__ \__ \
 \__,_|\___\___\___||___/___/

"""

def disable_team_access(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.enable_team_access = False
    tournament.save()
    compile_cache(request)

r"""
                  _     _         _                _
  ___ _ __   __ _| |__ | | ___   | | ___  __ _  __| | ___ _ __
 / _ \ '_ \ / _` | '_ \| |/ _ \  | |/ _ \/ _` |/ _` |/ _ \ '__|
|  __/ | | | (_| | |_) | |  __/  | |  __/ (_| | (_| |  __/ |
 \___|_| |_|\__,_|_.__/|_|\___|  |_|\___|\__,_|\__,_|\___|_|

 _                         _
| |__   ___   __ _ _ __ __| |
| '_ \ / _ \ / _` | '__/ _` |
| |_) | (_) | (_| | | | (_| |
|_.__/ \___/ \__,_|_|  \__,_|

"""

def enable_leader_board(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.show_leader_board = True
    tournament.save()
    compile_cache(request)

r"""
     _ _           _     _         _                _
  __| (_)___  __ _| |__ | | ___   | | ___  __ _  __| | ___ _ __
 / _` | / __|/ _` | '_ \| |/ _ \  | |/ _ \/ _` |/ _` |/ _ \ '__|
| (_| | \__ \ (_| | |_) | |  __/  | |  __/ (_| | (_| |  __/ |
 \__,_|_|___/\__,_|_.__/|_|\___|  |_|\___|\__,_|\__,_|\___|_|

 _                         _
| |__   ___   __ _ _ __ __| |
| '_ \ / _ \ / _` | '__/ _` |
| |_) | (_) | (_| | | | (_| |
|_.__/ \___/ \__,_|_|  \__,_|

"""

def disable_leader_board(request):
    from .models import Tournament
    tournament = Tournament.objects.filter(active=True)[0]
    tournament.show_leader_board = False
    tournament.save()
    compile_cache(request)

r"""
                _     _
  __ _ _ __ ___| |__ (_)_   _____
 / _` | '__/ __| '_ \| \ \ / / _ \
| (_| | | | (__| | | | |\ V /  __/
 \__,_|_|  \___|_| |_|_| \_/ \___|

 _                                                    _
| |_ ___  _   _ _ __ _ __   __ _ _ __ ___   ___ _ __ | |_
| __/ _ \| | | | '__| '_ \ / _` | '_ ` _ \ / _ \ '_ \| __|
| || (_) | |_| | |  | | | | (_| | | | | | |  __/ | | | |_
 \__\___/ \__,_|_|  |_| |_|\__,_|_| |_| |_|\___|_| |_|\__|

"""

def archive_tournament(request):
    
    from .models import Tournament, Team, History
    tournament = Tournament.objects.filter(active=True)[0]
    teams = Team.objects.filter(active=True).order_by('sortable_score').all()
    History.objects.filter(tournament=tournament).delete()

    # Get all table fields.
    fields = Team._meta.get_fields()
    
    # Cycle through all fields and update `columns` list.  Each item in list will be a column dict
    # with keys 'title', 'field', 'width' and 'editor'.  Also update `size` dict.
    for team in teams:
        data = {}
        data['tournament'] = tournament
        for field in fields:
            if field.name == 'id': continue
            if field.many_to_many: continue
            if field.one_to_many: continue
            if field.one_to_one: continue
            field_name = field.name
            data[field_name] = getattr(team, field_name)
        history = History.objects.create(**data)
        history.save()

r"""
 _____         _   ____        _
|_   _|__  ___| |_|  _ \  __ _| |_ __ _
  | |/ _ \/ __| __| | | |/ _` | __/ _` |
  | |  __/\__ \ |_| |_| | (_| | || (_| |
  |_|\___||___/\__|____/ \__,_|\__\__,_|

"""

class TestData():
    r'''
    The `TestData` class is a test harness used for unit testing.  

    ## Usage

    ```python
    # In view function `Home()`...
    test = TestData()
    test.add(view, 'Home')
    test.save()

    # In test function...
    test = TestData(reset=False)
    self.assertTrue(test.data['view'] == 'Home')
    ```

    Methods `test.add()` and `test.save()` do nothing unless `settings.TESTING` is True.  If 
    `settings.TESTING` is True then `test.add()` lets you add data to `test.data` and `test.save()`
    saves the data as a JSON file.  When you subsequently do:

    ```python
    test = TestData(reset=False)
    ```

    the JSON file will be read.  You can then test the view data in `test.data`.
    '''

    def __init__(self, reset=True, **kwarg):
        self.data = kwarg
        if not settings.TESTING: return
        self.file = fs.fix(fs.join(fs.dirname(settings.DATABASES['default']['NAME']), '.test.json'))
        if reset:
            if fs.exists(self.file): fs.unlink(self.file)
        else:
            if fs.exists(self.file):
                txt = fs.read(self.file, to_string=True)
                self.data = json.loads(txt)
    
    def add(self, key, val):
        if not settings.TESTING: return
        if key in self.data and type(self.data[key]) == list:
            self.data[key].append(val)
        else:
            self.data[key] = val

    def save(self):
        if not settings.TESTING: return
        txt = json.dumps(self.data, indent=2)
        fs.writeif(self.file, txt)


