# -*- coding: UTF-8 -*-
import json
import os
import time
from datetime import datetime
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
            last_datetime = datetime.strftime(sync_log.created_at, "%Y-%m-%d %H:%M:%S")
        else:
            last_datetime = timezone.now() - timedelta(days=60)

        # TODO: remove after testing
        last_datetime = timezone.now() - timedelta(days=60)
        print(last_datetime)

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
                        fetched = fetched[:10]
                        try:
                            for index, entry in enumerate(fetched):
                                name_ = entry["name"].strip()
                                is_updated = False

                                mineral, created_ = Mineral.objects.get_or_create(name=name_)
                                if created_:
                                    is_updated = True
                                    mineral(
                                        mindat_id=entry["id"],
                                        description=entry["description"] or None,
                                    )
                                    mineral.save()
                                else:
                                    if mineral.mindat_id == entry["id"] and mineral.description == (
                                        entry["description"] or None
                                    ):
                                        pass
                                    else:
                                        is_updated = True
                                        mineral.mindat_id = entry["id"]
                                        mineral.description = entry["description"] or None
                                        mineral.save()

                                formula_note = entry["formulanotes"] or None
                                if entry["formula"]:
                                    entry_, created_ = MineralFormula.objects.get_or_create(
                                        mineral=mineral,
                                        formula=entry["formula"],
                                        source=formula_mindat,
                                        defaults={
                                            "note": formula_note,
                                        },
                                    )
                                    if created_:
                                        is_updated = True

                                if entry["imaformula"]:
                                    entry_, created_ = MineralFormula.objects.get_or_create(
                                        mineral=mineral,
                                        formula=entry["formula"],
                                        source=formula_ima,
                                        defaults={
                                            "note": formula_note,
                                        },
                                    )

                                    if created_:
                                        is_updated = True

                                if any(
                                    [
                                        entry["yeardiscovery"],
                                        entry["imayear"],
                                        entry["publication_year"],
                                        entry["approval_year"],
                                    ]
                                ):
                                    entry_, updated_ = MineralHistory.objects.update_or_create(
                                        mineral=mineral,
                                        defaults={
                                            "discovery_year": entry["yeardiscovery"] or None,
                                            "ima_year": entry["imayear"] or None,
                                            "approval_year": entry["approval_year"] or None,
                                            "publication_year": entry["publication_year"] or None,
                                        },
                                    )
                                    if updated_:
                                        is_updated = True

                                if not is_updated:
                                    fetched.pop(index)
                            if fetched:
                                MindatSync.objects.create(values=fetched)
                                self.stdout.write(
                                    self.style.SUCCESS("Successfully synced mindat.org")
                                )
                            else:
                                MindatSync.objects.create(values=None)
                                self.stdout.write(
                                    self.style.SUCCESS("All good, there's nothing to sync!")
                                )
                        except Exception as e:
                            raise CommandError("Error while saving synced data: " + str(e))
                    else:
                        self.stdout.write(self.style.SUCCESS("All good, there's nothing to sync!"))
                else:
                    raise CommandError("Error while syncing with mindat.org")
            else:
                raise CommandError("Error while authorizing with api.mindat.org")

        except Exception as e:
            raise CommandError(e)
