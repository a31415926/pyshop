def viewed_products(data):
    data = dict(reversed(list(data.items())))
    responce_html = ''
    for i in data.values():
        responce_html += (
            f'<div class="card" style="width: 18rem;">'
            f'<div class="card-body">'
            f'<h5 class="card-title">{i["title"]}</h5>'
            f'<p class="card-text">{i.get("desc")}</p>'
            f'<a href="/shop/product/{i.get("id")}" class="btn btn-primary">open page</a></div></div>'
            
        )
    return responce_html


def my_wishlist(data):
    responce_html = ''
    for item in data:
        product = item.product
        responce_html += (
            f'<div class="card" style="flex:25%">'
            f'<div class="card-body">'
            f'<h5 class="card-title"><a href="/shop/product/{product.id}">{product.title}</a></h5>'
            f'<p class="card-text">{product.price}</p>'
            f'<button type="button" class="btn btn-primary" onclick="wishlist({product.id}, \'del_for_wishlist\')" id="btn_wishlist">Удалить из вишлиста</button>'
            f'<input type="number" step="1" min=1 name="cnt" start="1" value="1" id="cnt_product_{product.id}">'
            f'<span class="btn_basket_{product.id}"><button type="submit" onclick="add2basket({product.id})" id="btn_add2basket">Добавить в корзину</button></span>'
            '</div></div>'            
        )
    return responce_html
