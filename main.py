from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from os import environ, path
from pydantic import BaseModel
from psycopg2 import connect
from uvicorn import run


# Load environment
dotenv_path = path.join(path.dirname(__file__), '.env')
if path.exists(dotenv_path):
    load_dotenv(dotenv_path)
db_type = environ.get('DB_TYPE')
db_ip = environ.get('DB_HOST')
db_port = int(environ.get('DB_PORT'))
db_user = environ.get('DB_USER')
db_pass = environ.get('DB_PASSWORD')
app_ip = environ.get('WSGI_HOST')
app_port = int(environ.get('WSGI_PORT'))


# FastAPI application and request body
class Menu(BaseModel):
    title: str
    description: str

class Dish(Menu):
    price: str

app = FastAPI()


# Database
connection = connect(user=db_user, password=db_pass, host=db_ip, port=db_port, database=db_type)
cursor = connection.cursor()
cursor.execute("""
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
connection.commit()


# Menus
@app.get("/api/v1/menus")
async def get_menus():
    cursor.execute("""
    SELECT
        m.id::text,
        m.title,
        m.description,
        COUNT(DISTINCT s.id),
        COUNT(DISTINCT d.id)
    FROM menus m
    LEFT OUTER JOIN submenus s ON m.id = s.menu
    LEFT OUTER JOIN dishes d ON s.id = d.submenu
    GROUP BY m.id
    """)
    values = cursor.fetchall()
    if values:
        keys = ['id', 'title', 'description', 'submenus_count', 'dishes_count']
        return [dict(zip(keys, value)) for value in values]
    else:
        return values

@app.get("/api/v1/menus/{target_menu_id}")
async def get_menu(target_menu_id: int):
    cursor.execute(f"""
    SELECT
        m.id::text,
        m.title,
        m.description,
        COUNT(DISTINCT s.id),
        COUNT(DISTINCT d.id)
    FROM menus m
    LEFT OUTER JOIN submenus s ON m.id = s.menu
    LEFT OUTER JOIN dishes d ON s.id = d.submenu
    WHERE m.id = {target_menu_id}
    GROUP BY m.id
    """)
    values = cursor.fetchone()
    if values:
        keys = ['id', 'title', 'description', 'submenus_count', 'dishes_count']
        return dict(zip(keys, values))
    else:
        raise HTTPException(status_code=404, detail="menu not found")

@app.post("/api/v1/menus", status_code=201)
async def create_menu(menu: Menu):
    cursor.execute(f"INSERT INTO menus (title, description) VALUES ('{menu.title}', '{menu.description}') RETURNING id")
    return {"id": str(cursor.fetchone()[0]), "title": menu.title, "description": menu.description}

@app.patch("/api/v1/menus/{target_menu_id}")
async def update_menu(target_menu_id: int, menu: Menu):
    cursor.execute(f"UPDATE menus SET (title, description) = ('{menu.title}', '{menu.description}') "
                   f"WHERE id = {target_menu_id}")
    return {"id": str(target_menu_id), "title": menu.title, "description": menu.description}

@app.delete("/api/v1/menus/{target_menu_id}")
async def delete_menu(target_menu_id: int):
    return cursor.execute(f"DELETE FROM menus WHERE id={target_menu_id}")

# Submenus
@app.get("/api/v1/menus/{target_menu_id}/submenus")
async def get_submenus(target_menu_id: int):
    cursor.execute(f"""
    SELECT
        s.id::text,
        s.title,
        s.description,
        COUNT(DISTINCT d.id)
    FROM menus m
    INNER JOIN submenus s ON m.id = s.menu
    LEFT OUTER JOIN dishes d ON s.id = d.submenu
    WHERE m.id = {target_menu_id}
    GROUP BY s.id
    """)
    values = cursor.fetchall()
    if values:
        keys = ['id', 'title', 'description', 'dishes_count']
        return [dict(zip(keys, value)) for value in values]
    else:
        return values

@app.get("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}")
async def get_submenu(target_menu_id: int, target_submenu_id: int):
    cursor.execute(f"""
    SELECT
        s.id::text,
        s.title,
        s.description,
        COUNT(DISTINCT d.id)
    FROM menus m
    INNER JOIN submenus s ON m.id = s.menu
    LEFT OUTER JOIN dishes d ON s.id = d.submenu
    WHERE m.id = {target_menu_id} AND s.id = {target_submenu_id}
    GROUP BY s.id
    """)
    values = cursor.fetchone()
    if values:
        keys = ['id', 'title', 'description', 'dishes_count']
        return dict(zip(keys, values))
    else:
        raise HTTPException(status_code=404, detail="submenu not found")

@app.post("/api/v1/menus/{target_menu_id}/submenus", status_code=201)
async def create_submenu(target_menu_id: int, menu: Menu):
    cursor.execute(f"INSERT INTO submenus (menu, title, description)"
                   f"VALUES ({target_menu_id}, '{menu.title}', '{menu.description}')"
                   f"RETURNING id")
    return {"id": str(cursor.fetchone()[0]), "title": menu.title, "description": menu.description}

@app.patch("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}")
async def update_submenu(target_menu_id: int, target_submenu_id: int, menu: Menu):
    cursor.execute(f"UPDATE submenus SET (title, description) = ('{menu.title}', '{menu.description}') "
                   f"WHERE menu={target_menu_id} AND id={target_submenu_id}")
    return {"id": str(target_submenu_id), "title": menu.title, "description": menu.description}

@app.delete("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}")
async def delete_submenu(target_menu_id: int, target_submenu_id: int):
    return cursor.execute(f"DELETE FROM submenus WHERE menu={target_menu_id} AND id={target_submenu_id}")

# Dishes
@app.get("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes")
async def get_dishes(target_menu_id: int, target_submenu_id: int):
    cursor.execute(f"""
    SELECT
        d.id::text,
        d.title,
        d.description,
        d.price
    FROM menus m
    INNER JOIN submenus s ON m.id = s.menu
    INNER JOIN dishes d ON s.id = d.submenu
    WHERE m.id = {target_menu_id} AND s.id = {target_submenu_id}
    GROUP BY d.id
    """)
    values = cursor.fetchall()
    if values:
        keys = ['id', 'title', 'description', 'price']
        return [dict(zip(keys, value)) for value in values]
    else:
        return values

@app.get("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def get_dish(target_menu_id: int, target_submenu_id: int, target_dish_id: int):
    cursor.execute(f"""
    SELECT
        d.id::text,
        d.title,
        d.description,
        d.price
    FROM menus m
    INNER JOIN submenus s ON m.id = s.menu
    LEFT OUTER JOIN dishes d ON s.id = d.submenu
    WHERE m.id = {target_menu_id} AND s.id = {target_submenu_id} AND d.id = {target_dish_id}
    GROUP BY d.id
    """)
    values = cursor.fetchone()
    if values:
        keys = ['id', 'title', 'description', 'price']
        return dict(zip(keys, values))
    else:
        raise HTTPException(status_code=404, detail="dish not found")

@app.post("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes", status_code=201)
async def create_submenu(target_submenu_id: int, dish: Dish):
    cursor.execute(f"INSERT INTO dishes (submenu, title, description, price) "
                   f"VALUES ('{target_submenu_id}', '{dish.title}', '{dish.description}', '{dish.price}') "
                   f"RETURNING id")
    return {"id": str(cursor.fetchone()[0]), "title": dish.title, "description": dish.description, "price": dish.price}

@app.patch("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def update_submenu(target_dish_id: int, dish: Dish):
    cursor.execute(f"UPDATE dishes SET (title, description, price) = ('{dish.title}', '{dish.description}', '{dish.price}') "
                   f"WHERE id={target_dish_id}")
    return {"id": str(target_dish_id), "title": dish.title, "description": dish.description, "price": dish.price}

@app.delete("/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def delete_submenu(target_dish_id: int):
    return cursor.execute(f"DELETE FROM dishes WHERE id={target_dish_id}")


if __name__ == "__main__":
    run(app, host=app_ip, port=app_port)
