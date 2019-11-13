import pytest
from coordinator.api.models import Study
from coordinator.api.factories.study import StudyFactory
from coordinator.api.factories.release import ReleaseFactory


ALL_STUDIES = """
query (
    $kfId: String,
    $visible: Boolean,
    $deleted: Boolean,
    $nameContains: String,
    $createdBefore: Float,
    $createdAfter: Float,
    $orderBy: String,
    $state: String
) {
    allStudies(
        kfId: $kfId,
        visible: $visible,
        deleted: $deleted,
        nameContains: $nameContains,
        createdBefore: $createdBefore,
        createdAfter: $createdAfter,
        orderBy: $orderBy
    ) {
        edges {
            node {
                id
                kfId
                name
                visible
                deleted
                createdAt
                releases(state: $state) {
                    edges {
                        node {
                            id
                            kfId
                            version
                        }
                    }
                }
            }
        }
    }
}
"""


@pytest.mark.parametrize(
    "user_type,expected",
    [("admin", 40), ("dev", 40), ("user", 10), ("anon", 10)],
)
def test_list_all_permissions(db, test_client, user_type, expected):
    """
    ADMIN - Can query all studies
    DEV - Can query all studies
    USER - Can query all non-deleted, visible studies
    anonomous - Can query all non-deleted, visible studies
    """

    studies = StudyFactory.create_batch(10, visible=True)
    studies = StudyFactory.create_batch(10, visible=False)
    studies = StudyFactory.create_batch(10, deleted=True)
    studies = StudyFactory.create_batch(10, visible=True, deleted=True)

    client = test_client(user_type)
    resp = client.post("/graphql", data={"query": ALL_STUDIES})
    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allStudies"]["edges"]) == expected


def test_subquery(db, admin_client):
    """
    Test that a study's releases may be subqueried correctly
    """
    study = StudyFactory()
    other_study = StudyFactory()
    release1 = ReleaseFactory(
        state="published", studies=[study], version="1.1.1"
    )
    release2 = ReleaseFactory(state="staged", studies=[study], version="1.1.2")
    # This release won't include the study of interest
    release3 = ReleaseFactory(
        state="published", studies=[other_study], version="1.1.3"
    )

    variables = {"state": "published", "kfId": study.kf_id}
    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": ALL_STUDIES, "variables": variables},
    )

    # Test that the correct number of releases are returned
    assert len(resp.json()["data"]["allStudies"]["edges"]) == 1
    study = resp.json()["data"]["allStudies"]["edges"][0]["node"]
    assert len(study["releases"]["edges"]) == 1
    release = study["releases"]["edges"][0]["node"]
    assert release["version"] == "1.1.1"
    assert release["kfId"] == release1.kf_id

    variables = {"state": "published", "kfId": other_study.kf_id}
    resp = admin_client.post(
        "/graphql",
        format="json",
        data={"query": ALL_STUDIES, "variables": variables},
    )
    assert len(resp.json()["data"]["allStudies"]["edges"]) == 1
    study = resp.json()["data"]["allStudies"]["edges"][0]["node"]
    assert len(study["releases"]["edges"]) == 1
    release = study["releases"]["edges"][0]["node"]
    assert release["version"] == "1.1.3"
    assert release["kfId"] == release3.kf_id
