from django.db import models
from django.forms import CharField, Form, ModelForm, Textarea
from datetime import *
from django.contrib.auth.models import User
import re


RELATION_STATE_CHOICES = (
	(u'Uncontacted', u'Uncontacted'),
	(u'Active', u'Active'),
	(u'Friendly', u'Friendly'),
	(u'Dead', u'Dead'),
)

class Contact(models.Model):
	owner = models.ForeignKey(User)

	#basic info
	name = models.CharField(max_length=100)
	job_title = models.CharField(max_length=100)
	company = models.CharField(max_length=100)
	state = models.CharField(max_length=100, 
							 choices=RELATION_STATE_CHOICES)
	#extra info
	email = models.CharField(max_length=100)
	twitter = models.CharField(max_length=100)
	linked_in = models.CharField(max_length=100)
	hacker_news = models.CharField(max_length=100)
	website = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name

	def getMiscFields(self):
		return (self.twitter, 
			self.linked_in, 
			self.hacker_news,
			self.website,
			)

	def toText(self):
		text = ''
		if self.name: 
			text = self.name + "\n"
		
		if self.job_title:
			text = text + self.job_title
		
		if self.company:
			text = text + " @ " + self.company + "\n"
		
		if self.email:
			text = text + self.email + "\n"

		for field in self.getMiscFields():
			if field: 
				text = text + field + '\n'

		return text

	def fromText(self, text):
		lines = text.split('\n')
		
		self.name = ""
		self.job_title = ""
		self.company = ""
		
		self.email = ""
		self.twitter = ""
		self.linked_in = ""
		self.hacker_news = ""
		self.website = ""

		# first line is location-sensitive for name
		if len(lines) >= 1:
			self.name = lines[0].strip()
		
		for line in lines:
			# job @ company
			if re.match(r".+? @ .+", line):
				tokens = line.split(' @ ')
				self.job_title = tokens[0].strip()
				self.company = tokens[1].strip()
			elif re.match(r"@ .+", line):
				tokens = line.split(' @ ')
				self.company = tokens[0].strip()
			
			#email
			elif re.match(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b", line):
				self.email = line
			
			# twitter
			elif re.match(r"@.+$", line):
				self.twitter = line
				
			# linked in
			elif re.search(r"linkedin.com", line):
				self.linked_in = line
				
			# hacker news
			elif re.search(r"HN .+", line):
				self.hacker_news = line
			
			# generic website (personal or business)
			elif re.match(r"http|www", line):
				self.website = line
		
		return self

class Step(models.Model):
	name = models.CharField(max_length=100)
	order = models.DecimalField(decimal_places=2, max_digits=4, default=1)

	def __unicode__(self):
		if self.name: return self.name
		else: return "unnamed step"
	class Meta:
		ordering = ['order']

class SubstepCategory(models.Model):
	name = models.CharField(max_length=100)
	step = models.ForeignKey(Step)
	order = models.DecimalField(decimal_places=2, max_digits=4, default=1)
	
	def __unicode__(self):
		if self.name: return self.step.name + ' - ' + self.name
		else: return "unnamed substep"
	class Meta:
		ordering = ['order']
		
class Substep(models.Model):
	name = models.CharField(max_length=100)
	substepcategory = models.ForeignKey(SubstepCategory)
	order = models.DecimalField(decimal_places=2, max_digits=4)
	
	def __unicode__(self):
		return self.substepcategory.name + ' - ' + self.name
	class Meta:
		ordering = ['substepcategory__order', 'order']

class Worksheet(models.Model):
	name = models.CharField(max_length=100)
	order = models.DecimalField(decimal_places=2, max_digits=4, null=True)
	substep = models.ForeignKey(Substep) #safe to duplicate & makes for easier filtering
	#custom_template = models.CharField(max_length=100, blank=True, null=True)
	custom_view = models.CharField(max_length=100, blank=True, null=True)
	
	def __unicode__(self):
		if self.name: return self.name
		else: return "unnamed worksheet"
	class Meta:
		ordering = ['order']
		
class Question(models.Model):
	prompt = models.CharField(max_length=200, null=True, blank=True)
	order = models.DecimalField(decimal_places=2, max_digits=4, null=True)
	field_rows = models.IntegerField(default=4, null=True)
	worksheet = models.ForeignKey(Worksheet)
	details = models.CharField(max_length=1000, null=True, blank=True)
	
	def __unicode__(self):
		if self.prompt: return self.prompt
		else: return "blank question"
	class Meta:
		ordering = ['order']

class Answer(models.Model):
	owner = models.ForeignKey(User)
	question = models.ForeignKey(Question)
	answer = models.CharField(max_length=1000, default="", blank=True)
	#versioning
	is_latest = models.BooleanField(default=False) #true if this is the user's most recent Question
	previous_version = models.OneToOneField('self', blank=True, null=True, related_name='next_version') #link to previous version of this Question
	timestamp = models.DateTimeField(blank=True, null=True) #when this version was made & saved

	def __unicode__(self):
		if self.answer: return self.answer
		else: return ""

class WorksheetForm(ModelForm):
	class Meta:
		model = Worksheet
		#exclude = ('',)
		#fields = ('',)
	def __unicode__(self):
		if self.model and self.model.name: return self.model.name
		else: return "unnamed worksheet form"


class QuestionForm(Form):
	#answer = CharField(label="", widget=Textarea)
	answer = Textarea()

