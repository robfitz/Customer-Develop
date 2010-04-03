from mycd.models import *
from django.shortcuts import render_to_response

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

def getPrevNextWorksheets(worksheet):
	worksheets = []
	for ss in Substep.objects.all():
		ss_worksheets = Worksheet.objects.filter(substep=ss)
		worksheets.extend(ss_worksheets)
		
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
