from marshmallow import Schema, fields
from app.pharmacy.schemes import CategoryScheme, MedicineSchema, OrderNoSchema



class AdminSchema(Schema):
    id = fields.Int(required=False)
    login = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


#class OrderNoQuery(Schema):
#    order_no = fields.Str(required=True)


# class CategoryScheme(Schema):
#     id = fields.Int(required=False)
#     title = fields.Str(required=True)


class CategorySetScheme(Schema):
    categories = fields.Nested(CategoryScheme, many=True, required=True)


# class MedicineSchema(Schema):
#     id = fields.Int(required=False)
#     vendor_code = fields.Int(required=True)
#     category_title = fields.Str(required=True)
#     title = fields.Str(required=True)
#     manufacturer = fields.Str(required=True)
#     trade_price = fields.Float(required=False)
#     price = fields.Float(required=False)
#     price_offline = fields.Float(required=False)
#     amount = fields.Int(required=True)
#     valid_until = fields.Date('%Y/%m/%d')


class MedicineSetSchema(Schema):
    medicine = fields.Nested(MedicineSchema, many=True, required=False)


class ClientSchema(Schema):
    id = fields.Int(required=False)
    name = fields.Str(required=True)
    rating: fields.Int(required=True)
    phone: fields.Str(required=True)
    email: fields.Str(required=True)


class RevenueSchema(Schema):
    order_no = fields.Str(required=False)
    sum = fields.Float(required=True)


