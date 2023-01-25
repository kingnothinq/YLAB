Hello.

It is a laboratory project for the YLAB Academy. The project contains an FastAPI application run with ASGI uvicorn and connected to PostgreSQL DB.

The application simulates an API for restaraunt menu. 

API supports the next actions:
GET /api/v1/menus
Show a list of menus including the amount of related submenus and dishes.

GET /api/v1/menus/{target_menu_id}
Show menu including the amount of related submenus and dishes.

POST /api/v1/menus
Create a menu

PATCH /api/v1/menus/{target_menu_id}
Update a menu

DELETE /api/v1/menus/{target_menu_id}
Delete a menu

GET /api/v1/menus/{target_menu_id}/submenus
Show a list of submenus including the amount of related dishes.

GET /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}
Show submenu including the amount of related dishes.

POST /api/v1/menus/{target_menu_id}/submenus
Create a submenu

PATCH /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}
Update a menu

DELETE /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}
Delete a menu

GET /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes
Show a list of dishes

GET /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}
Show a dish

POST /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/disCreate a dish

PATCH /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}
Update a dish

DELETE /api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}
Delete a dish


Production:
1) docker compose -f docker-compose-prod.yml -p ylab build
2) docker compose -f docker-compose-prod.yml -p ylab up
3) test API with Postman collections from the tests folder

Test:
1) docker compose -f docker-compose-test.yml -p ylab_test build
2) docker compose -f docker-compose-test.yml -p ylab_test up
3) Windows: docker compose -f docker-compose-test.yml -p ylab_test logs
   Linux: docker compose -f docker-compose-test.yml -p ylab_test logs
