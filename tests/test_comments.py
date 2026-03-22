from tests.conftest import (
    USER_DATA, USER_DATA_2,
    register_user, login_user, auth_header, create_shanyrak,
)


def add_comment(client, shanyrak_id, token, content="Отличная квартира!"):
    resp = client.post(
        f"/shanyraks/{shanyrak_id}/comments/",
        json={"content": content},
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    return resp


class TestCreateComment:
    def test_create_success(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        add_comment(client, sid, token)

    def test_create_unauthorized(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        resp = client.post(f"/shanyraks/{sid}/comments/", json={"content": "test"})
        assert resp.status_code == 401

    def test_create_shanyrak_not_found(self, client):
        register_user(client)
        token = login_user(client)
        resp = client.post(
            "/shanyraks/999/comments/",
            json={"content": "test"},
            headers=auth_header(token),
        )
        assert resp.status_code == 404


class TestGetComments:
    def test_get_comments(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        add_comment(client, sid, token, "Первый")
        add_comment(client, sid, token, "Второй")

        resp = client.get(f"/shanyraks/{sid}/comments/")
        assert resp.status_code == 200
        assert len(resp.json()["comments"]) == 2

    def test_total_comments_in_shanyrak(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        add_comment(client, sid, token, "Коммент 1")
        add_comment(client, sid, token, "Коммент 2")
        add_comment(client, sid, token, "Коммент 3")

        resp = client.get(f"/shanyraks/{sid}")
        assert resp.json()["total_comments"] == 3


class TestUpdateComment:
    def test_update_own(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        add_comment(client, sid, token)

        comments = client.get(f"/shanyraks/{sid}/comments/").json()["comments"]
        cid = comments[0]["id"]

        resp = client.patch(
            f"/shanyraks/{sid}/comments/{cid}",
            json={"content": "Обновлённый текст"},
            headers=auth_header(token),
        )
        assert resp.status_code == 200

    def test_update_forbidden(self, client):
        register_user(client, USER_DATA)
        token1 = login_user(client)
        sid = create_shanyrak(client, token1)
        add_comment(client, sid, token1)

        comments = client.get(f"/shanyraks/{sid}/comments/").json()["comments"]
        cid = comments[0]["id"]

        register_user(client, USER_DATA_2)
        token2 = login_user(client, USER_DATA_2["username"], USER_DATA_2["password"])
        resp = client.patch(
            f"/shanyraks/{sid}/comments/{cid}",
            json={"content": "Хак"},
            headers=auth_header(token2),
        )
        assert resp.status_code == 403


class TestDeleteComment:
    def test_delete_own(self, client):
        register_user(client)
        token = login_user(client)
        sid = create_shanyrak(client, token)
        add_comment(client, sid, token)

        comments = client.get(f"/shanyraks/{sid}/comments/").json()["comments"]
        cid = comments[0]["id"]

        assert client.delete(
            f"/shanyraks/{sid}/comments/{cid}", headers=auth_header(token)
        ).status_code == 200

        comments_after = client.get(f"/shanyraks/{sid}/comments/").json()["comments"]
        assert len(comments_after) == 0

    def test_delete_forbidden(self, client):
        register_user(client, USER_DATA)
        token1 = login_user(client)
        sid = create_shanyrak(client, token1)
        add_comment(client, sid, token1)

        comments = client.get(f"/shanyraks/{sid}/comments/").json()["comments"]
        cid = comments[0]["id"]

        register_user(client, USER_DATA_2)
        token2 = login_user(client, USER_DATA_2["username"], USER_DATA_2["password"])
        assert client.delete(
            f"/shanyraks/{sid}/comments/{cid}", headers=auth_header(token2)
        ).status_code == 403