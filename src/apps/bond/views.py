# # -*- coding: UTF-8 -*-
import re

from django.http import HttpResponse
from rest_framework import renderers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from svg.path import parse_path
from bs4 import BeautifulSoup
import pandas as pd

from .serializers import SVGSerializer
# import pandas as pd



class SVGView(APIView):

    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer,]
    permission_classes = [AllowAny,]
    serializer_class = SVGSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get the file and parse it
        svg_str = serializer.validated_data["file"].read().decode("utf-8")

        soup = BeautifulSoup(svg_str, "html.parser")
        # get all the g elements with id containing uppercase letters
        g_elements = soup.find_all("g", {"id": re.compile(r"_[A-Z]*")})
        print(g_elements)
        data = []
        for g in g_elements:
            print(g.get("id"))
            for path in g.find_all("path"):
                d = path.get("d")
                path_data = parse_path(d)
                coordinates = []
                for segment in path_data:
                    coordinates.append((segment.start.real, segment.start.imag))
                data.append({g.get("id"): coordinates})

        return HttpResponse(data)
        # df = pd.DataFrame(data)

        # create an excel file with the data
        # excel_file = io.BytesIO()
        # df.to_excel(excel_file, index=False)
        # excel_file.seek(0)

        # return the excel file in the response
        # response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # response['Content-Disposition'] = 'attachment; filename=data.xlsx'
        # return response
