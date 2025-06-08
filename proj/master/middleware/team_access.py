from django.conf import settings
from main.models import TeamAccess, Cache
import ru
import json

class TeamAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        team_access_granted = False

        team = request.session['team'] if 'team' in request.session else {'access': False}

        if 'token' in team:
            session_team_token = team['token']
            try:
                team_access = TeamAccess.objects.get(token=session_team_token)
                if settings.DEBUG: print(f'Team {team_access.team.name} access is granted.')
                team['name'] = team_access.team.name
                team_info = request.session['cache']['team'][team['name']]
                players = []
                if 'player1' in team_info and len(team_info['player1']) > 0: players.append(team_info['player1'])
                if 'player2' in team_info and len(team_info['player2']) > 0: players.append(team_info['player2'])
                if 'player3' in team_info and len(team_info['player3']) > 0: players.append(team_info['player3'])
                team['players'] = ru.join_items(players, last_join=' and ')
                team['player_list'] = players
                team['id'] = team_access.team.id
                team['access'] = True
                team_access_granted = True
            except:
                pass
        if not team_access_granted:
            team = {'access': False}
        request.session['team'] = team

        cache = Cache.objects.first()
        request.session['cache'] = json.loads(cache.data)

        # Required statement.  Do not remove!!!
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response