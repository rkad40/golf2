from apps.main.util import dictate
import fs, json, sys
from unchained import get_localized_datetime
from django.test import TestCase, RequestFactory, override_settings
from django.conf import settings
from main.util import TestData
from bs4 import BeautifulSoup
from django.urls import reverse
from django.test import Client
from rex import Rex

# sys.path.append('..')

# Create your tests here.

TABLE_TEAM_DATA = r'''name	player1	player2	player3	start_hole	handicap	history	active
01A	Colton Tucker	Samuel Tucker	Ronnie Tucker	1	8	90	TRUE
01B	Gary Tucker	Scott Tucker	Jeremy Tucker	1	11	0	TRUE
14A	Bobby Goertz	Cliff Goertz	Steve Darilek	14	3	60	TRUE
14B	John Allen Goertz	TBD	TBD	14	15	0	TRUE
15A	Jon Bartsch	Chris Fohn	Jackie Tucker	15	3	20	TRUE
15B	Greg Friske	Nicholas Friske	Bill Kadura	15	15	0	TRUE
16A	John Kadura	Kris Klaus	Brian Klaus	16	9	0	TRUE
16B	Scott Rascke	Justin Fohn	Clint Osborne	16	10	0	TRUE
17A	Elmer Goertz	Darren Goertz	Christopher Goertz	17	9	0	TRUE
17B	Richie Fiebrich	Steve Fiebrich	Kevin Klaus	17	6	45	TRUE
17C	Stephen Klaus	Adam Goertz	Kevin Wolf	17	13	0	TRUE
17D	Bradley Nutt	Kaycee Nutt	Carter Nutt	17	5	0	TRUE
18A	Kenny Hoffman	Joe Hoffman	Toby Hoffman	18	9	45	TRUE
18B	John Altum	Shawn Altum	Rodney Kadura	18	8	0	TRUE
'''

JSON_TEAM_DATA = r'''[{"name": "01A", "player1": "Colton Tucker", "player2": "Samuel Tucker", "player3": "Ronnie Tucker", "start_hole": 1, "handicap": 8, "history": 90, "active": true}, {"name": "01B", "player1": "Gary Tucker", "player2": "Scott Tucker", "player3": "Jeremy Tucker", "start_hole": 1, "handicap": 11, "history": 0, "active": true}, {"name": "14A", "player1": "Bobby Goertz", "player2": "Cliff Goertz", "player3": "Steve Darilek", "start_hole": 14, "handicap": 3, "history": 60, "active": true}, {"name": "14B", "player1": "John Allen Goertz", "player2": "TBD", "player3": "TBD", "start_hole": 14, "handicap": 15, "history": 0, "active": true}, {"name": "15A", "player1": "Jon Bartsch", "player2": "Chris Fohn", "player3": "Jackie Tucker", "start_hole": 15, "handicap": 3, "history": 20, "active": true}, {"name": "15B", "player1": "Greg Friske", "player2": "Nicholas Friske", "player3": "Bill Kadura", "start_hole": 15, "handicap": 15, "history": 0, "active": true}, {"name": "16A", "player1": "John Kadura", "player2": "Kris Klaus", "player3": "Brian Klaus", "start_hole": 16, "handicap": 9, "history": 0, "active": true}, {"name": "16B", "player1": "Scott Rascke", "player2": "Justin Fohn", "player3": "Clint Osborne", "start_hole": 16, "handicap": 10, "history": 0, "active": true}, {"name": "17A", "player1": "Elmer Goertz", "player2": "Darren Goertz", "player3": "Christopher Goertz", "start_hole": 17, "handicap": 9, "history": 0, "active": true}, {"name": "17B", "player1": "Richie Fiebrich", "player2": "Steve Fiebrich", "player3": "Kevin Klaus", "start_hole": 17, "handicap": 6, "history": 45, "active": true}, {"name": "17C", "player1": "Stephen Klaus", "player2": "Adam Goertz", "player3": "Kevin Wolf", "start_hole": 17, "handicap": 13, "history": 0, "active": true}, {"name": "17D", "player1": "Bradley Nutt", "player2": "Kaycee Nutt", "player3": "Carter Nutt", "start_hole": 17, "handicap": 5, "history": 0, "active": true}, {"name": "18A", "player1": "Kenny Hoffman", "player2": "Joe Hoffman", "player3": "Toby Hoffman", "start_hole": 18, "handicap": 9, "history": 45, "active": true}, {"name": "18B", "player1": "John Altum", "player2": "Shawn Altum", "player3": "Rodney Kadura", "start_hole": 18, "handicap": 8, "history": 0, "active": true}]'''

class MainTest(TestCase):

    @override_settings(TESTING=True)
    def setUp(self):
        r'''
        Run setup for each test.

        - Create database.
        - Define admin superuser `self.admin`.
        - Define cache `self.cache`.
        '''
        self.factory = RequestFactory()
        self.test_dir = fs.fix(fs.join(fs.dirname(settings.DATABASES['default']['NAME']), 'test', '100'))
        from main.models import Team, Award, Cache, Course, Hole, Tournament
        from access.models import User
        from book.models import Article
        self.data_to_db(Team, 'main_team.json', date_time_fields=['updated_on'])
        self.data_to_db(Award, 'main_award.json', date_time_fields=['created_on'])
        self.data_to_db(Cache, 'main_cache.json', date_time_fields=[])
        self.data_to_db(Course, 'main_course.json', date_time_fields=[])
        self.data_to_db(Hole, 'main_hole.json', date_time_fields=[])
        self.data_to_db(Tournament, 'main_tournament.json', date_time_fields=['date_time'])
        self.data_to_db(User, 'access_user.json', date_time_fields=['date_joined', 'last_login'])
        self.data_to_db(Article, 'book_article.json', date_time_fields=[])
        self.admin = User.objects.filter(username='admin')[0]
        from main.models import Cache
        cache = Cache.objects.first()
        self.cache = json.loads(cache.data)
    
    def data_to_db(self, model, name, date_time_fields=[]):
        r'''
        Convert raw JSON data table to database table.
        '''
        data = json.loads(fs.read(fs.join(self.test_dir, name), to_string=True))
        for row in data:
            for field in date_time_fields:
                row[field] = get_localized_datetime(row[field])
            model.objects.create(**row)

    r'''
     _____         _
    |_   _|__  ___| |_ ___
      | |/ _ \/ __| __/ __|
      | |  __/\__ \ |_\__ \
      |_|\___||___/\__|___/

    '''

    @override_settings(TESTING=True)
    def test_001_views_Home(self):
        r'''
        Test home page.
        '''

        # Test URLs.
        self.assertEqual(reverse('home'), '/home')
        self.assertEqual(reverse('root'), '/')
        self.assertEqual(reverse('home-next'), '/home/next')
        self.assertEqual(reverse('home-prev'), '/home/prev')

        # Generate request.
        request = self.factory.get('')
        request.user = self.admin

        # Test response.
        from main.views import Home 
        response = Home(request)
        self.assertEqual(response.status_code, 200)

        # Test TestData.
        test = TestData(reset=False)
        self.assertTrue(test.data['view'] == 'Home')

        # Test HTML.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament')
        self.assertEqual(len(test.data['articles']), 8)

    @override_settings(TESTING=True)
    def test_002_views_ScoreCard(self):
        r'''
        Test scorecard page.
        '''

        # Test URLs.
        self.assertEqual(reverse('score-card'), '/team/scorecard')

        # Generate request.
        request = self.factory.get('')
        request.user = self.admin

        # Create session and assign to request. 
        session = {}
        session['cache'] = self.cache
        session['team'] = dict(id=154)
        setattr(request, 'session', session)

        # Test response.
        from main.views import ScoreCard 
        response = ScoreCard(request)
        self.assertEqual(response.status_code, 200)

        # Test HTML.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Scorecard')
        tag = soup.section
        self.assertEqual(tag['id'], 'TestHook')
        self.assertEqual(tag.text, 'score-card')

        # Test TestData.
        test = TestData(reset=False)
        self.assertEqual(test.data['view'], 'ScoreCard')
        self.assertEqual(test.data['team-player1'], 'Kenny Hoffman')

    @override_settings(TESTING=True)
    def test_003_util_team_login(self):
        r'''
        Test team login (via `team_login()` function).
        '''

        # Generate request.
        request = self.factory.get('')

        from main.models import Team
        team = Team.objects.get(name='01A')

        self.assertEqual(team.name, '01A')
        self.assertEqual(team.player1, 'Kenny Hoffman')

        from main.util import team_login

        # Create session and assign to request. 
        session = {}
        session['cache'] = self.cache
        setattr(request, 'session', session)

        self.assertNotIn('team', request.session)
        team_login(request, team)
        self.assertIn('team', request.session)
        self.assertIn('token', request.session['team'])

        rex = Rex()
        self.assertTrue(rex.m(request.session['team']['token'], r'^01A\.00000154\.\d+.\d+.\d+$', ''))

    @override_settings(TESTING=True)
    def test_004_views_TeamLogin(self):
        r'''
        Test team login (from login page).
        '''

        # Generate request.
        request = self.factory.get('')

        from main.forms import TeamLoginForm
        form = TeamLoginForm()
        def is_valid(): return True
        setattr(form, 'is_valid', is_valid)
        setattr(form, 'cleaned_data', dict(team='01A', password='tee247'))

        session = {}
        session['cache'] = self.cache

        request.method = 'POST'
        request.user = self.admin
        setattr(request, 'test_form_debug', form)
        setattr(request, 'session', session)

        from main.views import TeamLogin
        TeamLogin(request)

        test = TestData(reset=False)
        self.assertDictEqual(test.data, {'view': 'TeamLogin', 'form-is-valid': True, 'players': ['Kenny Hoffman', 'Joe Hoffman', 'Robyn Hoffman']})

    @override_settings(TESTING=True)
    def test_005_views_TeamLoginForm(self):
        r'''
        Test team login (from team login form).
        
        This is a bug fix test.  Previously, if a player was not defined, it would cause a login error because the 
        algorithm was attempting to do a len() operation on None. 
        '''

        from main.models import Team
        team = Team.objects.get(name='01A')

        self.assertEqual(team.name, '01A')
        self.assertEqual(team.player2, 'Joe Hoffman')
        team.player2 = None
        team.save()
        team = Team.objects.get(name='01A')
        self.assertIsNone(team.player2)

        # Generate request.
        request = self.factory.get('')

        from main.forms import TeamLoginForm
        form = TeamLoginForm()
        def is_valid(): return True
        setattr(form, 'is_valid', is_valid)
        setattr(form, 'cleaned_data', dict(team='01A', password='tee247'))

        session = {}
        session['cache'] = self.cache

        request.method = 'POST'
        request.user = self.admin
        setattr(request, 'test_form_debug', form)
        setattr(request, 'session', session)

        from main.views import TeamLogin
        TeamLogin(request)

        test = TestData(reset=False)
        self.assertDictEqual(test.data, {'view': 'TeamLogin', 'form-is-valid': True, 'players': ['Kenny Hoffman', 'Robyn Hoffman']})

    @override_settings(TESTING=True)
    def test_006_misc_staff_permissions(self):
        r'''
        Test anonymous user vs. staff permissions.
        '''

        # Generate request.
        request = self.factory.get('')
        from django.contrib.auth.models import AnonymousUser 
        
        request.user = AnonymousUser
        self.assertTrue(request.user.is_anonymous)
        self.assertTrue(request.user.is_authenticated)
        self.assertFalse(request.user.is_staff)

        request.user = self.admin
        self.assertFalse(request.user.is_anonymous)
        self.assertTrue(request.user.is_authenticated)
        self.assertTrue(request.user.is_staff)

    @override_settings(TESTING=True)
    def test_007_util_AjaxUpdateScores(self):
        r'''
        Test team sortable score calculation.  
        '''

        from main.util import dictate
        from main.admin import clear_team_scores, clear_sortable_scores, recalculate_team_scores
        from main.models import Team

        request = self.factory.get('')
        session = {}
        session['cache'] = self.cache
        session['team'] = {}
        request.method = 'POST'
        request.user = self.admin
        setattr(request, 'session', session)

        teams1 = []
        for team in Team.objects.order_by('name').all():
            data = dictate(team.__dict__)
            del data['updated_on']
            del data['proj_adj_rel_score']
            teams1.append(data)
            self.assertTrue(team.score_calculated)

        queryset = Team.objects.order_by('name').all()
        # clear_team_scores(None, request, queryset)
        clear_sortable_scores(None, request, queryset)

        for team in Team.objects.order_by('name').all():
            self.assertEqual(team.sortable_score, '')
            self.assertFalse(team.score_calculated)

        recalculate_team_scores(None, request, queryset)

        from main.views import AjaxUpdateScores
        request = self.factory.get('')
        AjaxUpdateScores(request)

        teams3 = []
        for team in Team.objects.order_by('name').all():
            data = dictate(team.__dict__)
            del data['proj_adj_rel_score']
            del data['updated_on']
            teams3.append(data)

        for team1, team3  in zip(teams1, teams3):
            self.assertDictEqual(team1, team3)

        
    @override_settings(TESTING=True)
    def test_008_url_response_status_code(self):
        r'''
        Test team sortable score calculation.  
        '''
        client = Client()
        self.assertEqual(client.get('/home').status_code, 200)
        self.assertEqual(client.get('/home/prev').status_code, 302)
        self.assertEqual(client.get('/home/next').status_code, 200)
        self.assertEqual(client.get('/team/scorecard/update').status_code, 200)
        self.assertEqual(client.get('/team/scorecard/01A').status_code, 302)

    @override_settings(TESTING=True)
    def test_009_views_login_success(self):
        r'''
        Correct team name and password.
        '''
        client = Client()
        response = client.post('/team/login', dict(team='01A', password='tee247'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament')
        results = soup.findAll("div", {"role" : "alert"})
        tag = str(results[0])
        self.assertTrue('<strong>Team 01A</strong>: Kenny Hoffman, Joe Hoffman and Robyn Hoffman.' in tag)

    @override_settings(TESTING=True)
    def test_010_views_login_success(self):
        r'''
        Correct team name and password, but each having incorrect case and lead/trailing spaces/tabs (which should be 
        ignored by the algorithm).
        '''
        client = Client()
        # Enter team name and password with mixed case, spaces and tabs.  This should work.  
        response = client.post('/team/login', dict(team=' 1a    ', password='   TeE247 '), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament')
        results = soup.findAll("div", {"role" : "alert"})
        tag = str(results[0])
        self.assertTrue('<strong>Team 01A</strong>: Kenny Hoffman, Joe Hoffman and Robyn Hoffman.' in tag)

    @override_settings(TESTING=True)
    def test_011_views_login_fail(self):
        r'''
        Fail login for incorrect password.
        '''
        client = Client()
        response = client.post('/team/login', dict(team='01A', password='tee248'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Team Login')
        results = soup.findAll("div", {"role" : "alert"})
        tag = str(results[0])
        self.assertTrue('<strong>ERROR</strong>: Invalid team name or password.  Please try again.' in tag)

    @override_settings(TESTING=True)
    def test_012_views_login_fail(self):
        r'''
        Fail login for invalid team name.
        '''
        client = Client()
        response = client.post('/team/login', dict(team='01C', password='tee247'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Team Login')
        results = soup.findAll("div", {"role" : "alert"})
        tag = str(results[0])
        self.assertTrue('<strong>ERROR</strong>: Invalid team name or password.  Please try again.' in tag)

    @override_settings(TESTING=True)
    def test_013_scorecard_view(self):
        r'''
        View scorecard after login success.
        '''
        rex = Rex()
        client = Client()
        response = client.post('/team/login', dict(team='01A', password='tee247'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament')
        results = soup.findAll("div", {"role" : "alert"})
        tag = str(results[0])
        self.assertTrue('<strong>Team 01A</strong>: Kenny Hoffman, Joe Hoffman and Robyn Hoffman.' in tag)
        response = client.post('/team/scorecard', follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        txt = rex.s(str(soup.findAll("section", {"id" : "TestHook"})[0]), '\<.*?\>', '', 'g=')
        self.assertEqual(txt, 'score-card')

    @override_settings(TESTING=True)
    def test_014_scorecard_view(self):
        r'''
        Deny scorecard view without login.
        '''
        rex = Rex()
        client = Client()
        response = client.post('/team/scorecard', follow=True)
        content = response.content.decode()
        # fs.write_file(fs.join(settings.BASE_DIR, 'debug.html'), content)
        soup = BeautifulSoup(content, 'html.parser')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('You must be logged in before you can access a team scorecard. Please go to Team Login and enter your team credentials to gain access.' in txt)

    @override_settings(TESTING=True)
    def test_015_logout(self):
        r'''
        Log out test.
        '''
        rex = Rex()
        client = Client()
        response = client.post('/team/login', dict(team='01A', password='tee247'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        results = soup.findAll("div", {"role" : "alert"})
        tag = str(results[0])
        self.assertTrue('<strong>Team 01A</strong>: Kenny Hoffman, Joe Hoffman and Robyn Hoffman.' in tag)
        response = client.post('/team/logout', follow=True)
        content = response.content.decode()
        # fs.write_file(fs.join(settings.BASE_DIR, 'debug.html'), content)
        soup = BeautifulSoup(content, 'html.parser')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('You have successfully logged out.' in txt)

    @override_settings(TESTING=True)
    def test_016_admin_login(self):
        r'''
        Log out test.
        '''
        rex = Rex()
        client = Client()
        # Fail login.
        response = client.post('/admin/login', dict(name='admin', password='krakapoo351x'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('ERROR: Invalid user name or password.' in txt)
        # Pass login.
        response = client.post('/admin/login', dict(name='admin', password='krakapoo351!'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('Hello admin. You have been successfully logged in.' in txt)
        # Logout.
        response = client.post('/user/logout', follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('You have been successfully logged out.' in txt)
        # Pass login with redirect.
        response = client.post('/admin/login', dict(name='admin', password='krakapoo351!', next_url='/admin/actions'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Admin Actions')
        # Logout.
        response = client.post('/user/logout', follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('You have been successfully logged out.' in txt)

        # fs.write_file(fs.join(settings.BASE_DIR, 'debug.html'), content)

    @override_settings(TESTING=True)
    def test_017_new_players(self):
        # Initialize
        def plusminus(val): 
            return f'+{val}' if val >= 0 else f'{val}' 
        from main.models import Cache, Team, Tournament, History, Award, Hole
        cache1 = Cache.objects.first()
        data1 = json.loads(cache1.data)
        self.assertEqual(data1['team']['01A']['player1'], 'Kenny Hoffman')
        rex = Rex()
        client = Client()
        # Pass login.
        response = client.post('/admin/login', dict(name='admin', password='krakapoo351!'), follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('Hello admin. You have been successfully logged in.' in txt)
        # Create table.
        data = dict(table='Team', course=1, data=TABLE_TEAM_DATA, data_type='tab')
        response = client.post('/create-table', data, follow=True)
        content = response.content.decode()
        data_txt = None
        if rex.m(content, r'^\s*var\s+table\s*=\s*new\s+Tabulator\s*\(\s*"#data-table"\s*,\s*(\{.*?\})\s*\);', 'ms'):
            temp_val = rex.d(1)
            if rex.m(temp_val, r'data:\s*(\[\s*\{.*?\}\s*\])', 'ms'):
                data_txt = rex.d(1)
        self.assertIsNotNone(data_txt)
        data1 = None
        try: 
            data1 = json.loads(data_txt)
        except Exception as err: 
            self.assertTrue(False, f'JSON data did not load: {err}')
        self.assertIsNotNone(data1)
        data2 = json.loads(JSON_TEAM_DATA)
        for d1,d2 in zip(data1, data2):
            self.assertDictEqual(d1, d2)
        # Test teams before new table creation.
        team = Team.objects.get(name='01A')
        self.assertEqual(team.name, '01A')
        self.assertEqual(team.player1, 'Kenny Hoffman')
        self.assertIsNotNone(team.password)
        # Verify table.
        data = dict(table='Team', course=1, data=TABLE_TEAM_DATA, data_type='tab')
        response = client.post('/verify-table', data, follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(content, 'html.parser')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('SUCCESS: Data saved.' in txt)
        # Test teams before new table creation.
        from main.models import Team
        team = Team.objects.get(name='01A')
        self.assertEqual(team.name, '01A')
        self.assertEqual(team.player1, 'Colton Tucker')
        self.assertIsNone(team.password)
        # Go to admin page.
        response = client.get('/admin/actions', {}, follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Admin Actions')
        # Go to admin page and create random passwords.
        data = dict(action='create-random-passwords')
        response = client.post('/admin/actions', data, follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Admin Actions')
        team = Team.objects.get(name='01A')
        self.assertEqual(team.name, '01A')
        self.assertEqual(team.player1, 'Colton Tucker')
        self.assertIsNotNone(team.password)
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('Random passwords added for 14 teams.' in txt)
        password1 = team.password
        # Try creating passwords again.  No passwords should be created because they already exist.
        data = dict(action='create-random-passwords')
        response = client.post('/admin/actions', data, follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Admin Actions')
        team = Team.objects.get(name='01A')
        self.assertEqual(team.name, '01A')
        self.assertEqual(team.player1, 'Colton Tucker')
        self.assertIsNotNone(team.password)
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('All valid teams already have passwords defined. No passwords added.' in txt)
        password2 = team.password
        self.assertEqual(password1, password2)
        # Compile cache.
        data = dict(action='compile-cache')
        response = client.post('/admin/actions', data, follow=True)
        cache2 = Cache.objects.first()
        data2 = json.loads(cache2.data)
        self.assertEqual(data2['team']['01A']['player1'], 'Colton Tucker')
        soup = BeautifulSoup(response.content, 'html.parser')
        txt = rex.s(str(soup.findAll("div", {"role" : "alert"})[0]), '\<.*?\>', '', 'g=')
        self.assertTrue('Cache successfully compiled.' in txt)
        # Get tournament base.
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Make results invisible.
        data = dict(action='make-results-invisible')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertFalse(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Make results visible (again).
        data = dict(action='make-results-visible')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Disable scorecard editing.
        data = dict(action='disable-scorecard-editing')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertFalse(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Enable scorecard editing (again).
        data = dict(action='enable-scorecard-editing')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Disable team access.
        data = dict(action='disable-team-access')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertFalse(tournament.enable_team_access)
        # Enable team access (again).
        data = dict(action='enable-team-access')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Disable leader board.
        data = dict(action='disable-leader-board')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertFalse(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Enable leader board (again).
        data = dict(action='enable-leader-board')
        response = client.post('/admin/actions', data, follow=True)
        tournament = Tournament.objects.filter(active=True).first()
        self.assertTrue(tournament.active)
        self.assertTrue(tournament.show_results)
        self.assertTrue(tournament.show_leader_board)
        self.assertTrue(tournament.enable_team_input)
        self.assertTrue(tournament.enable_team_access)
        # Goto scorecard staff
        data = dict()
        response = client.post('/team/scorecard/01A', data, follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Scorecard')
        fs.write_file(fs.join(settings.BASE_DIR, 'debug.html'), content)
        # Input team scores.
        tournament = Tournament.objects.filter(active=True).first()
        course = tournament.course
        holes = course.holes.all()
        i = 0
        awards = []
        award_holes = Hole.objects.exclude(special__isnull=True).exclude(special__exact='')
        for hole in award_holes:
            awards.append(f'{hole.special} : Hole # {hole.hole}')
        a = 0
        for team in Team.objects.filter(active=True).all():
            i += 1
            data = dict()
            response = client.post(f'/team/scorecard/{team.name}', data, follow=True)
            self.assertEqual(team.holes_played, 0)
            team_data = {
                "IsLoggedIn": 0,
                "TeamInfo": {
                    "Name": team.name,
                    "Valid": True,
                    "Players": [],
                    "StartHole": team.start_hole,
                    "Handicap": team.handicap,
                    "Score": {}
                },
                "EnableWrite": 1
            }
            if team.player1 is not None and len(team.player1) > 0: 
                team_data['TeamInfo']['Players'].append(team.player1)
                team_data['Award'] = {
                    'AwardType': awards[a],
                    'Team': team.name,
                    'Player': team.player1,
                }
                a += 1
                if a >= len(awards): a = 0
            if team.player2 is not None and len(team.player2) > 0: 
                team_data['TeamInfo']['Players'].append(team.player2)
            if team.player3 is not None and len(team.player3) > 0: 
                team_data['TeamInfo']['Players'].append(team.player3)
            for hole in holes:
                score = 4
                # Team starts out (on their start hole) with a 5.  They score 4 on all other holes.
                if team.start_hole == hole.hole:
                    score = 5
                team_data['TeamInfo']['Score'][str(hole.hole)] = {
                    'RawScore': score,
                    'RelScore': plusminus(score - hole.par),
                    'Valid': 1,
                }
            data = dict(Data=json.dumps(team_data, indent=None, separators=(',', ':')))
            response = client.post('/team/scorecard/update', data, follow=True)
            content = response.content.decode()
            response_data = json.loads(content)
            # print(json.dumps(response_data, indent=2))
            self.assertEqual(response_data['ourTeamData']['name'], team.name)
            self.assertEqual(response_data['ourTeamData']['holes_played'], 18)
            self.assertTrue(response_data['writeOccurred'])
        sorted_scores = []
        for team in Team.objects.filter(active=True).all():
            self.assertEqual(team.holes_played, 18)
            sorted_scores.append(team.sortable_score)
        # for score in sorted_scores:
        #     print(f'"{score}",')
        # print('---')
        sorted_scores.sort()
        # print(sorted_scores)
        expected_sorted_scores = [
            "058:000:333333333334333333:073:15B",
            "058:000:333433333333333333:073:14B",
            "060:000:333333333333343333:073:17C",
            "062:000:433333333333333333:073:01B",
            "063:000:343333333333333333:073:16B",
            "064:000:333333333333343333:073:17A",
            "064:000:343333333333333333:073:16A",
            "064:045:333333333333333433:073:18A",
            "065:000:333333333333333433:073:18B",
            "065:090:433333333333333333:073:01A",
            "067:045:333333333333343333:073:17B",
            "068:000:333333333333343333:073:17D",
            "070:020:333333333334333333:073:15A",
            "070:060:333433333333333333:073:14A",
        ]
        for actual_score, expected_score in zip(sorted_scores,expected_sorted_scores):
            self.assertEqual(actual_score, expected_score)
        # Test awards. 
        self.assertEqual(len(Award.objects.all()), len(Team.objects.all()))
        # Make sure there is no history.
        history = History.objects.all()
        self.assertEqual(len(history), 0)
        # Finalize results.
        data = {}
        response = client.post('/results', data, follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Tournament Results')
        for tag in soup.findAll("td", {"class" : "team-column"}):
            team_from_tournament_results_html = tag.text
            team_from_expected_sorted_scores = rex.split(expected_sorted_scores.pop(0), ':')[4]
            self.assertEqual(team_from_tournament_results_html, team_from_expected_sorted_scores)

        # fs.write_file(fs.join(settings.BASE_DIR, 'debug.html'), content)

    @override_settings(TESTING=True)
    def test_018_misc_player_pages(self):
        rex = Rex()
        client = Client()
        # Test past tournaments.
        data = {}
        response = client.post('/past/results', data, follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Past Tournaments')
        # Test 
        data = {}
        response = client.post('/teams', data, follow=True)
        content = response.content.decode()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.string, 'Rockne Invitational Golf Tournament : Teams')
        
        # fs.write_file(fs.join(settings.BASE_DIR, 'debug.html'), content)


        # response = client.post('/team/login', dict(team='01A', password='tee247'), follow=True)


