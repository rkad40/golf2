import datetime

from colorfield.fields import ColorField
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.validators import MaxValueValidator, MinValueValidator, EmailValidator
from django.db import models
from django.db.models import Q
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils import timezone

from rex import Rex

DEBUG = False

def localize_now():
    return timezone.now()

r"""
  ____           _
 / ___|__ _  ___| |__   ___
| |   / _` |/ __| '_ \ / _ \
| |__| (_| | (__| | | |  __/
 \____\__,_|\___|_| |_|\___|

"""

class Cache(models.Model):
    epoch = models.IntegerField('Epoch Timestamp', null=False, blank=False, default=0)
    data = models.CharField('Data', max_length=1000000, unique=False, null=True, blank=True)
    class Meta:
        verbose_name = 'Compiled Data Cache'
        verbose_name_plural = 'Compiled Data Cache'

r"""
 _____
|_   _|__  __ _ _ __ ___
  | |/ _ \/ _` | '_ ` _ \
  | |  __/ (_| | | | | | |
  |_|\___|\__,_|_| |_| |_|

"""

class Team(models.Model):
    name = models.CharField('Name', max_length=10, unique=True, null=False, blank=False)
    player1 = models.CharField('Player 1', max_length=100, unique=False, null=True, blank=True)
    player2 = models.CharField('Player 2', max_length=100, unique=False, null=True, blank=True)
    player3 = models.CharField('Player 3', max_length=100, unique=False, null=True, blank=True)
    handicap = models.IntegerField( 'Handicap',  unique=False, null=True, blank=True)
    start_hole = models.IntegerField('Start Hole', validators=[MaxValueValidator(18), MinValueValidator(1)], help_text="Hole that the team starts on.", unique=False, null=True, blank=True)
    password = models.CharField('Password', max_length=100, unique=False, null=True, blank=True)
    hole1 = models.IntegerField ('Hole 1 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole2 = models.IntegerField ('Hole 2 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole3 = models.IntegerField ('Hole 3 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole4 = models.IntegerField ('Hole 4 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole5 = models.IntegerField ('Hole 5 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole6 = models.IntegerField ('Hole 6 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole7 = models.IntegerField ('Hole 7 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole8 = models.IntegerField ('Hole 8 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole9 = models.IntegerField ('Hole 9 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole10 = models.IntegerField('Hole 10 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole11 = models.IntegerField('Hole 11 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole12 = models.IntegerField('Hole 12 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole13 = models.IntegerField('Hole 13 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole14 = models.IntegerField('Hole 14 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole15 = models.IntegerField('Hole 15 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole16 = models.IntegerField('Hole 16 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole17 = models.IntegerField('Hole 17 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole18 = models.IntegerField('Hole 18 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    holes_played = models.IntegerField( 'Holes Played', unique=False, null=False, blank=False, default=0)
    current_raw_score = models.IntegerField('Current Raw Score', unique=False, null=False, blank=False, default=0)
    current_rel_score = models.IntegerField('Current Relative Score', unique=False, null=False, blank=False, default=0)
    final_adj_raw_score = models.IntegerField('Final Adjusted Raw Score', unique=False, null=False, blank=False, default=0)
    final_adj_rel_score = models.IntegerField('Final Adjusted Relative Score', unique=False, null=False, blank=False, default=0)
    proj_adj_rel_score = models.IntegerField('Projected Adjusted Relative Score', unique=False, null=False, blank=False, default=0)
    history = models.IntegerField('History', unique=False, null=False, blank=False, default=0, help_text="First tiebreaker is tournament history. Number > 0 means team includes players that have recently have had 1st, 2nd, or 3rd place finish.")
    updated_on = models.DateTimeField('Updated On', null=True, blank=True, help_text="Scored last updated on.")
    sortable_score = models.CharField('Sortable Score', max_length=200, unique=False, null=True, blank=True)
    rank = models.IntegerField('Rank', unique=False, null=True, blank=True)
    comment = models.CharField('Comment', max_length=200, unique=False, null=True, blank=True)
    score_calculated = models.BooleanField('Score Calculated', default=False)
    active = models.BooleanField('Active', default=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'All Teams'

r"""
 _____                       _
|_   _|__  __ _ _ __ ___    / \   ___ ___ ___  ___ ___
  | |/ _ \/ _` | '_ ` _ \  / _ \ / __/ __/ _ \/ __/ __|
  | |  __/ (_| | | | | | |/ ___ \ (_| (_|  __/\__ \__ \
  |_|\___|\__,_|_| |_| |_/_/   \_\___\___\___||___/___/

"""

class TeamAccess(models.Model):
    token = models.CharField('Token', max_length=100, unique=True, null=False, blank=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Team Access Token'
        verbose_name_plural = 'Team Access Tokens'

r"""
 ____  _
|  _ \| | __ _ _   _  ___ _ __
| |_) | |/ _` | | | |/ _ \ '__|
|  __/| | (_| | |_| |  __/ |
|_|   |_|\__,_|\__, |\___|_|
               |___/
"""

class Player(models.Model):
    VOTE_CHOICES = [
        ('koozies', 'Koozies are good enough for me!'),
        ('trophies', 'Honestly, I liked tophies better.'),
        ('koozies and trophies', 'I vote for koozies and (smaller) trophies'),
    ]
    name = models.CharField('Name', max_length=100, unique=False, null=False, blank=False)
    spelling = models.CharField('Your Name (if not spelled correctly above)', max_length=100, unique=False, null=True, blank=True, help_text="If I have mis-spelled your name, please help me get it right the next time.")
    email = models.CharField('Email Address', max_length=200, unique=False, null=True, blank=True, help_text="Please provide at least one of your email address or text capable cell phone number.")
    phone = models.CharField('Cell Number', max_length=100, unique=False, null=True, blank=True, help_text="Please provide at least one of your email address or text capable cell phone number.")
    handicap = models.FloatField('Handicap', unique=False, null=True, blank=True, help_text="Do you know your handicap?  If so, please provide.")
    score = models.IntegerField('Average Score', unique=False, null=True, blank=True, help_text="If you don't know your handicap, can you provide an average score?")
    vote = models.CharField('Your Vote: Trophies or Koozies?', max_length=100, choices=VOTE_CHOICES, null=True, blank=True, help_text="This year we are doing koozies in lieu of trophies.  But next year I will do whatever the consensus wants.  Just know that if we go back to trophies, it probably means we have to raise entry fees.") 
    comment = models.CharField('Comments', max_length=10000, unique=False, null=True, blank=True, help_text="Comments? Questions? Complaints?  If you want to kindly suggest any changes to our tournament, this is your chance.")

r"""
    _                        _
   / \__      ____ _ _ __ __| |
  / _ \ \ /\ / / _` | '__/ _` |
 / ___ \ V  V / (_| | | | (_| |
/_/   \_\_/\_/ \__,_|_|  \__,_|

"""

class Award(models.Model):
    award_type = models.CharField('Award Type', max_length=100, unique=False, null=False, blank=False, default='Closest to the Hole')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.CharField('Player', max_length=100, unique=False, null=False, blank=False)
    created_on = models.DateTimeField('Created On', null=False, blank=False)
    is_best = models.BooleanField('Current Best?', default=True)
    class Meta:
        verbose_name = 'Hole Award'
        verbose_name_plural = 'Hole Awards'

r"""
  ____
 / ___|___  _   _ _ __ ___  ___
| |   / _ \| | | | '__/ __|/ _ \
| |__| (_) | |_| | |  \__ \  __/
 \____\___/ \__,_|_|  |___/\___|

"""

class Course(models.Model):
    name = models.CharField('Name', max_length=50, unique=True, null=False, blank=False)
    par = models.IntegerField('Par', unique=False, null=True, blank=True)
    rating = models.FloatField('Rating', unique=False, null=True, blank=True)
    slope = models.FloatField('Slope', unique=False, null=True, blank=True)
    active = models.BooleanField('Active', default=True)
    def __str__(self):
        return self.name

r"""
 _   _       _
| | | | ___ | | ___
| |_| |/ _ \| |/ _ \
|  _  | (_) | |  __/
|_| |_|\___/|_|\___|

"""

class Hole(models.Model):
    SPECIAL_CHOICES = [
        ('Closest to the Hole', 'Closest to the Hole'),
        ('Longest Drive', 'Longest Drive'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='holes')
    hole = models.IntegerField('Hole', unique=False, null=True, blank=True)
    par = models.IntegerField('Par', unique=False, null=True, blank=True)
    handicap = models.IntegerField('Handicap', unique=False, null=True, blank=True)
    gold = models.IntegerField('Gold', unique=False, null=True, blank=True)
    blue = models.IntegerField('Blue', unique=False, null=True, blank=True)
    white = models.IntegerField('White', unique=False, null=True, blank=True)
    red = models.IntegerField('Red', unique=False, null=True, blank=True)
    special = models.CharField('Special', max_length=100, choices=SPECIAL_CHOICES, null=True, blank=True) 
    class Meta:
        verbose_name = 'Course Hole Info'
        verbose_name_plural = 'Course Holes Info'
    def __str__(self):
        return f'{self.course.name} : Hole {self.hole}'

r"""
 _____                                                 _
|_   _|__  _   _ _ __ _ __   __ _ _ __ ___   ___ _ __ | |_
  | |/ _ \| | | | '__| '_ \ / _` | '_ ` _ \ / _ \ '_ \| __|
  | | (_) | |_| | |  | | | | (_| | | | | | |  __/ | | | |_
  |_|\___/ \__,_|_|  |_| |_|\__,_|_| |_| |_|\___|_| |_|\__|

"""

class Tournament(models.Model):
    PLAY_FROM_CHOICES = [
        ('gold', 'Gold tees'),
        ('blue', 'Blue tees'),
        ('white', 'White tees'),
        ('red', 'Red tees'),
    ]
    name = models.CharField('Name', max_length=500, unique=False, null=False, blank=False)
    date_time = models.DateTimeField('Updated On', null=True, blank=True, help_text="Tournament date and start time.")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    play_from = models.CharField('Play From', max_length=100, choices=PLAY_FROM_CHOICES, default='white', null=False, blank=False) 
    enable_team_access = models.BooleanField('Enable Team Access', default=False)
    enable_team_input = models.BooleanField('Enable Team Input', default=False)
    show_leader_board = models.BooleanField('Show Leader Board', default=False)
    show_results = models.BooleanField('Show Results', default=False)
    archived = models.BooleanField('Archived', default=False)
    archive_notes = models.CharField('Notes', max_length=10000, unique=False, null=True, blank=True)
    active = models.BooleanField('Active', default=True)
    def __str__(self):
        return f'{self.name} - {self.date_time.strftime("%b %d, %Y")}'
    class Meta:
        verbose_name = 'Tournament'
        verbose_name_plural = 'All Tournaments'

r"""
 _   _ _     _
| | | (_)___| |_ ___  _ __ _   _
| |_| | / __| __/ _ \| '__| | | |
|  _  | \__ \ || (_) | |  | |_| |
|_| |_|_|___/\__\___/|_|   \__, |
                           |___/
"""

class History(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=10, unique=False, null=False, blank=False)
    player1 = models.CharField('Player 1', max_length=100, unique=False, null=True, blank=True)
    player2 = models.CharField('Player 2', max_length=100, unique=False, null=True, blank=True)
    player3 = models.CharField('Player 3', max_length=100, unique=False, null=True, blank=True)
    handicap = models.IntegerField( 'Handicap',  unique=False, null=True, blank=True)
    start_hole = models.IntegerField('Start Hole', validators=[MaxValueValidator(18), MinValueValidator(1)], help_text="Hole that the team starts on.", unique=False, null=True, blank=True)
    password = models.CharField('Password', max_length=100, unique=False, null=True, blank=True)
    hole1 = models.IntegerField ('Hole 1 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole2 = models.IntegerField ('Hole 2 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole3 = models.IntegerField ('Hole 3 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole4 = models.IntegerField ('Hole 4 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole5 = models.IntegerField ('Hole 5 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole6 = models.IntegerField ('Hole 6 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole7 = models.IntegerField ('Hole 7 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole8 = models.IntegerField ('Hole 8 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole9 = models.IntegerField ('Hole 9 Score',  validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole10 = models.IntegerField('Hole 10 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole11 = models.IntegerField('Hole 11 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole12 = models.IntegerField('Hole 12 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole13 = models.IntegerField('Hole 13 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole14 = models.IntegerField('Hole 14 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole15 = models.IntegerField('Hole 15 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole16 = models.IntegerField('Hole 16 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole17 = models.IntegerField('Hole 17 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    hole18 = models.IntegerField('Hole 18 Score', validators=[MaxValueValidator(10), MinValueValidator(1)], unique=False, null=True, blank=True)
    holes_played = models.IntegerField( 'Holes Played',  unique=False, null=True, blank=True)
    current_raw_score = models.IntegerField('Current Raw Score', unique=False, null=True, blank=True)
    current_rel_score = models.IntegerField('Current Relative Score', unique=False, null=True, blank=True)
    final_adj_raw_score = models.IntegerField('Final Adjusted Raw Score', unique=False, null=True, blank=True)
    final_adj_rel_score = models.IntegerField('Final Adjusted Relative Score', unique=False, null=True, blank=True)
    proj_adj_rel_score = models.IntegerField('Projected Adjusted Relative Score', unique=False, null=True, blank=True)
    updated_on = models.DateTimeField('Updated On', null=True, blank=True, help_text="Scored last updated on.")
    history = models.IntegerField('History', unique=False, null=False, blank=False, default=0, help_text="First tiebreaker is tournament history. Number > 0 means team includes players that have recently have had 1st, 2nd, or 3rd place finish.")
    sortable_score = models.CharField('Sortable Score', max_length=200, unique=False, null=True, blank=True)
    rank = models.IntegerField('Rank', unique=False, null=True, blank=True)
    comment = models.CharField('Comment', max_length=10000, unique=False, null=True, blank=True)
    score_calculated = models.BooleanField('Score Calculated', default=False)
    active = models.BooleanField('Active', default=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Past Tournament Results'
        verbose_name_plural = 'Past Tournament Results'

