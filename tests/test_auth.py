import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'email': 'a', 'password': 'a', 'name': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            'select * from user where email = \'a\'',
        ).fetchone() is not None

@pytest.mark.parametrize(('email', 'password', 'name', 'message'),( 
    ('', '', '', b'Email is required.'),
    ('a@bar.com', '', '', b'Password is required.'),
    ('a@bar.com', 'a', '', b'Name is required.'),
    ('foo@bar.com', 'test', 'Foo', b'already registered.'),
))
def test_register_validate_input(client, email, password, name, message):
    response = client.post(
        '/auth/register',
        data={'name': name, 'email': email, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['email'] == 'foo@bar.com'

@pytest.mark.parametrize(('email', 'password', 'message'), (
    ('a', 'test', b'Incorrect email.'),
    ('foo@bar.com', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, email, password, message):
    response = auth.login(email, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
