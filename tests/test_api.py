import pytest
import sys

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from os import environ, path, getcwd
from psycopg2 import connect

sys.path.append(getcwd())
environ["TEST"] = "True"
import app.api


client = TestClient(app.api.app)

@pytest.fixture(scope="session")
def session():
    dotenv_path = path.abspath(path.join(path.dirname(__file__), '..', '.env'))
    if path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    db_settings = {"database": environ.get('POSTGRES_TEST_DB'),
                   "user": environ.get('POSTGRES_USER'),
                   "password": environ.get('POSTGRES_PASSWORD'),
                   "host": environ.get('POSTGRES_TEST_HOST'),
                   "port": int(environ.get('POSTGRES_PORT'))}
    connection = connect(**db_settings)
    cursor = connection.cursor()
    app.api.cursor = cursor
    yield cursor
    connection.close()


@pytest.fixture
def setup_db(session):
    session.execute("""
    DROP TABLE IF EXISTS menus, submenus, dishes;
    CREATE TABLE menus (
        id SERIAL PRIMARY KEY, 
        title VARCHAR(150), 
        description VARCHAR(150));
    CREATE TABLE submenus (
        id SERIAL PRIMARY KEY, 
        menu INT REFERENCES menus (id) ON DELETE CASCADE,
        title VARCHAR(150), description VARCHAR(150));
    CREATE TABLE dishes (
        id SERIAL PRIMARY KEY, 
        submenu INT REFERENCES submenus (id) ON DELETE CASCADE,
        title VARCHAR(150),
        description VARCHAR(150),
        price VARCHAR(150))
    """)
    session.connection.commit()

@pytest.fixture(scope="session")
def item():
    return {"menu": None, "submenu": None, "dish": None}

def test_get_menus(session, setup_db, item):
    response = client.get("/api/v1/menus")
    assert response.status_code == 200
    assert response.json() == []

def test_get_menu():
    response = client.get("/api/v1/menus/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "menu not found"}

def test_create_menu():
    # Create menu
    data_req = {"title": "My menu 1", "description": "My menu description 1"}
    response = client.post("/api/v1/menus", json=data_req)
    item.menu = response.json()["id"]
    data_res = {"id": item.menu, "title": "My menu 1", "description": "My menu description 1"}
    assert response.status_code == 201
    assert response.json() == data_res

    # Check whether it was added or not (all submenus)
    response = client.get("/api/v1/menus")
    data_res["submenus_count"] = 0
    data_res["dishes_count"] = 0
    assert response.status_code == 200
    assert response.json() == [data_res]

    # Check whether it was added or not (by id)
    response = client.get(f"/api/v1/menus/{item.menu}")
    assert response.status_code == 200
    assert response.json() == data_res

def test_update_menu():
    # Update menu
    data_req = {"title": "My updated menu 1", "description": "My updated menu description 1"}
    data_res = {"id": item.menu, "title": "My updated menu 1", "description": "My updated menu description 1"}
    response = client.patch(f"/api/v1/menus/{item.menu}", json=data_req)
    assert response.status_code == 200
    assert response.json() == data_res

    # Check whether it was updated or not
    response = client.get(f"/api/v1/menus/{item.menu}")
    data_res["submenus_count"] = 0
    data_res["dishes_count"] = 0
    assert response.status_code == 200
    assert response.json() == data_res

def test_delete_menu():
    # Delete menu
    response = client.delete(f"/api/v1/menus/{item.menu}")
    assert response.status_code == 200

    # Check whether it was deleted or not
    response = client.get(f"/api/v1/menus/{item.menu}")
    assert response.status_code == 404
    assert response.json() == {"detail": "menu not found"}

@pytest.fixture
def setup_menu():
    data_req = {"title": "My menu 1", "description": "My menu description 1"}
    response = client.post("/api/v1/menus", json=data_req)
    item.menu = response.json()["id"]

def test_get_submenus():
    response = client.get(f"/api/v1/menus/{item.menu}/submenus")
    assert response.status_code == 200
    assert response.json() == []

def test_get_submenu():
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "submenu not found"}

def test_create_submenu(setup_menu):
    # Create submenu
    data_req = {"title": "My submenu 1", "description": "My submenu description 1"}
    response = client.post(f"/api/v1/menus/{item.menu}/submenus", json=data_req)
    item.submenu = response.json()["id"]
    data_res = {"id": item.submenu, "title": "My submenu 1", "description": "My submenu description 1"}
    assert response.status_code == 201
    assert response.json() == data_res

    # Check whether it was added or not (all submenus)
    response = client.get(f"/api/v1/menus/{item.menu}/submenus")
    data_res["dishes_count"] = 0
    assert response.status_code == 200
    assert response.json() == [data_res]

    # Check whether it was added or not (by id)
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}")
    assert response.status_code == 200
    assert response.json() == data_res

def test_update_submenu():
    # Update submenu
    data_req = {"title": "My updated menu 1", "description": "My updated menu description 1"}
    data_res = {"id": item.submenu, "title": "My updated menu 1", "description": "My updated menu description 1"}
    response = client.patch(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}", json=data_req)
    assert response.status_code == 200
    assert response.json() == data_res

    # Check whether it was updated or not (by id)
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}")
    data_res["dishes_count"] = 0
    assert response.status_code == 200
    assert response.json() == data_res

def test_delete_submenu():
    # Delete submenu
    response = client.delete(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}")
    assert response.status_code == 200

    # Check whether it was deleted or not
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}")
    assert response.status_code == 404
    assert response.json() == {"detail": "submenu not found"}

# Dishes

@pytest.fixture
def setup_submenu():
    data_req = {"title": "My submenu 1", "description": "My submenu description 1"}
    response = client.post(f"/api/v1/menus/{item.menu}/submenus", json=data_req)
    item.submenu = response.json()["id"]

def test_get_dishes():
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes")
    assert response.status_code == 200
    assert response.json() == []

def test_get_dish():
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "dish not found"}

def test_create_dish(setup_submenu):
    # Create dish
    data_req = {"title": "My dish 1", "description": "My dish description 1", "price": "12.50"}
    response = client.post(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes", json=data_req)
    item.dish = response.json()["id"]
    data_res = {"id": item.dish, "title": "My dish 1", "description": "My dish description 1", "price": "12.50"}
    assert response.status_code == 201
    assert response.json() == data_res

    # Check whether it was added or not (all submenus)
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes")
    assert response.status_code == 200
    assert response.json() == [data_res]

    # Check whether it was added or not (by id)
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes/{item.dish}")
    assert response.status_code == 200
    assert response.json() == data_res

def test_update_dish():
    # Update dish
    data_req = {"title": "My updated dish 1", "description": "My updated dish description 1", "price": "14.50"}
    data_res = {"id": item.dish, "title": "My updated dish 1", "description": "My updated dish description 1", "price": "14.50"}
    response = client.patch(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes/{item.dish}", json=data_req)
    assert response.status_code == 200
    assert response.json() == data_res

    # Check whether it was updated or not (by id)
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes/{item.dish}")
    assert response.status_code == 200
    assert response.json() == data_res

def test_delete_dish():
    # Delete submenu
    response = client.delete(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes/{item.dish}")
    assert response.status_code == 200

    # Check whether it was deleted or not
    response = client.get(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes/{item.dish}")
    assert response.status_code == 404
    assert response.json() == {"detail": "dish not found"}

# Data asset to check submenu and dishes counters
@pytest.fixture(scope="function")
def setup_full_menu(session):
    session.execute("""
    DROP TABLE IF EXISTS menus, submenus, dishes;
    CREATE TABLE menus (
        id SERIAL PRIMARY KEY,
        title VARCHAR(150),
        description VARCHAR(150));
    CREATE TABLE submenus (
        id SERIAL PRIMARY KEY,
        menu INT REFERENCES menus (id) ON DELETE CASCADE,
        title VARCHAR(150), description VARCHAR(150));
    CREATE TABLE dishes (
        id SERIAL PRIMARY KEY,
        submenu INT REFERENCES submenus (id) ON DELETE CASCADE,
        title VARCHAR(150),
        description VARCHAR(150),
        price VARCHAR(150))
    """)
    data_menu = {"title": "My menu 1", "description": "My menu description 1"}
    data_submenu = {"title": "My submenu 1", "description": "My submenu description 1"}
    data_dish = {"title": "My dish 1", "description": "My dish description 1", "price": "12.50"}

    ###############################################################################
    # Menu 1 (2 Submenus, 3 Dishes)
    item.menu = client.post("/api/v1/menus", json=data_menu).json()["id"]

    # Submenu 1 (2 Dishes)
    item.submenu = client.post(f"/api/v1/menus/{item.menu}/submenus", json=data_submenu).json()["id"]
    # Dish 1
    client.post(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes", json=data_dish)
    # Dish 2
    client.post(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes", json=data_dish)
    #
    # Submenu 2 (1 Dishes)
    item.submenu = client.post(f"/api/v1/menus/{item.menu}/submenus", json=data_submenu).json()["id"]
    # Dish 3
    client.post(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes", json=data_dish)
    ###############################################################################
    # Menu 2 (2 Submenus, 1 Dish)
    item.menu = client.post("/api/v1/menus", json=data_menu).json()["id"]
    #
    # Submenu 3 (1 Dish)
    item.submenu = client.post(f"/api/v1/menus/{item.menu}/submenus", json=data_submenu).json()["id"]
    # Dish 4
    client.post(f"/api/v1/menus/{item.menu}/submenus/{item.submenu}/dishes", json=data_dish)
    #
    # Submenu 4 (Empty)
    item.submenu = client.post(f"/api/v1/menus/{item.menu}/submenus", json=data_submenu).json()["id"]
    ###############################################################################
    # Menu 3 (Empty)
    client.post("/api/v1/menus", json=data_menu)

    session.connection.commit()

# Check submenus and dishes counters
def test_full_menu(session, setup_full_menu):
    response = client.get("/api/v1/menus")
    data_res = response.json()
    assert response.status_code == 200
    assert len(data_res) == 3
    assert data_res[0]["submenus_count"] == 2
    assert data_res[0]["dishes_count"] == 3
    assert data_res[1]["submenus_count"] == 2
    assert data_res[1]["dishes_count"] == 1
    assert data_res[2]["submenus_count"] == 0
    assert data_res[2]["dishes_count"] == 0

# Check dishes counter
def test_full_submenu(session, setup_full_menu):
    response = client.get("/api/v1/menus/1/submenus")
    data_res = response.json()
    assert response.status_code == 200
    assert len(data_res) == 2
    assert data_res[0]["dishes_count"] == 2
    assert data_res[1]["dishes_count"] == 1

# Check cascade delete
def test_full_delete(session, setup_full_menu):
    client.delete(f"/api/v1/menus/1")
    response = client.get("/api/v1/menus/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "menu not found"}