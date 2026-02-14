from app.models.user import User

def test_register_then_login(client, app):
    email = "test1@example.com"
    password = "Pass12345"

    r = client.post("/register", data={"email": email, "password": password}, follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        assert User.query.filter_by(email=email).first() is not None

    l = client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
    assert l.status_code == 200

def test_logout(client, app):
    email = "test2@example.com"
    password = "Pass12345"

    client.post("/register", data={"email": email, "password": password})
    client.post("/login", data={"email": email, "password": password})

    out = client.post("/logout", follow_redirects=True)
    assert out.status_code == 200