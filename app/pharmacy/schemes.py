from marshmallow import Schema, fields


class ClientRegistrationSchema(Schema):
    id = fields.Int(required=False)
    name = fields.Str(required=True)
    phone = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    rating = fields.Int(required=False)


class ClientSchema(Schema):
    phone = fields.Str(required=False)
    email = fields.Str(required=False)
    password = fields.Str(required=True, load_only=True)


class CategoryScheme(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class CategorySchemeTwo(Schema):
    title = fields.Str(required=False)


class MedicineSchema(Schema):
    id = fields.Int(required=False)
    vendor_code = fields.Str(required=True)
    category_title = fields.Str(required=True)
    title = fields.Str(required=True)
    manufacturer = fields.Str(required=True)
    trade_price = fields.Float(required=False)
    price = fields.Float(required=False)
    price_offline = fields.Float(required=False)
    amount = fields.Int(required=True)
    valid_until = fields.Date('%Y/%m/%d', required=False)


class MedicineSetSchema(Schema):
    medicine = fields.Nested(MedicineSchema, many=True)


class OrderFullSchema(Schema):
    id = fields.Int(required=True)
    client = fields.Nested(ClientRegistrationSchema)
    medicine = fields.Nested(MedicineSchema, many=True, required=True)
    order_no = fields.Str(required=True)
    total_price = fields.Float(required=True)
    valid_until = fields.Date('%Y/%m/%d', required=True)
    status = fields.Str(required=True)


class CategoryWithMedicineSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    medicine = fields.Nested(MedicineSchema, many=True, required=True)


class MultipleCategoriesSchema(Schema):
    categories = fields.Nested(CategoryWithMedicineSchema, many=True, required=True)


class MedicineByCategory(Schema):
    category = fields.Nested(CategoryScheme, required=True)
    medicine = fields.Nested(MedicineSchema, many=True, required=True)


class TitleSchema(Schema):
    title = fields.Str(required=False)


class MedicineIdSchema(Schema):
    medicine_id = fields.Int(required=True)
    amount = fields.Int(required=False)


class OrderNoSchema(Schema):
    order_no = fields.Str(required=True)
    promo_rating_score = fields.Int(required=False)


