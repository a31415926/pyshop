from product import models
import re


class ProductServices:

    def data_preparation_edit_price(lst_data) -> dict :
        """ Подготовка данных для массовой замены цен в категориях
            type_edit - тип изменения (фиксированный/проценты)
            value_edit - на сколько изменять цену
            is_edit_old_price - устанавливать ли "Цена" в "Старая цена"
            lst_cats_id - список IDs категорий
         """
        context_data = {}
        context_data['type_edit'] = lst_data.get('type_edit', 'fix')
        context_data['is_edit_old_price'] = lst_data.get('is_edit_old_price', False)
        context_data['value_edit'] = 0
        try:
            context_data['value_edit'] = float(lst_data.get('value_edit_price', 0))
        except ValueError:
            context_data['value_edit'] = 0
        mask_cats_edit = 'id_cat_'
        r = re.compile(f'{mask_cats_edit}.*')
        lts_cats = list(filter(r.match, lst_data))
        context_data['lst_cats_id'] = []
        for category in lts_cats:
            try:
                id_category = int(category[len(mask_cats_edit):])
                context_data['lst_cats_id'].append(id_category)
            except ValueError:
                pass
        return context_data
        


    def get_all_products_in_categories(lts_categories: list):
        """ lst_categories - список с ID категорий. 
        возвращает QuerySet со всеми товарами категорий  """
        return models.Product.objects.filter(cid__pk__in = lts_categories)


    def edit_price_products(products, type_edit: str, value_edit: float, is_edit_old_price = False):

        for product in products:
            new_price = product.price
            if type_edit == 'fix':
                new_price = product.price + value_edit
            elif type_edit == 'relative':
                new_price = product.price + product.price * value_edit/100
            new_price = new_price if new_price>= 0 else 0

            if is_edit_old_price:
                product.old_price = product.price
            
            product.price = new_price
            product.save()
        