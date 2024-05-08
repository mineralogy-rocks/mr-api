# # -*- coding: UTF-8 -*-
import io
import re

from bs4 import BeautifulSoup
from django.http import FileResponse
from openpyxl import Workbook
from rest_framework import renderers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from svg.path import parse_path

from .serializers import SVGSerializer

path_elements = [
    {"id": "_T-O_", "d": "M19,101.28H93"},
    {"id": "_T-O_-2", "d": "M111,101.28h70"},
    {"id": "_T-O_-3", "d": "M102.5,91.78V21.78"},
    {"id": "_T-O_-4", "d": "M102.5,180.78V110.78"},
]


class SVGView(APIView):

    renderer_classes = [
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
    ]
    permission_classes = [
        IsAuthenticated,
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
                "x1",
                "y1",
                "x2",
                "y2",
            ]
        )

        svg_str = serializer.validated_data["file"].read().decode("utf-8")
        soup = BeautifulSoup(svg_str, "html.parser")

        # get all the g elements with id containing uppercase letters
        g_elements = soup.find_all("g", {"id": re.compile(r"_[A-Z]*")})
        labels = soup.find_all("text", {"class": "cls-2"})

        # for label in labels:
        #     x, y = label.get("transform").split("(")[1].split(")")[0].split(" ")

        for g in g_elements:
            for path in g.find_all("path"):
                d = path.get("d")
                path_data = parse_path(d)
                coordinates = []
                print(path_data)
                coordinates.append(
                    (path_data[1].start.real, path_data[1].start.imag, path_data[1].end.real, path_data[1].end.imag)
                )
                ws.append(
                    [
                        g.get("id"),
                        coordinates[0][0],
                        coordinates[0][1],
                        coordinates[0][2],
                        coordinates[0][3],
                    ]
                )

        file_name = "coordinates.xlsx"

        buffer = io.BytesIO()
        wb.save(buffer)

        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=True, filename=file_name)
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        response["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return response
