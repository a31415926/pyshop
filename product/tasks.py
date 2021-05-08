from shop.celery import app
from time import sleep
from product import services


@app.task
def test_celery(cnt):
    for i in range(cnt):
        sleep(0.5)
        print(i)


@app.task
def edit_price_in_category(lst_cats, type_edit, value_edit, is_edit_old_price):
    services.ProductServices.edit_price_products(
            lst_cats=lst_cats,
            type_edit = type_edit, 
            value_edit = value_edit, 
            is_edit_old_price = is_edit_old_price
    )