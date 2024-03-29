# Дипломная работа к профессии Python-разработчик «API Сервис заказа товаров для розничных сетей».

## Описание

Приложение предназначено для автоматизации закупок в розничной сети через REST API.

**Внимание! Все взаимодействие с приложением ведется через API запросы. 
Реализация фронтенд-приложения возможна только по желанию обучающегося**

Пользователи сервиса:


**Клиент (покупатель):**

- Делает ежедневные закупки по каталогу, в котором
  представлены товары от нескольких поставщиков.
- В одном заказе можно указать товары от разных поставщиков.
- Пользователь может авторизироваться, регистрироваться и восстанавливать пароль через API.
    
**Поставщик:**

- Через API информирует сервис об обновлении прайса.
- Может включать и отключать прием заказов.
- Может получать список оформленных заказов (с товарами из его прайса).


### Задача

Необходимо разработать backend-часть сервиса заказа товаров для розничных сетей на Django Rest Framework.

**Базовая часть:**
* Разработка сервиса под готовую спецификацию (API);
* Возможность добавления настраиваемых полей (характеристик) товаров;
* Импорт товаров;
* Отправка накладной на email администратора (для исполнения заказа);
* Отправка заказа на email клиента (подтверждение приема заказа).

**Продвинутая часть:**
* Экспорт товаров;
* Админка заказов (проставление статуса заказа и уведомление клиента);
* Выделение медленных методов в отдельные асинхронные функции (email, импорт, экспорт).


1. Создать модели:
    1. Shop
        - name
        - url
    2. Category
        - shops (m2m)
        - name
    3. Product
        - category
        - name
    4. ProductInfo
        - product
        - shop
        - name
        - quantity
        - price
        - price_rrc
    5. Parameter
        - name
    6. ProductParameter
        - product_info
        - parameter
        - value
    7. Order
        - user
        - dt
        - status
    8. OrderItem
        - order
        - product
        - shop
        - quantity
    9. Contact
        - type
        - user
        - value
