from flakon import JsonBlueprint
from flask import request, jsonify, abort
from myservice.classes.poll import Poll, NonExistingOptionException, UserAlreadyVotedException

doodles = JsonBlueprint('doodles', __name__)

_ACTIVEPOLLS = {} # list of created polls
_POLLNUMBER = 0 # index of the last created poll

@doodles.route('/doodles', methods=['GET','POST']) #TODO: complete the decoration
def all_polls():

    if request.method == 'POST':
        result = create_doodle(request)

    elif request.method == 'GET':
        result = get_all_doodles(request)
    
    return result

@doodles.route('/doodles/<id>', methods=['GET', 'PUT', 'DELETE']) #TODO: complete the decoration
def single_poll(id):
    global _ACTIVEPOLLS
    
    id2 = int(id)

    result = ""

    exist_poll(id2) # check if the Doodle is an existing one
    
    if request.method == 'GET': # retrieve a poll
        result = jsonify(_ACTIVEPOLLS[id2].serialize())
      
        return(result)

    elif request.method == 'DELETE': 
        #TODO: delete a poll and get back winners
        result = jsonify({'winners' : _ACTIVEPOLLS[id2].get_winners()})
        _ACTIVEPOLLS.pop(id2)
        return result

    elif request.method == 'PUT': 
        #TODO: vote in a poll
        
        result = jsonify({'winners' : vote(id2, request)})
        return result

@doodles.route('/doodles/<id>/<person>', methods=['GET', 'DELETE']) #TODO: complete the decoration
def person_poll(id, person):
    
    #TODO: check if the Doodle exists
    id2 = int(id)
    exist_poll(id2)
    if request.method == 'GET':
        #TODO: retrieve all preferences cast from <person> in poll <id>
        doodl = _ACTIVEPOLLS[id2]
        result = jsonify({'votedoptions' : doodl.get_voted_options(person)})
    if request.method == 'DELETE':
        #TODO: delete all preferences cast from <person> in poll <id>
        doodl = _ACTIVEPOLLS[id2]
        result = jsonify({'removed' : doodl.delete_voted_options(person)})

    return result
       

def vote(id, request):
    result = ""
    #TO DO: extract person and option fields from the JSON request
    json_data = request.get_json()
    persona = json_data['person']
    opzione = json_data['option'] 
    try:
        result = _ACTIVEPOLLS[id].vote(persona, opzione)# TODO: cast a vote from person in  _ACTIVEPOLLS[id]
    except UserAlreadyVotedException:
        abort(400) # Bad Request
    except NonExistingOptionException:
        abort(400)# TODO: manage the NonExistingOptionException

    return result


def create_doodle(request):
    global _ACTIVEPOLLS, _POLLNUMBER
    #TODO: create a new poll in _ACTIVEPOLLS based on the input JSON. Update _POLLNUMBER by incrementing it.
     
    _POLLNUMBER += 1
    json_data = request.get_json()
    title = json_data['title']
    options = json_data['options']
    newdoodle = Poll(_POLLNUMBER, title, options)
    _ACTIVEPOLLS[_POLLNUMBER] = newdoodle
    return jsonify({'pollnumber': _POLLNUMBER})


def get_all_doodles(request):
    global _ACTIVEPOLLS
    return jsonify(activepolls = [e.serialize() for e in _ACTIVEPOLLS.values()])

def exist_poll(id):
    
    if int(id) > _POLLNUMBER:
        abort(404) # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(id in _ACTIVEPOLLS):
        abort(410) # error 410: Gone, i.e. it existed but it's not there anymore