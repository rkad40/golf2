from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
import json
import arrow
import ru
import yaml
from cronos import epoch

def dictate(data):
    d = {}
    for key in data:
        if key.startswith('_'): continue
        val = data[key]
        stype = ru.stype(data[key])
        if stype not in ['int', 'str', 'bool', 'float']:
            val = str(val)
        d[key] = val
    return d
        
def compile():
    from main.models import Hole, Course, Tournament, Team, Cache
    data = {}
    tournament = Tournament.objects.filter(active=True)[0]
    data['tournament'] = dictate(tournament.__dict__)
    data['course'] = dictate(tournament.course.__dict__)
    data['hole'] = {}
    for hole in Hole.objects.filter(course_id=data['tournament']['course_id']).all().values():
        hole['yards'] = hole[tournament.play_from]
        num = int(hole['hole'])
        for key in ['id', 'course_id', 'gold', 'blue', 'white', 'red']:
            try: del hole[key]
            except: pass
        data['hole'][num] = dictate(hole)
    data['team'] = {}
    for team in Team.objects.filter(active=True).all().values():
        name = team['name']
        data['team'][name] = {}
        for key in ['player1', 'player2', 'player3', 'handicap', 'start_hole']:
            data['team'][name][key] = team[key]
        data['team'][name]['str_handicap'] = f"""+{data['team'][name]['handicap']}""" if data['team'][name]['handicap'] >= 0 else f"""{data['team'][name]['handicap']}"""
    print(json.dumps(data, indent=2))
    
    json_txt = json.dumps(data, indent=None, separators=(',', ':'))
    cache = None
    try: cache = Cache.objects.first()
    except: pass
    if cache is not None:
        Cache.objects.filter(~Q(id=cache.id)).delete()
        cache.data = json_txt
        cache.epoch = epoch(int)
        cache.save()
    else:
        Cache.objects.create(data=json_txt, epoch=epoch(int))
        

    print(handicap)
    print()
    

class Command(BaseCommand):
    help = 'Basic prod tests'
    def handle(self, *args, **kwargs):
        from main.models import Team
        from main.util import update_team_scores
        team = Team.objects.get(name='01B')
        update_team_scores(team)


