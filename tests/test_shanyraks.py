from tests.conftest import (
    USER_DATA, USER_DATA_2, SHANYRAK_DATA,
    register_user, login_user, auth_header, create_shanyrak,
)


class TestCreateShanyrak:
    def test_create_success(self, client):
        register_user(client)
        token = login_user(client)
        resp = client.post("/shanyraks/", json=SHANYRAK_DATA, headers=auth_header(token))
        assert resp.status_code == 200
        assert "id" in resp.json()

    def test_create_unauthorized(self, client):
        resp = client.post("/shanyraks/", json=SHANYRAK_DATA)
        assert resp.status_code == 401


class TestGetShanyrak:
    def test_get_success(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        resp = client.get(f"/shanyraks/{sid}")
        assert resp.status_code == 200
        assert resp.json()["price"] == SHANYRAK_DATA["price"]
        assert "user_id" in resp.json()

    def test_get_not_found(self, client):
        assert client.get("/shanyraks/999").status_code == 404


class TestUpdateShanyrak:
    def test_update_own(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        resp = client.patch(
            f"/shanyraks/{sid}",
            json={"price": 250000},
            headers=auth_header(token),
        )
        assert resp.status_code == 200
        assert client.get(f"/shanyraks/{sid}").json()["price"] == 250000

    def test_update_forbidden(self, client):
        register_user(client, USER_DATA)
        token1 = login_user(client)
        sid = create_shanyrak(client, token1)

        register_user(client, USER_DATA_2)
        token2 = login_user(client, USER_DATA_2["username"], USER_DATA_2["password"])
        resp = client.patch(
            f"/shanyraks/{sid}",
            json={"price": 999},
            headers=auth_header(token2),
        )
        assert resp.status_code == 403


class TestDeleteShanyrak:
    def test_delete_own(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        assert client.delete(f"/shanyraks/{sid}", headers=auth_header(token)).status_code == 200
        assert client.get(f"/shanyraks/{sid}").status_code == 404

    def test_delete_forbidden(self, client):
        register_user(client, USER_DATA)
        token1 = login_user(client)
        sid = create_shanyrak(client, token1)

        register_user(client, USER_DATA_2)
        token2 = login_user(client, USER_DATA_2["username"], USER_DATA_2["password"])
        assert client.delete(f"/shanyraks/{sid}", headers=auth_header(token2)).status_code == 403