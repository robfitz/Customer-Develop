from django.db import models
from django.forms import CharField, Form, ModelForm, Textarea
from datetime import *
from django.contrib.auth.models import User

class Step(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        if self.name: return self.name
        else: return "unnamed step"

class SubstepCategory(models.Model):
    name = models.CharField(max_length=100)
    step = models.ForeignKey(Step)

    def __unicode__(self):
        if self.name: return self.name
        else: return "unnamed substep"

    #class Meta:
    #    ordering = ['name']
    
class Substep(models.Model):
    name = models.CharField(max_length=100)
    substepcategory = models.ForeignKey(SubstepCategory)
    order = models.DecimalField(decimal_places=2, max_digits=4)
    
    def __unicode__(self):
        return self.substepcategory.step.name + ' - ' + self.substepcategory.name + ' - ' + self.name
    class Meta:
        ordering = ['order']

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

