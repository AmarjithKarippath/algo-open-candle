import pymongo

url = "mongodb+srv://amarjithsudhakar:rOeaIFH1MbeMwg6d@cluster0.b2kvbro.mongodb.net/"
client = pymongo.MongoClient(url)
db = client.test

print(db.my_collection)
print(db.my_collection.insert_one({"x": 10}).inserted_id)


trade_symbol = "NIFTY"
QTY = 100
order_p = 120
SL = 5
PT = 10
data = {
    "symbol": trade_symbol,
    "qty": QTY,
    "side": 1,
    "type": 1,
    "productType": "BO",
    "limitPrice": round(order_p),
    "stopPrice": 0,
    "disclosedQty": 0,
    "validity": "DAY",
    "offlineOrder": "False",
    "stopLoss": SL,
    "takeProfit": PT
}
var = db.my_collection.insert_one(data).inserted_id

print(var)