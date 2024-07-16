# LittleLemon REST API

## What is it?
This is the peer-reviewed REST API project required for the Meta Back-End Developer Professional Certification. Implements proper user authentication, user group permissions, filtering, pagination, and throttling.

## Scope
A fully functioning API project that allows client application developers to develop web and mobile applications through an API. People with different roles will be able to browse, add and edit menu items, place orders, browse orders, assign delivery crew to orders and finally deliver the orders.

### Error checking and proper status codes

| HTTP Status code | Reason |
|:----------------------|:--------------|
| 200 - OK              | For all successful GET, PUT, PATCH and DELETE calls|
| 201 - Created         | For all successful POST requests |
| 403 - Unauthorized    | If authorization fails for the current user token |
| 400 – Bad request  | If the request was made for a non-existing resource |


### User registration and token generation endpoints 

| Endpoint                | Role                                    | Method | Purpose                                                                               |
|-------------------------|-----------------------------------------|--------|---------------------------------------------------------------------------------------|
| `/api/users`            | No role required                        | `POST` | Creates a new user with name, email and password                                       |
| `/api/users/users/me/`  | Anyone with a valid user token          | `GET`  | Displays only the current user                                                         |
| `/token/login/`         | Anyone with a valid username and password | `POST` | Generates access tokens that can be used in other API calls in this project             |

### Menu-items endpoints

| Endpoint                        | Role                    | Method                      | Purpose                                                                   |
|---------------------------------|-------------------------|-----------------------------|---------------------------------------------------------------------------|
| `/api/menu-items`               | Customer, delivery crew | `GET`                       | Lists all menu items. Returns a `200 - Ok` HTTP status code                |
| `/api/menu-items`               | Customer, delivery crew | `POST, PUT, PATCH, DELETE`  | Denies access and returns `403 - Unauthorized` HTTP status code            |
| `/api/menu-items/{menuItem}`    | Customer, delivery crew | `GET`                       | Lists single menu item                                                    |
| `/api/menu-items/{menuItem}`    | Customer, delivery crew | `POST, PUT, PATCH, DELETE`  | Returns `403 - Unauthorized`                                               |
| `/api/menu-items`               | Manager                 | `GET`                       | Lists all menu items                                                      |
| `/api/menu-items`               | Manager                 | `POST`                      | Creates a new menu item and returns `201 - Created`                        |
| `/api/menu-items/{menuItem}`    | Manager                 | `GET`                       | Lists single menu item                                                    |
| `/api/menu-items/{menuItem}`    | Manager                 | `PUT, PATCH`                | Updates single menu item                                                  |
| `/api/menu-items/{menuItem}`    | Manager                 | `DELETE`                    | Deletes menu item                                                         |


### User group management endpoints

| Endpoint                                      | Role    | Method | Purpose                                                                                                                                                            |
|-----------------------------------------------|---------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/api/groups/manager/users`                   | Manager | `GET`   | Returns all managers                                                                                                                                               |
| `/api/groups/manager/users`                   | Manager | `POST`  | Assigns the user in the payload to the manager group and returns `201 - Created`                                                                                   |
| `/api/groups/manager/users/{userId}`          | Manager | `DELETE`| Removes this particular user from the manager group and returns `200 - Success` if everything is okay. If the user is not found, returns `404 - Not found`         |
| `/api/groups/delivery-crew/users`             | Manager | `GET`   | Returns all delivery crew                                                                                                                                          |
| `/api/groups/delivery-crew/users`             | Manager | `POST`  | Assigns the user in the payload to delivery crew group and returns `201 - Created`                                                                                 |
| `/api/groups/delivery-crew/users/{userId}`    | Manager | `DELETE`| Removes this user from the delivery crew group and returns `200 - Success` if everything is okay. If the user is not found, returns `404 - Not found`              |

### Cart management endpoints

| Endpoint                        | Role     | Method  | Purpose                                                                                         |
|---------------------------------|----------|---------|-------------------------------------------------------------------------------------------------|
| `/api/cart/menu-items`          | Customer | `GET`   | Returns current items in the cart for the current user token                                    |
| `/api/cart/menu-items`          | Customer | `POST`  | Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items |
| `/api/cart/menu-items`          | Customer | `DELETE`| Deletes all menu items created by the current user token                                        |

### Order management endpoints

| Endpoint                    | Role         | Method        | Purpose                                                                                                                                                                                                                               |
|-----------------------------|--------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/api/orders`               | Customer     | `GET`         | Returns all orders with order items created by this user                                                                                                                                                                              |
| `/api/orders`               | Customer     | `POST`        | Creates a new order item for the current user. Gets current cart items from the cart endpoints and adds those items to the order items table. Then deletes all items from the cart for this user.                                      |
| `/api/orders/{orderId}`     | Customer     | `GET`         | Returns all items for this order id. If the order ID doesn’t belong to the current user, it displays an appropriate HTTP error status code.                                                                                           |
| `/api/orders`               | Manager      | `GET`         | Returns all orders with order items by all users                                                                                                                                                                                      |
| `/api/orders/{orderId}`     | Customer     | `PUT, PATCH`  | Updates the order. A manager can use this endpoint to set a delivery crew to this order, and also update the order status to 0 or 1. If a delivery crew is assigned to this order and the `status = 0`, it means the order is out for delivery. If a delivery crew is assigned to this order and the `status = 1`, it means the order has been delivered. |
| `/api/orders/{orderId}`     | Manager      | `DELETE`      | Deletes this order                                                                                                                                                                                                                    |
| `/api/orders`               | Delivery crew| `GET`         | Returns all orders with order items assigned to the delivery crew                                                                                                                                                                     |
| `/api/orders/{orderId}`     | Delivery crew| `PATCH`       | A delivery crew can use this endpoint to update the order status to 0 or 1. The delivery crew will not be able to update anything else in this order.                                                                                   |
