import requests
from django.conf import settings
from coordinator.api.models import Study


def sync():
    if not settings.DATASERVICE_URL:
        return [], []

    resp = requests.get(settings.DATASERVICE_URL + "/studies?limit=100")
    resp.raise_for_status()

    studies = Study.objects.all()
    new = []
    deleted = []

    for study in resp.json()["results"]:
        try:
            s = Study.objects.get(kf_id=study["kf_id"])
        # We don't know about the study, create it
        except Study.DoesNotExist:
            s = Study(
                kf_id=study["kf_id"],
                name=study["name"],
                visible=study["visible"],
                created_at=study["created_at"],
            )
            s.save()
            new.append(s)
            continue

        # Check for updated fields
        for field in ["name", "visible"]:
            if getattr(s, field) != study[field]:
                setattr(s, field, study[field])
        s.save()

    # Check if any studies were deleted from the dataservice
    coord_studies = set(s.kf_id for s in studies)
    ds_studies = set(s["kf_id"] for s in resp.json()["results"])
    missing_studies = coord_studies - ds_studies
    deleted = list(missing_studies)
    for study in missing_studies:
        s = Study.objects.get(kf_id=study)
        s.deleted = True
        s.save()

    return new, deleted
