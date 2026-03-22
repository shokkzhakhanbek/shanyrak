from tests.conftest import USER_DATA, register_user, login_user, auth_header


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/auth/users/", json=USER_DATA)
        assert resp.status_code == 200

    def test_register_duplicate(self, client):
        register_user(client)
        resp = client.post("/auth/users/", json=USER_DATA)
        assert resp.status_code == 400

    def test_register_missing_fields(self, client):
        resp = client.post("/auth/users/", json={"username": "x@gmail.com"})
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        register_user(client)
        resp = client.post(
            "/auth/users/login",
            data={"username": USER_DATA["username"], "password": USER_DATA["password"]},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        register_user(client)
        resp = client.post(
            "/auth/users/login",
            data={"username": USER_DATA["username"], "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/auth/users/login",
            data={"username": "nobody@gmail.com", "password": "12345678"},
        )
        assert resp.status_code == 401


class TestGetProfile:
    def test_get_profile(self, client):
        register_user(client)
        token = login_user(client)
        resp = client.get("/auth/users/me", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == USER_DATA["username"]
        assert data["name"] == USER_DATA["name"]
        assert "password" not in data

    def test_get_profile_unauthorized(self, client):
        resp = client.get("/auth/users/me")
        assert resp.status_code == 401


class TestUpdateProfile:
    def test_update_profile(self, client):
        register_user(client)
        token = login_user(client)
        resp = client.patch(
            "/auth/users/me",
            json={"name": "Новое Имя", "city": "Астана"},
            headers=auth_header(token),
        )
        assert resp.status_code == 200

        me = client.get("/auth/users/me", headers=auth_header(token))
        assert me.json()["name"] == "Новое Имя"
        assert me.json()["city"] == "Астана"

    def test_update_partial(self, client):
        register_user(client)
        token = login_user(client)
        client.patch(
            "/auth/users/me",
            json={"phone": "+7 777 000 0000"},
            headers=auth_header(token),
        )
        me = client.get("/auth/users/me", headers=auth_header(token))
        assert me.json()["phone"] == "+7 777 000 0000"
        assert me.json()["name"] == USER_DATA["name"]

    def test_update_unauthorized(self, client):
        resp = client.patch("/auth/users/me", json={"name": "Hacker"})
        assert resp.status_code == 401