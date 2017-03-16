

/***** handling submit button ******/

function make_submit_button_handler(forButton) {
    return function (e) {
        var all_containers = jQuery.makeArray($('.container'));
        var dict = {};
        var button = $(forButton);

        // freeze width to current value so the text change doesn't resize the button
        button.css({
              width: button.outerWidth(),
              height: button.outerHeight(),
              padding: 0
        });

        var originalLabel = button.text();
        button.text("Updating ...");
        button.attr("disabled", "disabled");

        for( var i = 0; i < all_containers.length; i++ ) {
          var container = all_containers[i];

          for( var j = 0; j < container.children.length; j++ ) {
            var element = container.children[j];
            dict[element.id] = container.id; // "assignment_" +
          }
        }

        // send asynchronous HTTP request to update data in database
        $.ajax({
            'url': '/room-planner.html',
            'type': 'POST',
            'contentType':'application/json',
            'data': JSON.stringify(dict),
//            'error': function(data) { console.log("error "); console.log(data); },
            'success': function(data) {
                if(data == "success") {
                    set_message("Database updated.", "message");
                    button.text(originalLabel);
                    button.removeAttr("disabled");
                }
            }
        });
    };
}


function set_message(text, htmlClass) {
    $("#message").text(text);
    $("#message").removeClass().addClass(htmlClass);
}



/***** Dragula code *******/

(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

    // NB This script assumes that the variable "people"
    // has been initialized correctly, in another <script> block,
    // before this code is executed.


    function person_for_element(element) {
        return people[element.id];
    }

    function check_containers(containers, people) {
        for(var i = 0; i < containers.length; i++ ) {
            var container = containers[i];
            var size = container.children.length;

            var other_arrival = null;
            var other_departure = null;
            var inconsistent_dates = false;

            for( var j = 0; j < size; j++ ) {
                var el = container.children[j];
                var person = person_for_element(el);

                if( other_arrival == null ) {
                  other_arrival = person.arrival;
                  other_departure = person.departure;
                } else {
                  if( (person.arrival != other_arrival) || (person.departure != other_departure) ) {
                    inconsistent_dates = true;
                  }
                }

                if( person.roomsize < size ) {
                    // too many people in this room
                    el.className = "w-too-many";
                } else if( ! are_partner_desires_met(person, container) ) {
                    // specified partner, but is not in a room with that partner
                    el.className = "w-wrong-partner";
                } else if( size == 1 && person.roomsize > 1 ) {
                    // double-room person alone in a room
                    el.className = "w-not-enough";
                } else if( has_undesired_partner(person, container) ) {
                    // has partner of other gender, and that is not the preferred partner
                    el.className = "w-mixed-gender";
                } else if( ! person.extras_submitted ) {
                    // hasn't submitted extras form
                    el.className = "w-not-submitted";
                } else {
                    el.className = "w-happy";
                }
            }

            if(inconsistent_dates) {
                container.className = "container cw-inconsistent-dates";
            } else {
                container.className = "container";
            }
        }
    }

    // checks if person has another person of the other gender in the same room,
    // except if that other person was specifically desired
    function has_undesired_partner(person, container) {
        for( var j = 0; j < container.children.length; j++ ) {
            var el = container.children[j];
            var other_person = people[el.id];

            if( person.id != other_person.id ) {
                if( other_person.gender && person.gender && (person.gender != other_person.gender) ) {
                    if( ! is_desired_partner(person, other_person) ) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    // returns true if the other_person is a partner that person specifically requested
    function is_desired_partner(person, other_person) {
        if( person.guest_of ) {
            // person is guest
            if( person.partner == 3 ) {
                // guest wants to share with participant, other person is that participant
                return person.guest_of == other_person.id;
            } else if( person.partner == 4 ) {
                // guest wants to share with other guest, other person is a guest
                return other_person.guest_of;
            } else {
                return false;
            }
        } else {
            // person is participant
            if( person.partner == -2 ) {
                // wants to share with guest
                return other_person.guest_of == person.id;  // ok if other_person is my guest
            } else if( person.partner ) {
                // wants to share with specific participant
                return other_person.id == person.partner;
            } else {
                return false;
            }
        }
    }

    // if person specified a partner, checks if that partner is in the same room
    function are_partner_desires_met(person, container) {
        if( !person.partner ) {
            return true;
        } else {
            for(var i = 0; i < container.children.length; i++) {
                if( is_desired_partner(person, person_for_element(container.children[i])) ) {
                    return true;
                }
            }

            return false;
        }
    }

    function prepend_gender(person, str) {
        if(person.gender == "M") {
            return "\u2642 " + str;
        } else if( person.gender == "F") {
            return "\u2640 " + str;
        } else {
            return str;
        }
    }

    var all_containers = jQuery.makeArray($('.container'));

    for (var id in people) {
        var person = people[id];
        var el = document.createElement("div");
        var t = document.createTextNode(person.name);

        if( person.guest_of ) {
          // write guest names in italics
          var t2 = document.createElement("i");
          t2.appendChild(t);
          t = t2;
        }

        el.appendChild(t);

        t = document.createElement("br");
        el.appendChild(t);

        t = document.createElement("span");
        t.className = "datelabel";
        t.appendChild(document.createTextNode(prepend_gender(person, person.arrival + " - " + person.departure)));
        el.appendChild(t);

        el.setAttribute("id", id);

        if( person.tooltip ) {
            el.setAttribute("data-ot", person.tooltip);
            el.setAttribute("data-ot-delay", "1");
        }

        f(people[id].room).appendChild(el);
    }

    check_containers(all_containers, people);


    var crossvent = require('crossvent');

    var drake = dragula(all_containers);

    drake.on("drop", function(el, target, source, sibling) {
        check_containers([target, source], people);
        set_message("Unsaved changes!", "message-old");

        // check whether move made everyone in target container happy
        var target_all_happy = true;
        for( var i = 0; i < target.children.length; i++ ) {
            var el = target.children[i];
            var status = el.getAttribute("class");

            console.log(status);
            if( status != "w-happy" ) {
                target_all_happy = false;
            }
        }

        // play sound depending on that
        if( target_all_happy ) {
            var audio = new Audio('/static/success.mp3');
            audio.play();
        } else {
            var audio = new Audio('/static/plonk.mp3');
            audio.play();
        }
    });

    function f (id) {
      return document.getElementById(id);
    }



},{"crossvent":3}],2:[function(require,module,exports){
(function (global){

var NativeCustomEvent = global.CustomEvent;

function useNative () {
  try {
    var p = new NativeCustomEvent('cat', { detail: { foo: 'bar' } });
    return  'cat' === p.type && 'bar' === p.detail.foo;
  } catch (e) {
  }
  return false;
}

/**
 * Cross-browser `CustomEvent` constructor.
 *
 * https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent.CustomEvent
 *
 */

module.exports = useNative() ? NativeCustomEvent :

// IE >= 9
'function' === typeof document.createEvent ? function CustomEvent (type, params) {
  var e = document.createEvent('CustomEvent');
  if (params) {
    e.initCustomEvent(type, params.bubbles, params.cancelable, params.detail);
  } else {
    e.initCustomEvent(type, false, false, void 0);
  }
  return e;
} :

// IE <= 8
function CustomEvent (type, params) {
  var e = document.createEventObject();
  e.type = type;
  if (params) {
    e.bubbles = Boolean(params.bubbles);
    e.cancelable = Boolean(params.cancelable);
    e.detail = params.detail;
  } else {
    e.bubbles = false;
    e.cancelable = false;
    e.detail = void 0;
  }
  return e;
}

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{}],3:[function(require,module,exports){
(function (global){
'use strict';

var customEvent = require('custom-event');
var eventmap = require('./eventmap');
var doc = global.document;
var addEvent = addEventEasy;
var removeEvent = removeEventEasy;
var hardCache = [];

if (!global.addEventListener) {
  addEvent = addEventHard;
  removeEvent = removeEventHard;
}

module.exports = {
  add: addEvent,
  remove: removeEvent,
  fabricate: fabricateEvent
};

function addEventEasy (el, type, fn, capturing) {
  return el.addEventListener(type, fn, capturing);
}

function addEventHard (el, type, fn) {
  return el.attachEvent('on' + type, wrap(el, type, fn));
}

function removeEventEasy (el, type, fn, capturing) {
  return el.removeEventListener(type, fn, capturing);
}

function removeEventHard (el, type, fn) {
  var listener = unwrap(el, type, fn);
  if (listener) {
    return el.detachEvent('on' + type, listener);
  }
}

function fabricateEvent (el, type, model) {
  var e = eventmap.indexOf(type) === -1 ? makeCustomEvent() : makeClassicEvent();
  if (el.dispatchEvent) {
    el.dispatchEvent(e);
  } else {
    el.fireEvent('on' + type, e);
  }
  function makeClassicEvent () {
    var e;
    if (doc.createEvent) {
      e = doc.createEvent('Event');
      e.initEvent(type, true, true);
    } else if (doc.createEventObject) {
      e = doc.createEventObject();
    }
    return e;
  }
  function makeCustomEvent () {
    return new customEvent(type, { detail: model });
  }
}

function wrapperFactory (el, type, fn) {
  return function wrapper (originalEvent) {
    var e = originalEvent || global.event;
    e.target = e.target || e.srcElement;
    e.preventDefault = e.preventDefault || function preventDefault () { e.returnValue = false; };
    e.stopPropagation = e.stopPropagation || function stopPropagation () { e.cancelBubble = true; };
    e.which = e.which || e.keyCode;
    fn.call(el, e);
  };
}

function wrap (el, type, fn) {
  var wrapper = unwrap(el, type, fn) || wrapperFactory(el, type, fn);
  hardCache.push({
    wrapper: wrapper,
    element: el,
    type: type,
    fn: fn
  });
  return wrapper;
}

function unwrap (el, type, fn) {
  var i = find(el, type, fn);
  if (i) {
    var wrapper = hardCache[i].wrapper;
    hardCache.splice(i, 1); // free up a tad of memory
    return wrapper;
  }
}

function find (el, type, fn) {
  var i, item;
  for (i = 0; i < hardCache.length; i++) {
    item = hardCache[i];
    if (item.element === el && item.type === type && item.fn === fn) {
      return i;
    }
  }
}

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{"./eventmap":4,"custom-event":2}],4:[function(require,module,exports){
(function (global){
'use strict';

var eventmap = [];
var eventname = '';
var ron = /^on/;

for (eventname in global) {
  if (ron.test(eventname)) {
    eventmap.push(eventname.slice(2));
  }
}

module.exports = eventmap;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{}]},{},[1])




