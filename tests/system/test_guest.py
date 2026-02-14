def test_home_guest(client):
    r = client.get("/")
    assert r.status_code == 200

def test_search_guest(client):
    r = client.get("/search")
    assert r.status_code == 200