# -*- coding: UTF-8 -*-
import json
import os
import time
from datetime import datetime
from datetime import timedelta

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils import timezone

from ...models.core import FormulaSource
from ...models.core import Status
from ...models.crystal import CrystalSystem
from ...models.mineral import MindatSync
from ...models.mineral import Mineral
from ...models.mineral import MineralCrystallography
from ...models.mineral import MineralFormula
from ...models.mineral import MineralHistory
from ...models.mineral import MineralStatus
from ...utils import send_email
from ...utils import shorten_text

MINDAT_API_URL = os.environ.get("MINDAT_API_URL")
MINDAT_API_USERNAME = os.environ.get("MINDAT_API_USERNAME")
MINDAT_API_PASSWORD = os.environ.get("MINDAT_API_PASSWORD")


class Command(BaseCommand):
    help = "syncs db with mindat.org"

    def handle(self, *args, **options):

        assert MINDAT_API_URL, "Please, add MINDAT_API_URL to your environment variables"
        assert MINDAT_API_USERNAME, "Please, add MINDAT_API_USERNAME to your environment variables"
        assert MINDAT_API_PASSWORD, "Please, add MINDAT_API_PASSWORD to your environment variables"

        sync_log = MindatSync.objects.filter(is_successful=True).order_by("-created_at").first()
        formula_mindat = FormulaSource.objects.get(name="mindat.org")
        formula_ima = FormulaSource.objects.get(name="IMA")

        if sync_log:
            last_datetime = sync_log.created_at - timedelta(hours=3)
        else:
            last_datetime = timezone.now() - timedelta(days=90)

        is_successful = True
        last_datetime = datetime.strftime(last_datetime, "%Y-%m-%d %H:%M:%S")
        # last_datetime = '2023-01-23 19:56:58'
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
                    "updated_at": last_datetime,
                    "non_utf": False,
                }
                r = requests.get(
                    MINDAT_API_URL + "/mr-items/sync",
                    params=query_params,
                    headers=headers,
                    timeout=10,
                )

                fetched = []
                entries_to_sync = []

                if r.status_code == 200:
                    response = r.json()
                    if response["results"]:
                        entries_to_sync += response["results"]

                    while True:
                        if "next" in response and response["next"]:
                            print(response["next"])
                            time.sleep(3)
                            r = requests.get(response["next"], headers=headers, timeout=100)
                            if r.status_code == 200:
                                response = r.json()
                                if response["results"]:
                                    entries_to_sync += response["results"]
                            else:
                                is_successful = False
                                break
                        else:
                            break
                else:
                    raise CommandError("Error while syncing with mindat.org")

                try:
                    for index, entry in enumerate(entries_to_sync):
                        name_ = entry["name"].strip()
                        is_updated, is_created = False, False

                        mineral, created_ = Mineral.objects.get_or_create(name=name_)
                        if created_:
                            is_updated, is_created = True, True
                            mineral.mindat_id = entry["id"]
                            mineral.ima_symbol = entry["ima_symbol"] or None
                            mineral.description = entry["description"] or None
                            mineral.save()

                            if entry["ima_symbol"]:
                                status = Status.objects.get(status_id=0)
                                MineralStatus.objects.create(mineral=mineral, status=status, needs_revision=True)

                        else:
                            if (
                                mineral.mindat_id == entry["id"]
                                and mineral.ima_symbol == (entry["ima_symbol"] or None)
                                and mineral.description == (entry["description"] or None)
                            ):
                                pass
                            else:
                                is_updated = True
                                mineral.mindat_id = entry["id"]
                                mineral.ima_symbol = entry["ima_symbol"] or None
                                mineral.description = entry["description"] or None
                                mineral.save()

                        if entry["description"]:
                            entry["description"] = shorten_text(entry["description"], limit=500, html=True)

                        formula_note = entry["formula_note"] or None
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

                        if entry["ima_formula"]:
                            entry_, created_ = MineralFormula.objects.get_or_create(
                                mineral=mineral,
                                formula=entry["ima_formula"],
                                source=formula_ima,
                                defaults={
                                    "note": formula_note,
                                },
                            )

                            if created_:
                                is_updated = True

                        if entry["crystal_system"]:
                            try:
                                crystal_system = CrystalSystem.objects.get(name=entry["crystal_system"].lower())
                                entry_, updated_ = MineralCrystallography.objects.update_or_create(
                                    mineral=mineral,
                                    defaults={
                                        "crystal_system": crystal_system,
                                    },
                                )
                                if updated_:
                                    is_updated = True
                            except CrystalSystem.DoesNotExist:
                                pass

                        if any(
                            [
                                entry["discovery_year"],
                                entry["ima_year"],
                                entry["publication_year"],
                                entry["approval_year"],
                            ]
                        ):
                            entry_, updated_ = MineralHistory.objects.update_or_create(
                                mineral=mineral,
                                defaults={
                                    "discovery_year": entry["discovery_year"] or None,
                                    "ima_year": entry["ima_year"] or None,
                                    "approval_year": entry["approval_year"] or None,
                                    "publication_year": entry["publication_year"] or None,
                                },
                            )
                            if updated_:
                                is_updated = True

                        if is_updated:
                            print(name_)
                            entry["action"] = "New entries" if is_created else "Updated entries"
                            entry["admin_link"] = mineral.get_admin_url()
                            entry["mindat_link"] = f"https://www.mindat.org/min-{entry['id']}.html"

                            fetched.append(entry)

                except Exception as e:
                    raise CommandError("Error while saving synced data: " + str(e))

                if fetched:
                    sync_log = MindatSync.objects.create(values=fetched, is_successful=is_successful)
                    self.stdout.write(self.style.SUCCESS("Successfully synced mindat.org"))
                else:
                    sync_log = MindatSync.objects.create(values=None, is_successful=is_successful)
                    self.stdout.write(self.style.SUCCESS("All good, there's nothing to sync!"))

                context = {
                    "minerals": fetched,
                    "base_url": f"{settings.SCHEMA}://{settings.BACKEND_DOMAIN}",
                    "domain": settings.FRONTEND_DOMAIN,
                    "link": sync_log.get_absolute_url(),
                }
                send_email(
                    subject="Mindat synchronization report",
                    template="sync/sync-report.html",
                    recepients=["liubomyr.gavryliv@gmail.com"],
                    context=context,
                )
            else:
                raise CommandError("Error while authorizing with api.mindat.org")

        except Exception as e:
            raise CommandError(e)
