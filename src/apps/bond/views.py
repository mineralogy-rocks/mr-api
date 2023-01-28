# # -*- coding: UTF-8 -*-
import io
import re

from bs4 import BeautifulSoup
from django.http import FileResponse
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework import renderers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from svg.path import parse_path

from .serializers import SVGSerializer


class SVGView(APIView):

    renderer_classes = [
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]
    permission_classes = [
        AllowAny,
    ]
    serializer_class = SVGSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        wb = Workbook()
        ws = wb.active
        ws.append(
            [
                "id",
                "x",
                "y",
            ]
        )

        svg_str = serializer.validated_data["file"].read().decode("utf-8")

        soup = BeautifulSoup(svg_str, "html.parser")
        # get all the g elements with id containing uppercase letters
        g_elements = soup.find_all("g", {"id": re.compile(r"_[A-Z]*")})
        print(g_elements)
        for g in g_elements:
            for path in g.find_all("path"):
                d = path.get("d")
                path_data = parse_path(d)
                coordinates = []
                print(path_data)
                for segment in path_data:
                    coordinates.append((segment.start.real, segment.start.imag))
                ws.append(
                    [
                        g.get("id"),
                        coordinates[0][0],
                        coordinates[0][1],
                    ]
                )

        file_name = "coordinates.xlsx"

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Save the workbook to the buffer
        wb.save(buffer)

        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=True, filename=file_name)
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        response["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return response

        # return the excel file in the response
        # response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # response['Content-Disposition'] = 'attachment; filename=data.xlsx'
        # return response
