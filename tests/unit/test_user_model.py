from app.models.user import User

def test_user_password_hashing():
    u = User(email="a@a.com", role="customer")
    u.set_password("Password123")

    assert u.password_hash is not None
    assert u.password_hash != "Password123"
    assert u.check_password("Password123") is True
    assert u.check_password("WrongPassword") is False