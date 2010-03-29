from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404
from mycd.models import Worksheet, Question, QuestionForm, Substep, Step, SubstepCategory, Answer
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import auth
from django.contrib.auth.models import User

from django.utils.encoding import smart_str, smart_unicode

def index(request):
    return render_to_response('static/index.html', locals())

def export(request):
    substeps = Substep.objects.all()
    questions = Question.objects.all()
    return render_to_response('util/exportCsv.html', locals())

def importCsv(request):
    if request.method == "POST":
        data = smart_str(request.POST['import_data'])
        rows = data.split('\n')
        print data
        print 'row length %d' % len(rows)
        for r in rows:
            #print r
            cols = r.split(';')
            print 'col length %d' % len(cols)
            print '%s' % cols[0]
            step = None
            category = None
            substep = None
            
            if len(cols) >= 2:
                step, created = Step.objects.get_or_create(name=cols[0])
                if created:
                    print 'created a step!'
                    print step
                    step.save()
                else:
                    print 'accessed an existing step'
            if len(cols) >= 4:
                category, created = SubstepCategory.objects.get_or_create(name=cols[2],
                                                                          step=step)
                if created:
                    print 'created a category!'
                    print category
                    category.save()
            if len(cols) >= 6:
                print 'substep order %s' % cols[5]
                substep, created = Substep.objects.get_or_create(name=cols[4],
                                                                 order=cols[5],
                                                                 substepcategory=category)
                if created: substep.save()
                print substep
            if len(cols) >= 8 and len(cols[6]) > 0 and len(cols[7]) > 0:
                print 'name:%s order:%s substep:%s' % (cols[6], cols[7], substep)
                worksheet, created = Worksheet.objects.get_or_create(name=cols[6],
                                                                     order=cols[7],
                                                                     substep=substep)
                if created: worksheet.save()
                print worksheet
            if len(cols) >= 11 and len(cols[8]) > 0 and len(cols[9]) > 0 and len(cols[10]) > 0:
                question, created = Question.objects.get_or_create(prompt=cols[8],
                                                                   order=cols[9],
                                                                   field_rows=cols[10],
                                                                   worksheet=worksheet)
                if created: question.save()
            
        return HttpResponseRedirect("/dashboard")
    else:
        return render_to_response('util/importCsv.html')

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/dashboard")
    elif 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
    
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            auth.login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect("/dashboard")
        else:
            error = "Bad username or password :("

    breadcrumbs = [{'name':'Log in'}]
    form = AuthenticationForm()
    next = '/login/'
    return render_to_response('dashboard/login.html', locals())

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/dashboard")
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

                assignBaseModelsTo(user)
                
                return HttpResponseRedirect("/dashboard")
            else:
                error  = "Passwords should match (typo?)"
         
    breadcrumbs = [{'name':'Register'}]
    form = UserCreationForm()
    return render_to_response('dashboard/register.html', locals())

def signout(request):
    logout(request)
    return index(request)

def dashboard(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")
    
    breadcrumbs = [{'name':'Dashboard', 'url':'/dashboard'}]
    worksheets = Worksheet.objects.filter()
     
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

def getPrevNextWorksheets(worksheet):
    worksheets = Worksheet.objects.filter(substep__substepcategory=worksheet.substep.substepcategory)
    ws_index = 0
    prevWorksheet = None
    nextWorksheet = None
    for w in worksheets:
        if w == worksheet:
            if ws_index > 0:
                prevWorksheet = worksheets[ws_index - 1]
            if ws_index < len(worksheets) - 1:
                nextWorksheet = worksheets[ws_index + 1]
        ws_index = ws_index + 1
    return (prevWorksheet, nextWorksheet)

def getWorksheetBreadcrumbs(worksheet):
    return [{'name':'Dashboard',
             'url':'/dashboard/'},
            {'name':'Worksheets'},
            {'name':worksheet.substep.name,
             'url':'/worksheet/' + str(worksheet.substep.worksheet_set.all()[0].pk)},
            {'name':worksheet.name,
             'url':'/worksheet/' + str(worksheet.pk)}]

def getAnswerVersions(answer):
    versions = []
    temp = answer
    while temp.previous_version:
        temp = temp.previous_version
        if temp.answer:
            print 'version %s' % temp
            versions.append(temp)
    return versions

def addNewAnswer(question, owner, old_answer, new_answer_text):
    answer = Answer(question=question,
                    answer=new_answer_text,
                    previous_version=old_answer,
                    timestamp=datetime.now(),
                    is_latest=True,
                    owner=owner)
    answer.save()

    if old_answer:
        old_answer.is_latest = False
        old_answer.save()
    return answer
                    
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
            print new_answers
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
            print 'added new answer: %s' % new_answer_text

    else:
        for q in questions:
            try: old_answer = Answer.objects.filter(is_latest=True).filter(owner=request.user).get(question=q)
            except Answer.DoesNotExist: old_answer = None

            if old_answer:
                print old_answer
                answers = old_answer.answer.split(';')
                i = 0
                for a in answers:
                    #if a and len(a) > 0:
                    if len(rows)<=i: rows.append([])
                    rows[i].append({"pk": q.pk, "answer": a})
                    i = i + 1
                    
        for i in [0, 1, 2]:
            if len(rows) <= i:
                print 'appending a row for %i' % i
                rows.append([])
                for q in questions:
                    rows[i].append({"pk": q.pk, "answer": ""})
                
    return render_to_response('worksheets/features.html', locals())

def worksheet(request, worksheet_id):
    #verify access rights
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/login")

    #grab basic objects & navigation
    worksheet = get_object_or_404(Worksheet, pk=worksheet_id)
    prevWorksheet, nextWorksheet = getPrevNextWorksheets(worksheet)
    breadcrumbs = getWorksheetBreadcrumbs(worksheet)
    
    #redirect to a custom view if the worksheet requires it
    #NOTE:  there is some code duplication between this & child functions,
    #       but not sure how to remove it without making lengthy parameter
    #       dependencies
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
            else: print 'INVALID FORM!'
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

    #if worksheet.custom_template:
    #   return render_to_response(worksheet.custom_template, locals())
    #else:
    return render_to_response('worksheets/worksheet.html', locals())
