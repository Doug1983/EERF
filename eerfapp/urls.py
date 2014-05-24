from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from eerfapp.models import *

#===============================================================================
# urlpatterns = patterns('api.views',
#    url(r'^monitor/$', 'monitor'),
#    url(r'^subject/$', 'subject_index'),
#    url(r'^subject/(?P<subject_id>\d+)/$', 'subject_detail'), #calls subject_detail(request=<HttpRequest object>, subject_id='123')
#    url(r'^period/(?P<period_id>\d+)/$', 'period_detail'),
# )
#===============================================================================

urlpatterns = patterns('eerfapp.views',
    url(r'^$', 'index'), #This view is just a redirect to subject
    
    #===========================================================================
    # Some URLs for a basic API.
    #===========================================================================
    #url(r'^erps/(?P<trial_pk_csv>(?:\d+,*)*)', 'erps'),
    #url(r'^store_pk_check/(?P<pk>\d*)', 'store_pk_check'),
    url(r'^my_session/$', 'my_session', name='my_session'), #GET or POST session details.
    url(r'^detail_types/$', 'detail_types'),#GET ALL detail types
    url(r'^feature_types/$', 'feature_types'),#GET ALL feature types
    url(r'^get_xy/$', 'get_xy'), #GET data of detail (x) and feature (y)
    
    #===========================================================================
    # URLs for models
    #===========================================================================
    url(r'^subject/$', #List all the subjects.
        ListView.as_view(
            queryset=Subject.objects.all(),
            #context_object_name='subject_list',
            #template_name='api/subject_list.html'
        )
    ),
    url(r'^subject_list/$', 'subject_list', name='subject_list'),
    url(r'^subject_import/$', 'subject_import', name='subject_import'),
    url(r'^subject/(?P<pk>\d+)/$', #Give details about a specific subject.
        DetailView.as_view(
            model=Subject,
            #template_name='api/subject_detail.html'
        )
    ),
    url(r'^subject/(?P<pk>\d+)/view_data/$', 'view_data', name='view_data'), #Show trial data for a specific subject.
    url(r'^subject/(?P<pk>\d+)/set_details/$', 'set_details', name='set_details'), #POST a dict of detail kvps for subject pk
    url(r'^subject/(?P<pk>\d+)/detail_values/(?P<detail_name>\w*)/$', 'get_detail_values'), #GET the values for a detail name
    url(r'^subject/(?P<pk>\d+)/feature_values/(?P<feature_name>\w*)/$', 'get_feature_values'), #GET the values for a feature name
    url(r'^subject/(?P<pk>\d+)/count_trials/$', 'count_trials'), #GET the number of trials, filtered by session variables.
    url(r'^subject/(?P<pk>\d+)/erp_data/$', 'erp_data'), #GET the erp_data for this subject, filtered by session variables.
    url(r'^subject/(?P<pk>\d+)/recalculate_feature/(?P<feature_name>\w+)/$', 'recalculate_feature'), #Recalculate feature values
    url(r'^period/(?P<pk>\d+)/$',
        DetailView.as_view(
            model=Datum,
            template_name='eerfapp/period_detail.html',
            context_object_name='period',
        ),
        name='period_detail'
    ),
                       
    #===========================================================================
    # Other URLs
    #===========================================================================    
)