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
- Returns: An object with a single key, categories, that contains a object of id: date (as datetime) key:value pairs. 
    "dates": {
            "4": "Thu, 31 Dec 2020 00:00:00 GMT",
            "5": "Wed, 30 Dec 2020 00:00:00 GMT"
        }
- Errors:
    - 404 -  if there is no category


GET '/currencies'
- Fetches a list dictionaries of questios in which the keys are names of questions class atributes and the value is the corresponding value of the atribute for a gives question. Fetches also all categories in the same format as GET '/categoires'/
- Request Arguments:  
    -category(int) - optional, None by default -  coresponding to id of category for which we want to get questions
    -page(int) - opitional, 1 by default - page argument for pagination
- Returns: An object with a keys:
    - categories - same as for GET '/categoires'/
    - current_category - name of category for which questions were fatched
        e.g. "current_category": "Science" 
    - questions - list of dictionaries containig question details
        e.g. "questions": [
        {
        "answer": "Maya Angelou", 
        "category": 4, 
        "difficulty": 2, 
        "id": 5, 
        "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
        }, ...]
    - total_questions - number of all questions
        e.g. "total_questions": 19
- Errors:
    - 404 - if the idea of category is incorrect or there is no question in selected category 


DELETE '/questions/<int:question_id>'
- Delete question from the database
- Request Arguments:  question_id (int) - id of the question to be deleted 
- Returns: An object with a keys:
    - deleted - id of question that was deleted 
        e.g. "deleted": 1
    - questions and total_questions - same as in GET '/questions'
- Errors:
    - 404 - if question to be deleted wasn't found in the database


POST '/questions'
- Post new question to the database
- Request Arguments:  json object with question, answer, category and difficulty fildes
- Returns: An object with a keys:
    - question - value of this key is a string containg posted question
        e.g. "question": "How are you?"
- Errors:
    - 422 - if body does not contains requiered data
    - 409 - if question is already in the database


POST '/questions/search'
- Fetches a list dictionaries of questions same as GET '\questions', but only with questions which contains search term
- Request Arguments:  
    -searchTerm(string)  -  
- Returns: Similar object to the one return by GET '\questions' by this one does not contain categories key, and the list of question is restricted to the ones which match search term. 


GET '/categories/<int:category_id>/questions'
- Fetches a list dictionaries of questios for a given category.
- Request Arguments:  
    -category(int) - optional, None by default -  coresponding to id of category for which we want to get questions
    -page(int) - opitional, 1 by default - page argument for pagination
- Returns: An object with a keys:
    - questions - same as GET '/questions'
- Errors:
    - 404 - if category_id does not corespond to any category id in the database 

POST '/play'
- Fetches a random question from a given category.
- Request Arguments:  
    - quiz_category (dict) - optional, None by default -  dictionary with two keys id and type
    -previous_questions(list of int) - by default empyt list - list of question to be exlcude from this request
- Returns: An object with a keys:
    - question - dictionary with question, answer, category and difficulty keys
        e.g. "question":
        {
        "answer": "Maya Angelou", 
        "category": 4, 
        "difficulty": 2, 
        "id": 5, 
        "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
        }
- Errors:
    - 404 - if category_id does not corespond to any category id in the database 
```


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