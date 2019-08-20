from coordinator.api.models import ReleaseNote


def test_new_note(admin_client, db, release, study):
    """ Test basic response """
    assert ReleaseNote.objects.count() == 0
    resp = admin_client.get('http://testserver/release-notes')
    assert resp.status_code == 200
    assert resp.json()['count'] == 0

    resp = admin_client.post(
        "http://testserver/release-notes",
        data={
            "author": "test",
            "description": "Lorem ipsum",
            "release": "http://testserver/releases/" + release["kf_id"],
            "study": "http://testserver/studies/" + study.kf_id,
        },
    )

    assert resp.status_code == 201

    resp = admin_client.get('http://testserver/release-notes')
    assert resp.status_code == 200
    assert resp.json()['count'] == 1

    resp = admin_client.get('http://testserver/releases/'+release['kf_id'])
    assert resp.status_code == 200
    assert 'notes' in resp.json()
    assert len(resp.json()['notes']) == 1


def test_delete_note(admin_client, db, release, study, release_note):
    """ Test that note may be deleted """
    resp = admin_client.delete('http://testserver/release-notes/' +
                               release_note['kf_id'])
    assert resp.status_code == 204

    resp = admin_client.get('http://testserver/release-notes')
    assert resp.status_code == 200
    assert resp.json()['count'] == 0


def test_update_note(admin_client, db, release, study, release_note):
    """ Test that note may be updated """
    resp = admin_client.get('http://testserver/release-notes/' +
                            release_note['kf_id'])
    assert resp.json()['description'] != 'testing'

    resp = admin_client.patch('http://testserver/release-notes/' +
                              release_note['kf_id'],
                              {'description': 'testing'})
    assert resp.status_code == 200

    resp = admin_client.get('http://testserver/release-notes/' +
                            release_note['kf_id'])
    assert resp.json()['description'] == 'testing'


def test_filter_study(client, db, release, study, release_note):
    """ Test that notes may be filtered by study """
    resp = client.get('http://testserver/release-notes?study=SD_XXXXXXXX')
    assert resp.status_code == 400
    assert 'Select a valid choice' in resp.json()['study'][0]

    resp = client.get('http://testserver/release-notes?study='+study.kf_id)
    assert resp.status_code == 200
    assert resp.json()['count'] == 1


def test_filter_release(client, db, release, study,
                        release_note):
    """ Test that notes may be filtered by study """
    release_id = release['kf_id']
    resp = client.get(f'http://testserver/release-notes?release={release_id}')
    assert resp.status_code == 200
    assert resp.json()['count'] == 1

    resp = client.get('http://testserver/release-notes?release' +
                      release['kf_id'])
    assert resp.status_code == 200
    assert resp.json()['count'] == 1


def test_complex_filter(client, db, release, study,
                        release_note):
    """ Test more complex combinations of filters """
    url = (f"http://testserver/release-notes" +
           f"?release={release['kf_id']}&study=SD_XXXXXXXX")
    resp = client.get(url)
    assert resp.status_code == 400
    assert 'release' not in resp.json()
    assert 'study' in resp.json()

    url = (f"http://testserver/release-notes" +
           f"?release=RE_XXXXXXXX&study={study.kf_id}")
    resp = client.get(url)
    assert resp.status_code == 400
    assert 'release' in resp.json()
    assert 'study' not in resp.json()

    url = (f"http://testserver/release-notes" +
           f"?release={release['kf_id']}&study={study.kf_id}")
    resp = client.get(url)
    assert resp.json()['count'] == 1
