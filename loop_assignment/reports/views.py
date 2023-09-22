from django.shortcuts import render
from rest_framework import views, status
from rest_framework.response import Response
from .utils import populate_database, trigger_report
from .models import Report
import uuid
from django.http import FileResponse
import threading
# Create your views here.

class PopulateView(views.APIView):

    def get(self, request, format = None):
        populate_database()
        return Response({}, status= status.HTTP_200_OK)
    

class GenerateReportView(views.APIView):

    def get(self,request,format=None):
        l_report_id = uuid.uuid4()
        l_new_report = Report.objects.create(report_id = l_report_id, status = 'running')
        t = threading.Thread(target=trigger_report, args=[l_report_id])
        t.setDaemon = True
        t.start()
        return Response({"report_id":l_report_id},status=status.HTTP_201_CREATED)
    
class ShowReportView(views.APIView):

    def get(self, request, report_id, format = None):

        try:

            l_report = Report.objects.get(report_id = report_id)

            if l_report.status == 'running':
                return Response({"message" : "Still running"}, status=status.HTTP_200_OK)
            
            else:
                csv_file = open('static/report.csv')
                response = Response(csv_file, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="your_file.csv"'
                return FileResponse(open('static/report.csv', 'rb'))

        except Exception as e:

            print(e)

            return Response({"message":"No report found"}, status=status.HTTP_404_NOT_FOUND)


