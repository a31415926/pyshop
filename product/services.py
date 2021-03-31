from product import models
import re
from importlib import import_module
from django.conf import settings
import csv, xlsxwriter
import requests
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError



class ProductServices:

    def export_to_file(type_file):
        if type_file == 'csv':
            with open('testss.csv', 'w', newline='',encoding='utf-8') as f:
                export_file = csv.DictWriter(f, fieldnames = [
                    'Название',
                    'Остаток',
                    'Бренд',
                    'Описание',
                    'Артикул',
                    'Цена',
                    'Старая цена',
                    'Категория',
                ], delimiter = '|')

                export_file.writeheader()

                all_products = models.Product.objects.all()
                for item in all_products:
                    all_categories = item.cid.all()
                    lst_categories = []
                    for i in all_categories:
                        lst_categories.append(i.name)
                    export_file.writerow({
                        'Название':item.title,
                        'Остаток':item.stock,
                        'Бренд':item.brand,
                        'Описание':item.desc,
                        'Артикул':item.vendor_code,
                        'Цена':item.price,
                        'Старая цена':item.old_price,
                        'Категория':';'.join(lst_categories),
                    })
        elif type_file == 'xlsx':
            workbook = xlsxwriter.Workbook('price.xlsx')
            worksheet = workbook.add_worksheet()
            # Some data we want to write to the worksheet.
            data_for_export = (
                ['Название',
                'Остаток',
                'Бренд',
                'Описание',
                'Артикул',
                'Цена',
                'Старая цена',
                'Категория'],
            )

            row = 0
            col = 0

            all_products = models.Product.objects.all()
            for item in all_products:
                all_categories = item.cid.all()
                lst_categories = []
                for i in all_categories:
                    lst_categories.append(i.name)
                data_for_export = data_for_export + ([
                    item.title,
                    item.stock,
                    item.brand,
                    item.desc,
                    item.vendor_code,
                    item.price,
                    item.old_price,
                    ';'.join(lst_categories),
                ],)

            for nm, st, br, ds, vn, pr, oldpr, cat in (data_for_export):
                worksheet.write(row, col,     nm)
                worksheet.write(row, col + 1, st)
                worksheet.write(row, col + 2, br)
                worksheet.write(row, col + 3, ds)
                worksheet.write(row, col + 4, vn)
                worksheet.write(row, col + 5, pr)
                worksheet.write(row, col + 6, oldpr)
                worksheet.write(row, col + 7, cat)
                row += 1
            workbook.close()


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


class ImportSheet:

    def is_correct_link(link):
        CREDENTIALS_FILE = 'creds.json'
        spreadsheet_id = ''
        re_sheet_id = re.search(r'spreadsheets/d/(.*)/', link)
        if re_sheet_id:
            spreadsheet_id = re_sheet_id.group(1)
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, 
            ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
        try:
            values = service.spreadsheets().values().get(
                spreadsheetId = spreadsheet_id,
                range = 'A1:Z20',
                majorDimension = 'ROWS'
            ).execute()
            return True
        except HttpError:
            return False

    def import_from_gsheets(link, preview = False):
        CREDENTIALS_FILE = 'creds.json'
        spreadsheet_id = ''
        cnt_rows = 10 if preview else 9999
        re_sheet_id = re.search(r'spreadsheets/d/(.*)/', link)
        if re_sheet_id:
            spreadsheet_id = re_sheet_id.group(1)

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, 
            ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

        httpAuth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

        values = service.spreadsheets().values().get(
            spreadsheetId = spreadsheet_id,
            range = f'A1:Z{cnt_rows}',
            majorDimension = 'ROWS'
        ).execute()

        gsheets_values = values.get('values')
        gsheets_values = ImportSheet.preparation_for_import_gsheets(gsheets_values)
        if preview:
            return gsheets_values
        for row in gsheets_values:
            if row[0] and row[1]:
                price = float(row[5])
                old_price = float(row[6])
                stock = int(row[7])
                category_exists = models.Categories.objects.filter(name=row[0]).exists()
                category = models.Categories.objects.get(name = row[0]) if category_exists else models.Categories(name = row[0]).save()
                default_data = {
                    'brand':row[2],
                    'desc' : row[3],
                    'vendor_code' : row[4],
                    'price' : price,
                    'old_price' : old_price,
                    'stock' : stock,
                }
                product_obj, product_new = models.Product.objects.get_or_create(title = row[1], defaults = default_data)
                if product_new:
                    product_obj.cid.add(category)
                else:
                    product_obj.cid.set([category])

                product_obj.brand = row[2]
                product_obj.desc = row[3]
                product_obj.vendor_code = row[4]
                product_obj.price = price
                product_obj.old_price = old_price
                product_obj.stock = stock
                product_obj.save()


    def preparation_for_import_gsheets(data_lst):
        """ дополнить все элементы пустыми значениями, чтобы все списки были равны по длине"""
        count_column = 8
        for i in data_lst:
            while len(i) < count_column:
                i.append('')

        return data_lst

    def generate_preview_to_front(lst):
        html_result = """
            <table class="table">
                <thead class="thead-light">
            <tr>
                <th scope="col">Категория</th>
                <th scope="col">Название</th>
                <th scope="col">Бренд</th>
                <th scope="col">Описание</th>
                <th scope="col">Артикул</th>
                <th scope="col">Цена</th>
                <th scope="col">Старая цена</th>
                <th scope="col">Остаток</th>
            </tr>
            </thead>
            <tbody>"""
        for row in lst:
            html_result += f'<tr>'
            html_result += f'<td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td>'
            html_result += f'<td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td>'
            html_result += f'<td>{row[6]}</td><td>{row[7]}</td></tr>'
        html_result += '</tbody></table>'

        return html_result