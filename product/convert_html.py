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