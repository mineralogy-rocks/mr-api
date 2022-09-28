# -*- coding: UTF-8 -*-
import json
import os
import time
from datetime import timedelta

import requests
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils import timezone

from ...models.core import FormulaSource
from ...models.mineral import MindatSync
from ...models.mineral import Mineral
from ...models.mineral import MineralFormula
from ...models.mineral import MineralHistory

MINDAT_API_URL = os.environ.get("MINDAT_API_URL")
MINDAT_API_USERNAME = os.environ.get("MINDAT_API_USERNAME")
MINDAT_API_PASSWORD = os.environ.get("MINDAT_API_PASSWORD")


class Command(BaseCommand):
    help = "syncs db with mindat.org"

    def handle(self, *args, **options):

        assert MINDAT_API_URL
        assert MINDAT_API_USERNAME
        assert MINDAT_API_PASSWORD

        sync_log = MindatSync.objects.order_by("-created_at").first()
        formula_mindat = FormulaSource.objects.get(name="mindat.org")
        formula_ima = FormulaSource.objects.get(name="IMA")

        if sync_log:
            last_datetime = sync_log.values("created_at")
        else:
            last_datetime = timezone.now() - timedelta(days=1)

        try:
            r = requests.post(
                MINDAT_API_URL + "/api-token-auth/",
                data=json.dumps({"username": MINDAT_API_USERNAME, "password": MINDAT_API_PASSWORD}),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if r.status_code == 200:
                token = r.json()["token"]
                headers = {"Authorization": "Token " + token}
                query_params = {
                    "sync_datetime": last_datetime,
                    "fields": "id,name,imayear,yeardiscovery,publication_year,approval_year,formula,formulanotes,imaformula,description",
                    "expand": "description,publication_year,approval_year,formulanotes",
                    "non_utf": False,
                }
                r = requests.get(
                    MINDAT_API_URL + "/minerals/",
                    params=query_params,
                    headers=headers,
                    timeout=10,
                )

                if r.status_code == 200:
                    fetched = []
                    response = r.json()
                    if response["results"]:
                        fetched += response["results"]

                    while True:
                        if "next" in response and response["next"]:
                            time.sleep(3)
                            r = requests.get(response["next"], headers=headers, timeout=10)
                            if r.status_code == 200:
                                response = r.json()
                                if response["results"]:
                                    fetched += response["results"]
                                print(fetched)
                            else:
                                break
                        else:
                            break

                    if fetched:
                        print(fetched)
                        fetched = fetched[:1]
                        try:
                            for entry in fetched:
                                mineral, created = Mineral.objects.update_or_create(
                                    name=entry["name"],
                                    defaults={
                                        "mindat_id": entry["id"],
                                        "description": entry["description"],
                                    },
                                )
                                if entry["formula"]:
                                    formula_note = entry["formulanotes"] or None

                                    MineralFormula.objects.get_or_create(
                                        mineral=mineral,
                                        formula=entry["formula"],
                                        source=formula_mindat,
                                        defaults={
                                            "note": formula_note,
                                        },
                                    )

                                if entry["imaformula"]:
                                    MineralFormula.objects.get_or_create(
                                        mineral=mineral,
                                        formula=entry["formula"],
                                        source=formula_ima,
                                        defaults={
                                            "note": formula_note,
                                        },
                                    )

                                if any(
                                    entry["yeardiscovery"],
                                    entry["imayear"],
                                    entry["publication_year"],
                                    entry["approval_year"],
                                ):

                                    MineralHistory.objects.get_or_create(
                                        mineral=mineral,
                                        discovery_year=entry["yeardiscovery"] or None,
                                        ima_year=entry["imayear"] or None,
                                        approval_year=entry["approval_year"] or None,
                                        publication_year=entry["publication_year"] or None,
                                        defaults={
                                            "discovery_year": entry["yeardiscovery"] or None,
                                            "ima_year": entry["imayear"] or None,
                                            "approval_year": entry["approval_year"] or None,
                                            "publication_year": entry["publication_year"] or None,
                                        },
                                    )

                            MindatSync.objects.create(values=fetched)
                        except Exception as e:
                            raise CommandError("Error while saving synced data: " + str(e))

                else:
                    raise CommandError("Error while syncing with mindat.org")
            else:
                raise CommandError("Error while authorizing with api.mindat.org")

        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS("Successfully synced mindat.org"))
