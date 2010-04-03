from cdev.mycd.models import *
from django.contrib import admin

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5
    fields = ['order', 'prompt', 'field_rows']

class SubstepInline(admin.TabularInline):
    model = Substep
    extra = 5
    fields = ['order', 'name']

class SubstepCategoryInline(admin.TabularInline):
    model = SubstepCategory
    extra = 5
    fields = ['name']

class WorksheetInline(admin.TabularInline):
    model = Worksheet
    extra = 3
    fields = ['order', 'name']

class WorksheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'substep')
    #fields = ('name', 'substep')
    inlines = [QuestionInline]
    
class UserAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

class StepAdmin(admin.ModelAdmin):
    inlines = [SubstepCategoryInline]
    list_display = ('__unicode__', 'order')
    list_editable = ('order',)

class SubstepAdmin(admin.ModelAdmin):
    inlines = [WorksheetInline]
    list_display = ('__unicode__', 'order')
    list_editable = ('order',)

class SubstepCategoryAdmin(admin.ModelAdmin):
    inlines = [SubstepInline]
    list_display = ('__unicode__', 'order')
    list_editable = ('order',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'field_rows')
    list_editable = ('field_rows',)
    list_display_links = ('prompt',)
    search_fields = ('prompt',)
    #list_filter = ('is_latest', 'is_base_model')
    #date_hierarchy = 'timestamp'
    fields = ('worksheet', 'prompt', 'details', 'field_rows')
    #filter_horizontal = ('many_to_many_field',)
    #raw_id_fields = ('extraInfo',)

    def owner(self, model):
        return model.worksheet.user
    
admin.site.register(Contact)
admin.site.register(Answer)
admin.site.register(Worksheet, WorksheetAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Substep, SubstepAdmin)
admin.site.register(SubstepCategory, SubstepCategoryAdmin)
admin.site.register(Question, QuestionAdmin)
