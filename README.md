# Markit API
## About
This API provide more convenient access to Market Interest Rate Curve available at
https://www.markit.com/news/InterestRates_ccy_yyyymmdd.zip
details descripiton of the curve can be found here:
https://www.cdsmodel.com/cdsmodel/assets/cds-model/docs/Interest%20Rate%20Curve%20Specification%20-%20All%20Currencies%20(Updated%20October%202013).pdf 
it is running at markit-api.herokuapp.com
It offer two type of access
- client - can only get data
- quant - apart from getting data can also modify, add and delete curves

#### Dependencies
This project key dependecies are flask, sqlalchemy and postgresql, all dependecies are in requirements.txt.

#### Running localy
To run this localy configure enviroment variables, particularly for postgres db cilent
```bash
pip install -r requirements.txt
python app.py
```
## API
All endpoint returns contains keys success and status_code with boolean and int values respectively  (e.g.   {"status_code": 200, "success": true, ...} )

There are 3 error handlers (404, 409, 422) plus authorization error handlers, all returns json with three key value paris and error code
e.g jsonify({
            "success": False,
            "error": 404,
            "message": "There is no curve with id:2020}"
        }), 404
(the messages are customaized) 

GET '/dates'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns an object that apart from stadard keys contains a single key, categories, that contains a object of id: date (as datetime) key:value pairs. 
    "dates": {
            "4": "Thu, 31 Dec 2020 00:00:00 GMT",
            "5": "Wed, 30 Dec 2020 00:00:00 GMT"
        }
- required permission: get:dates
- Errors:
    - 404 -  if there is no dates


GET '/currencies'
- Fetches a dic of currencies with id currency name key-value pairs.
- Request Arguments:  None
- Returns an object that apart from stadard keys contains a key:
    - currencies
- required permission: get:currency
- Errors:
    - 404 - if there is no currencies


POST '/curves/id'
- Fetches curve id for reuqsted date and currency
- Request Arguments: 
    json object with:
    - date - date str in format yyyymmdd
    - ccy - currecny str in format XXX e.g. USD
- Returns an object that apart from stadard keys contains a key:
    - curve_id - id (int) of a curve for given currency date pair 
- required permission: get:curves
- Errors:
    - 404 - if there is no currency or date
    

 GET '/curves/<int:curve_id>'
- Fetches curve spreads for curve with curve_id 
- Request Arguments:  
    - curve_id - int 
- Returns an object that apart from stadard keys contains a key:
    - curve - dict with two keys curve_id and spreads, value for curve_id is just int curve id and for spread is a dict with tenor sprad key-value pairs.
- required permission: get:curves
- Errors:
    - 404 - if there is no curve with this id


POST '/curves'
- Post new curve to the database
- Request Arguments: 
    json object with:
    - date - date str in format yyyymmdd
    - ccy - currecny str in format XXX e.g. USD
- Returns an object that apart from stadard keys contains a keys:
    - curve - dict with date_id and ccy_id keys, with corresponding values
    - spread - 5y spread of the new curve 
- required permission: post:curves
- Errors:
    - 422 - unable to query 5y spread for posted curve.
    - 409 - curve already exist


PATCH '/curves/<int:curve_id>'
- Override existing curve in db
- Request Arguments:  
    - curve_id
- Returns an object that apart from stadard keys contains a keys:
    - curve - dict with date_id and ccy_id keys, with corresponding values
    - spreads - dict with tenor spreads key value pairs of override tenors
- required permission: pacht:curves
- Errors:
    - 422 - incorrect override, body of the request is incorrect
    - 404 - if there is no curve with this id



DELETE '/curves/<int:curve_id>'
- Delete existing curve in db
- Request Arguments:  
    - curve_id
- Returns an object that apart from stadard keys contains a key:
    - deleted_curve_id - int 
- required permission: delete:curves
- Errors:
   - 404 - if there is no curve with this id

## Testing
To run the tests,
set valid tokens in MarkitTestCase.SetUp:
- self.test_client - to test client access
- self.test_qunat - to test quant access
and run
```
dropdb markit_test
createdb markit_test 
python3 test_app.py
```