from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404
from mycd.models import Worksheet, Question, QuestionForm, Substep, Step, SubstepCategory, Answer
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import auth
from django.contrib.auth.models import User
from mycd.util import *

from django.utils.encoding import smart_str, smart_unicode

def index(request):
	if request.method == 'POST' and len(request.POST.keys()) > 0:
		if request.POST["email"]:
			sub = NewsSubscriber(email=request.POST["email"])
			sub.save()
			return HttpResponseRedirect('http://customerdevelop.wufoo.com/forms/thanks-for-the-interest-now-i-need-your-help/')
	return render_to_response('static/index.html', locals())

def scrap(request):
	return render_to_response('static/scrap.html')

def contactList(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/dashboard/")

	breadcrumbs = [{'name':'Dashboard', 'url':'/dashboard'},
				   {'name':'Contacts', 'url':'/contacts'}]				   
	
	contacts = Contact.objects.filter(owner=request.user)

	return render_to_response('crm/summary.html', locals())

def editContact(request, contact_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/dashboard/")

	breadcrumbs = [{'name':'Dashboard', 'url':'/dashboard'},
				   {'name':'Contacts', 'url':'/contacts'},
				   {'name':'Edit Contact'}]
				   
	if contact_id == '00':
		#create new contact with a blank form
		contact = Contact(owner=request.user)
		
	else:
		#populate form w/ existing model
		contact = Contact.objects.filter(owner=request.user).get(pk=contact_id)
				
		if not contact:
			return HttpResponseRedirect("/contacts/")

	categories = ContactTagCategory.objects.all()
	for category in categories:
		category.tags = ContactTag.objects.filter(category=category)
		for t in category.tags:
			if contact in t.contacts.all():
				t.is_active=True

	if request.method == 'POST' and len(request.POST.keys()) > 0:
		#grab stuff from form
		if request.POST['data']:
			data = request.POST['data']
			contact.fromText(data)
		if request.POST['state']:
			contact.state = request.POST['state']
		
		active_tags = []
		for key in request.POST.keys():
			if key.startswith('tag_'):
				id = key[4:]
				tag = ContactTag.objects.get(id=id)
				tag.contacts.add(contact)
				tag.save()
				active_tags.append(tag)

		tags = ContactTag.objects.all()
		for t in tags:
			if not t in active_tags:
				try: t.contacts.remove(contact)
				except: pass
			t.save()
		
		contact.save()
		
		return HttpResponseRedirect("/contacts/")
		
	contact.data = contact.toText()
	contact.tags = categories
	
	return render_to_response('crm/edit.html', locals())

def login(request):

	if request.user.is_authenticated():
		return HttpResponseRedirect("/dashboard/")
	elif 'username' in request.POST and 'password' in request.POST:
		username = request.POST['username']
		password = request.POST['password']
	
		user = auth.authenticate(username=username, password=password)
		if user is not None and user.is_active:
			# Correct password, and the user is marked "active"
			auth.login(request, user)
			# Redirect to a success page.
			return HttpResponseRedirect("/dashboard/")
		else:
			error = "Bad username or password :("
			return render_to_response('bad_login.html')

	breadcrumbs = [{'name':'Log in'}]
	form = AuthenticationForm()
	next = '/login/'
	return render_to_response('dashboard/login.html', locals())

def register(request):
	return HttpResponseRedirect("/")

	if request.user.is_authenticated():
		return HttpResponseRedirect("/dashboard/")
	else:
		if 'username' in request.POST and 'password1' in request.POST and 'password2' in request.POST:
			if request.POST['password1'] == request.POST['password2']:

				user = User.objects.create_user(username=request.POST['username'],
												email='example@example.com',
												password=request.POST['password1'])
				user.save()
				user = auth.authenticate(username=request.POST['username'],
										 password=request.POST['password1'])
				auth.login(request, user)
				
				return HttpResponseRedirect("/dashboard/")
			else:
				error  = "Passwords should match (typo?)"
		 
	breadcrumbs = [{'name':'Register'}]
	form = UserCreationForm()
	return render_to_response('dashboard/register.html', locals())

def signout(request):
	logout(request)
	return HttpResponseRedirect("/")

def dashboard(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/")
	
	breadcrumbs = [{'name':'Dashboard', 'url':'/dashboard'}]
	worksheets = []
	for ss in Substep.objects.all():
		ss_worksheets = Worksheet.objects.filter(substep=ss)
		worksheets.extend(ss_worksheets)

	substeps = []
	#grab all the substeps that the user has worksheets for
	for w in worksheets:
		if substeps.count(w.substep) == 0:
			substeps.append(w.substep)
	#collect the questions in each of those substeps
	for s in substeps:
		sheets = Worksheet.objects.filter(substep=s)
		if len(sheets) > 0:
			s.worksheets = sheets
	return render_to_response('dashboard/index.html', locals())
					
def featureWorksheet(request, worksheet_id):
	worksheet = get_object_or_404(Worksheet, pk=worksheet_id)
	prevWorksheet, nextWorksheet = getPrevNextWorksheets(worksheet)
	breadcrumbs = getWorksheetBreadcrumbs(worksheet)
	
	questions = Question.objects.filter(worksheet=worksheet)
	rows = []

	if request.method == 'POST' and len(request.POST.keys()) > 0:
		for q in questions:
			
			try: old_answer = Answer.objects.filter(is_latest=True).filter(owner=request.user).get(question=q)
			except Answer.DoesNotExist: old_answer = None
			
			new_answers = request.POST.getlist(unicode(q.pk))
			new_answer_text = ""
			i = 0
			for a in new_answers:
				new_answer_text = new_answer_text + a
				if i < len(new_answers) - 1:
					new_answer_text = new_answer_text + ';'
				if len(rows) <= i:
					rows.append([])
				rows[i].append({"pk": q.pk, "answer": a})
				i = i + 1
			
			addNewAnswer(q, request.user, old_answer, new_answer_text)
			
	else:
		for q in questions:
			try: old_answer = Answer.objects.filter(is_latest=True).filter(owner=request.user).get(question=q)
			except Answer.DoesNotExist: old_answer = None

			if old_answer:
				answers = old_answer.answer.split(';')
				i = 0
				for a in answers:
					#if a and len(a) > 0:
					if len(rows)<=i: rows.append([])
					rows[i].append({"pk": q.pk, "answer": a})
					i = i + 1
					
		for i in [0, 1, 2]:
			if len(rows) <= i:
				rows.append([])
				for q in questions:
					rows[i].append({"pk": q.pk, "answer": ""})
				
	return render_to_response('worksheets/features.html', locals())

def worksheet(request, worksheet_id):
	#verify access rights
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/login/")

	#grab basic objects & navigation
	worksheet = get_object_or_404(Worksheet, pk=worksheet_id)
	prevWorksheet, nextWorksheet = getPrevNextWorksheets(worksheet)
	breadcrumbs = getWorksheetBreadcrumbs(worksheet)
	
	#redirect to a custom view if the worksheet requires it
	#NOTE:  there is some code duplication between this & child functions,
	#	   but not sure how to remove it without making lengthy parameter
	#	   dependencies
	if worksheet.custom_view and globals()[worksheet.custom_view]:
		return globals()[worksheet.custom_view](request, worksheet_id)

	questions = []
	#user has submitted the form. check for new data & save it
	for q in Question.objects.filter(worksheet=worksheet):
	
		#if the user has submitted answers, handle them
		if request.method == 'POST' and len(request.POST.keys()) > 0:
			#if available, note down their old answer for versioning
			try: old_answer = Answer.objects.filter(is_latest=True).filter(owner=request.user).get(question=q)
			except Answer.DoesNotExist: old_answer = None
			#populate form w/ post data
			form = QuestionForm(request.POST, prefix=q.pk)
			form.instance = q
			if form.is_valid():
				# before saving
				new_answer_text = request.POST[str(q.pk) + '-answer'];
				if (not old_answer or new_answer_text != old_answer.answer):
					answer = addNewAnswer(q, request.user, old_answer, new_answer_text)
					form.answer = answer
				else:
					form.answer = old_answer
		else:
			form = QuestionForm(prefix=q.pk)
			form.instance = q
			try:
				form.answer = Answer.objects.filter(is_latest=True).filter(owner=request.user).get(question=q)
			except Answer.DoesNotExist:
				form.answer = None

		if form.answer:
			form.answer.versions = getAnswerVersions(form.answer)
		else: form.answer = ""

		questions.append(form);
		
		"""
		if q.contact_tag:
			matchingTags = ContactTag.objects.filter(name=q.contact_tag.name).filter(category=q.contact_tag.category).filter(is_active=True)
			tagContacts = []
			for t in matchingTags:
				if t.contact.owner == request.user:
					tagContacts.append(t.contact)
			num = len(tagContacts)
			q.field_note = "You currently have <b>" + str(num) + " contacts</b> of this type. Enter additional names below to add more."
		"""

	#if worksheet.custom_template:
	#   return render_to_response(worksheet.custom_template, locals())
	#else:
	return render_to_response('worksheets/worksheet.html', locals())
