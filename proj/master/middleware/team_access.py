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

        cache = Cache.objects.first()
        if cache is None or cache.data is None:
            try:
                from main.util import compile_cache
                compile_cache(request)
                cache = Cache.objects.first()
            except Exception as err:
                if settings.DEBUG: print(f'Cache could not be compiled. {err}')
        try:
            request.session['cache'] = json.loads(cache.data) if cache is not None and cache.data is not None else {}
        except Exception as err:
            if settings.DEBUG: print(f'Cache data could not be loaded. {err}')
            try:
                from main.util import compile_cache
                compile_cache(request)
                cache = Cache.objects.first()
                request.session['cache'] = json.loads(cache.data) if cache is not None and cache.data is not None else {}
            except Exception as err:
                if settings.DEBUG: print(f'Cache could not be repaired. {err}')
                request.session['cache'] = {}

        team = request.session['team'] if 'team' in request.session else {'access': False}

        if 'token' in team:
            session_team_token = team['token']
            try:
                team_access = TeamAccess.objects.get(token=session_team_token)
                if settings.DEBUG: print(f'Team {team_access.team.name} access is granted.')
                team['name'] = team_access.team.name
                team_info = request.session.get('cache', {}).get('team', {}).get(team['name'], {})
                players = []
                for player_key in ['player1', 'player2', 'player3']:
                    player = team_info.get(player_key, getattr(team_access.team, player_key))
                    if player is not None and len(player) > 0: players.append(player)
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

        # Required statement.  Do not remove!!!
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
