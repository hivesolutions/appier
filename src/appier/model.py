#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2012 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Appier Framework. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import copy
import types

import util
import mongo
import observer
import validation
import exceptions

RE = lambda v: [i for i in v if not i == ""]
""" Simple lambda function that removes any
empty element from the provided list value """

BUILDERS = {
    unicode : lambda v: v.decode("utf-8") if\
        type(v) == types.StringType else unicode(v),
    list : lambda v: RE(v) if type(v) == types.ListType else RE([v])
}
""" The map associating the various types with the
custom builder functions to be used when applying
the types function, this is relevant for the built-in
types that are meant to avoid using the default constructor """

TYPE_DEFAULTS = {
    str : None,
    unicode : None,
    int : None,
    float : None,
    list : [],
    dict : {}
}
""" The default values to be set when a type
conversion fails for the provided string value
the resulting value may be returned when a validation
fails an so it must be used carefully """

class Model(observer.Observable):

    def __init__(self, model = None):
        self.__dict__["_events"] = {}
        self.__dict__["_extras"] = []
        self.__dict__["model"] = model or {}
        observer.Observable.__init__(self)

    def __getattribute__(self, name):
        try:
            model = object.__getattribute__(self, "model")
            if name in model: return model[name]
        except AttributeError: pass
        cls = object.__getattribute__(self, "__class__")
        definition = cls.definition()
        if name in definition: raise AttributeError(
            "attribute '%s' is not set" % name
        )
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        is_base = name in self.__dict__
        if is_base: self.__dict__[name] = value
        else: self.model[name] = value

    def __delattr__(self, name):
        try:
            model = object.__getattribute__(self, "model")
            if name in model: del model[name]
        except AttributeError: pass

    @classmethod
    def new(cls, model = None, safe = True, build = False):
        instance = cls()
        instance.apply(model, safe_a = safe)
        build and cls.build(instance.model, map = False)
        return instance

    @classmethod
    def singleton(cls, model = None, safe = True, build = False):
        instance = cls.get(raise_e = False)
        if instance: instance.apply(model, safe_a = safe)
        else: instance = cls.new(model = model, safe = safe, build = build)
        return instance

    @classmethod
    def get(cls, *args, **kwargs):
        map, rules, build, skip, limit, sort, raise_e = cls._get_attrs(kwargs, (
            ("map", False),
            ("rules", True),
            ("build", True),
            ("skip", 0),
            ("limit", 0),
            ("sort", None),
            ("raise_e", True)
        ))

        collection = cls._collection()
        model = collection.find_one(
            kwargs, skip = skip, limit = limit, sort = sort
        )
        if not model and raise_e: raise RuntimeError("%s not found" % cls.__name__)
        if not model and not raise_e: return model
        cls.types(model)
        cls.fill(model)
        build and cls.build(model, map = map, rules = rules)
        return model if map else cls.new(model = model, safe = False)

    @classmethod
    def find(cls, *args, **kwargs):
        map, rules, build, skip, limit, sort = cls._get_attrs(kwargs, (
            ("map", False),
            ("rules", True),
            ("build", True),
            ("skip", 0),
            ("limit", 0),
            ("sort", None)
        ))

        cls._find_s(kwargs)

        collection = cls._collection()
        models = [cls.fill(cls.types(model)) for model in collection.find(
            kwargs, skip = skip, limit = limit, sort = sort
        )]
        build and [cls.build(model, map = map, rules = rules) for model in models]
        models = models if map else [cls.new(model = model, safe = False) for model in models]
        return models

    @classmethod
    def count(cls, *args, **kwargs):
        collection = cls._collection()
        if kwargs:
            result = collection.find(kwargs)
            result = result.count()
        else:
            result = collection.count()
        return result

    @classmethod
    def delete_c(cls, *args, **kwargs):
        collection = cls._collection()
        collection.remove(kwargs)

    @classmethod
    def definition(cls):
        # in case the definition are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_definition" in cls.__dict__: return cls._definition

        # creates the map that will hold the complete definition of
        # the current model
        definition = {}

        # retrieves the complete model hierarchy for the current model
        # this should allow the method to retrieve the complete set
        # of fields for the current model
        hierarchy = cls.hierarchy()

        # iterates over all the classes in the hierarchy to creates the
        # map that will contain the various names of the current model
        # associated with its definition map
        for _cls in hierarchy:
            for name, value in _cls.__dict__.iteritems():
                if name.startswith("_"): continue
                if not type(value) == types.DictionaryType: continue
                definition[name] = value

        # sets the "default" definition for the based identifier
        # (underlying identifier attribute)
        definition["_id"] = dict()

        # saves the currently generated definition under the current
        # class and then returns the contents of it to the caller method
        cls._definition = definition
        return definition

    @classmethod
    def definition_n(cls, name):
        definition = cls.definition()
        return definition.get(name, {})

    @classmethod
    def setup(cls):
        indexes = cls.indexes()
        collection = cls._collection()
        for index in indexes: collection.ensure_index(index)

    @classmethod
    def validate(cls):
        return []

    @classmethod
    def validate_new(cls):
        return cls.validate()

    @classmethod
    def build(cls, model, map = False, rules = True):
        if rules: cls.rules(model, map)
        cls._build(model, map)

    @classmethod
    def rules(cls, model, map):
        for name, _value in model.items():
            definition = cls.definition_n(name)
            is_private = definition.get("private", False)
            if not is_private: continue
            del model[name]

    @classmethod
    def types(cls, model):
        definition = cls.definition()

        for name, value in model.iteritems():
            if name == "_id": continue
            if value == None: continue
            if not name in definition: continue
            _definition = cls.definition_n(name)
            _type = _definition.get("type", unicode)
            builder = BUILDERS.get(_type, _type)
            try:
                model[name] = builder(value) if builder else value
            except:
                default = TYPE_DEFAULTS.get(_type, None)
                default = _type._default() if hasattr(_type, "_default") else default
                model[name] = default

        return model

    @classmethod
    def fill(cls, model):
        """
        Fills the current models with the proper values so that
        no values are unset as this would violate the model definition
        integrity. This is required when retrieving an object(s) from
        the data source (as some of them may be incomplete).

        @type model: Model
        @param model: The model that is going to have its unset
        attributes filled with "default" data.
        """

        definition = cls.definition()
        for name, _definition in definition.iteritems():
            if name in model: continue
            _type = _definition.get("type")
            default = TYPE_DEFAULTS.get(_type, None)
            default = _type._default() if hasattr(_type, "_default") else default
            model[name] = default

        return model

    @classmethod
    def all_parents(cls):
        # in case the all parents are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_all_parents" in cls.__dict__: return cls._all_parents

        # creates the list to hold the various parent
        # entity classes, populated recursively
        all_parents = []

        # retrieves the parent entity classes from
        # the current class
        parents = cls._bases()

        # iterates over all the parents to extend
        # the all parents list with the parent entities
        # from the parent
        for parent in parents:
            # retrieves the (all) parents from the parents
            # and extends the all parents list with them,
            # this extension method avoids duplicates
            _parents = parent.all_parents()
            all_parents += _parents

        # extends the all parents list with the parents
        # from the current entity class (avoids duplicates)
        all_parents += parents

        # caches the all parents element in the class
        # to provide fast access in latter access
        cls._all_parents = all_parents

        # returns the list that contains all the parents
        # entity classes
        return all_parents

    @classmethod
    def hierarchy(cls):
        # in case the hierarchy are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_hierarchy" in cls.__dict__: return cls._hierarchy

        # retrieves the complete set of parents for the current class
        # and then adds the current class to it
        all_parents = cls.all_parents()
        hierarchy = all_parents + [cls]

        # saves the current hierarchy list under the class and then
        # returns the sequence to the caller method
        cls._hierarchy = hierarchy
        return hierarchy

    @classmethod
    def increments(cls):
        # in case the increments are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_increments" in cls.__dict__: return cls._increments

        # creates the list that will hold the various names that are
        # meant to be automatically incremented
        increments = []

        # retrieves the map containing the definition of the class with
        # the name of the fields associated with their definition
        definition = cls.definition()

        # iterate over all the names in the definition to retrieve their
        # definition and check if their are of type increment
        for name in definition:
            _definition = cls.definition_n(name)
            is_increment = _definition.get("increment", False)
            if not is_increment: continue
            increments.append(name)

        # saves the increment list under the class and then
        # returns the sequence to the caller method
        cls._increments = increments
        return increments

    @classmethod
    def indexes(cls):
        # in case the indexes are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_indexes" in cls.__dict__: return cls._indexes

        # creates the list that will hold the various names that are
        # meant to be indexed in the data source
        indexes = []

        # retrieves the map containing the definition of the class with
        # the name of the fields associated with their definition
        definition = cls.definition()

        # iterate over all the names in the definition to retrieve their
        # definition and check if their are of type index
        for name in definition:
            _definition = cls.definition_n(name)
            is_index = _definition.get("index", False)
            if not is_index: continue
            indexes.append(name)

        # saves the index list under the class and then
        # returns the sequence to the caller method
        cls._indexes = indexes
        return indexes

    @classmethod
    def safes(cls):
        # in case the safes are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_safes" in cls.__dict__: return cls._safes

        # creates the list that will hold the various names that are
        # meant to be safe values in the data source
        safes = []

        # retrieves the map containing the definition of the class with
        # the name of the fields associated with their definition
        definition = cls.definition()

        # iterate over all the names in the definition to retrieve their
        # definition and check if their are of type safe
        for name in definition:
            _definition = cls.definition_n(name)
            is_safe = _definition.get("safe", False)
            if not is_safe: continue
            safes.append(name)

        # saves the safes list under the class and then
        # returns the sequence to the caller method
        cls._safes = safes
        return safes

    @classmethod
    def immutables(cls):
        # in case the immutables are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_immutables" in cls.__dict__: return cls._immutables

        # creates the list that will hold the various names that are
        # meant to be immutable values in the data source
        immutables = []

        # retrieves the map containing the definition of the class with
        # the name of the fields associated with their definition
        definition = cls.definition()

        # iterate over all the names in the definition to retrieve their
        # definition and check if their are of type immutable
        for name in definition:
            _definition = cls.definition_n(name)
            is_immutable = _definition.get("immutable", False)
            if not is_immutable: continue
            immutables.append(name)

        # saves the immutables list under the class and then
        # returns the sequence to the caller method
        cls._immutables = immutables
        return immutables

    @classmethod
    def default(cls):
        # in case the default are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_default" in cls.__dict__: return cls._default

        # retrieves the complete hierarchy of the model to be used
        # for the retrieval of the lowest possible default value for
        # the current class hierarchy
        hierarchy = cls.hierarchy()

        # creates the value that is going to store the default value for
        # the current class (in case there's one)
        default = None

        # iterates over all the classes in the current hierarchy, note
        # that the iteration is done from the leaf nodes to the root nodes
        # so that the lowest possible default value is found
        for _cls in reversed(hierarchy):
            for name in _cls.__dict__.keys():
                # retrieves the definition map for the current name an in
                # case the default value is set considers it default otherwise
                # continues the loop, nothing to be done
                _definition = cls.definition_n(name)
                is_default = _definition.get("default", False)
                if not is_default: continue

                # in case the default value is found sets its name in the
                # current default value and then breaks the loop
                default = name
                break

            # in case the default value has been found must break the external
            # loop as nothing else remains to be found
            if default: break

        # saves the default value (name) under the class and then
        # returns the sequence to the caller method
        cls._default = default
        return default

    @classmethod
    def filter_merge(cls, name, filter, kwargs):
        # retrieves a possible previous filter defined for the
        # provided name in case it does exists must concatenate
        # that previous value in an and statement
        filter_p = kwargs.get(name, None)
        if filter_p:
            # retrieves the and references for the current arguments
            # and appends the two filter values (current and previous)
            # then deletes the current name reference in the arguments
            # and updates the name value to the and value
            filter_a = kwargs.get("$and", [])
            filter = filter_a + [{name : filter}, {name : filter_p}]
            del kwargs[name]
            name = "$and"

        # sets the currently defined filter structures in the keyword
        # based arguments map for the currently defined name
        kwargs[name] = filter

    @classmethod
    def _build(cls, model, map):
        pass

    @classmethod
    def _collection(cls):
        name = cls._name()
        db = mongo.get_db()
        collection = db[name]
        return collection

    @classmethod
    def _name(cls):
        # retrieves the class object for the current instance and then
        # converts it into lower case value in order to serve as the
        # name of the collection to be used
        name = cls.__name__.lower()
        return name

    @classmethod
    def _get_attrs(cls, kwargs, attrs):
        _attrs = []

        for attr, value in attrs:
            if not attr in kwargs:
                _attrs.append(value)
                continue

            value = kwargs[attr]
            del kwargs[attr]
            _attrs.append(value)

        return _attrs

    @classmethod
    def _find_s(cls, kwargs):
        # in case the find string is currently not defined in the
        # named arguments map returns immediately as nothing is
        # meant to be done on this method
        if not "find_s" in kwargs: return

        # retrieves the find string into a local variable, then
        # removes the find string from the named arguments map
        # so that it's not going to be erroneously used by the
        # underlying find infra-structure
        find_s = kwargs["find_s"]
        del kwargs["find_s"]

        # retrieves the "name" of the attribute that is considered
        # to be the default (representation) for the model in case
        # there's none returns immediately, as it's not possible
        # to proceed with the filter creation
        default = cls.default()
        if not default: return

        # retrieves the definition for the default attribute and uses
        # it to retrieve it's target data type, defaulting to the
        # string type in case none is defined in the schema
        definition = cls.definition_n(default)
        default_t = definition.get("type", unicode)

        try:
            # in case the target date type for the default field is
            # string the right labeled wildcard regex is used for the
            # search otherwise the search value to be used is the exact
            # match of the value (required type conversion)
            if default_t in (str, unicode): find_v = {"$regex" : find_s + ".*"}
            else: find_v = default_t(find_s)
        except:
            # in case there's an error in the conversion for
            # the target type value sets the search value as
            # invalid (not going to be used in filter)
            find_v = None

        # in case there's a valid find value to be used sets
        # the value in the named arguments map to be used by
        # the underlying find infra-structure, note that the
        # set is done using a "merge" with the previous values
        if not find_v == None:
            cls.filter_merge(default, find_v, kwargs)

    @classmethod
    def _bases(cls):
        """
        Retrieves the complete set of base (parent) classes for
        the current class, this method is safe as it removes any
        class that does not inherit from the entity class.

        Please note that this function only retrieves the set of
        direct parents of the class and not the complete hierarchy.

        @rtype: List/Tuple
        @return: The set containing the various bases classes for
        the current class that are considered valid.
        """

        # retrieves the complete set of base classes for
        # the current class and in case the observable is
        # not the bases set returns the set immediately
        bases = cls.__bases__
        if not observer.Observable in bases: return bases

        # converts the base classes into a list and removes
        # the observable class from it, then returns the
        # new bases list/tuple (without the object class)
        bases = list(bases)
        bases.remove(observer.Observable)
        return tuple(bases)

    @classmethod
    def _increment(cls, name):
        _name = cls._name() + ":" + name
        db = mongo.get_db()
        value = db.counters.find_and_modify(
            query = {
                "_id" : _name
            },
            update = {
                "$inc" : {
                    "seq" : 1
                }
            },
            new = True,
            upsert = True
        )
        value = value or db.counters.find_one({
            "_id" : _name
        })
        return value["seq"]

    def val(self, name, default = None):
        return self.model.get(name, default)

    def build_m(self, model = None, rules = True):
        """
        Builds the currently defined model, this should run
        additional computation for the current model creating
        new (calculated) attributes and deleting other.

        The extra rules parameters allows for the (security) rules
        to be applied to the model, used this with care to avoid
        any security problems.

        This method should me used carefully to avoid validation
        problems and other side effects.

        @type model: Map
        @param model: The model map to be used for the build
        operation in case none is specified the currently set
        model is used instead.
        @type rules: bool
        @param rules: If the (security) rules should be applied to
        the model that is going to be built.
        """

        cls = self.__class__
        model = model or self.model
        cls.build(model, rules = rules)

    def apply(self, model = None, safe = None, safe_a = True):
        # calls the complete set of event handlers for the current
        # apply operation, this should trigger changes in the model
        self.pre_apply()

        # retrieves the reference to the class associated
        # with the current instance
        cls = self.__class__

        # creates the base safe map from the provided map or
        # builds a new map that will hold these values
        safe = safe or {}

        # verifies if the base safe rules should be applied
        # to the current map of safe attributes
        if safe_a:
            safes = cls.safes()
            for _safe in safes:
                safe[_safe] = True

        # retrieves the object loading it from all the available
        # sources and then iterates over all the of the model
        # values setting the values in the current intance's model
        # then runs the type casting/conversion operation in it
        model = model or util.get_object()
        for name, value in model.iteritems():
            is_safe = safe.get(name, False)
            if is_safe: continue
            self.model[name] = value
        cls = self.__class__
        cls.types(self.model)

        # calls the complete set of event handlers for the current
        # apply operation, this should trigger changes in the model
        self.post_apply()

    def copy(self, build = False, rules = True):
        cls = self.__class__
        _copy = copy.deepcopy(self)
        build and cls.build(_copy.model, map = False, rules = rules)
        return _copy

    def validate_extra(self, name):
        """
        Adds a new validate method to the current set of
        validate methods to be executed on the next validation
        execution. Note this validate method will only be used
        on the next validation execution, after that execution
        it will be removed from the extras validations list.

        @type name: String
        @param name: The name of the validation method that should
        be added to the extras list, note that the real name of
        the method should be prefixed with the "validate" prefix
        """

        cls = self.__class__
        method = getattr(cls, "validate_" + name)
        self._extras.append(method)

    def is_new(self):
        return not "_id" in self.model

    def save(self, validate = True):
        # checks if the instance to be saved is a new instance
        # or if this is an update operation
        is_new = self.is_new()

        # runs the validation process in the current model, this
        # should ensure that the model is ready to be saved in the
        # data source, without corruption of it, only run this process
        # in case the validate flag is correctly set
        validate and self._validate()

        # calls the complete set of event handlers for the current
        # save operation, this should trigger changes in the model
        self.pre_save()
        is_new and self.pre_create()
        not is_new and self.pre_update()

        # filters the values that are present in the current model
        # so that only the valid ones are stored in, invalid values
        # are going to be removed, note that if the operation is an
        # update operation the "immutable rules" also apply, the
        # returned value is normalizes meaning that for instance if
        # any relation is loaded the reference value is returned instead
        # of the loaded relation values (required for persistence)
        model = self._filter(immutables_a = not is_new, normalize = True)

        # in case the current model is not new must create a new
        # model instance and remove the main identifier from it
        if not is_new: _model = copy.copy(model); del _model["_id"]

        # retrieves the reference to the store object to be used and
        # uses it to store the current model data
        store = self._get_store()
        if is_new: self._id = store.insert(model); self.apply(model)
        else: store.update({"_id" : model["_id"]}, {"$set" : _model})

        # calls the post save event handlers in order to be able to
        # execute appropriate post operations
        self.post_save()
        is_new and self.post_create()
        not is_new and self.post_update()

    def delete(self):
        # calls the complete set of event handlers for the current
        # delete operation, this should trigger changes in the model
        self.pre_delete()

        # retrieves the reference to the store object to be able to
        # execute the removal command for the current model
        store = self._get_store()
        store.remove({"_id" : self._id})

        # calls the underlying delete handler that may be used to extend
        # the default delete functionality
        self._delete()

        # calls the complete set of event handlers for the current
        # delete operation, this should trigger changes in the model
        self.post_delete()

    def reload(self):
        is_new = self.is_new()
        if is_new: raise RuntimeError("Can't reload a new model entity")
        cls = self.__class__
        return cls.get(_id = self._id)

    def map(self):
        model = self._filter()
        return model

    def dumps(self):
        return mongo.dumps(self.model)

    def pre_validate(self):
        self.trigger("pre_validate")

    def pre_save(self):
        self.trigger("pre_save")

    def pre_create(self):
        self.trigger("pre_create")

    def pre_update(self):
        self.trigger("pre_update")

    def pre_delete(self):
        self.trigger("pre_delete")

    def post_validate(self):
        self.trigger("post_validate")

    def post_save(self):
        self.trigger("post_save")

    def post_create(self):
        self.trigger("post_create")

    def post_update(self):
        self.trigger("post_update")

    def post_delete(self):
        self.trigger("post_delete")

    def pre_apply(self):
        self.trigger("pre_apply")

    def post_apply(self):
        self.trigger("post_apply")

    def _get_store(self):
        return self.__class__._collection()

    def _delete(self):
        pass

    def _validate(self, model = None):
        # calls the event handler for the validation process this
        # should setup the operations for a correct validation
        self.pre_validate()

        # starts the model reference with the current model in
        # case none is defined
        model = model or self.model

        # retrieves the class associated with the current instance
        # to be able to retrieve the correct validate methods
        cls = self.__class__

        # checks if the current model is new (create operation)
        # and sets the proper validation methods retrieval method
        is_new = self.is_new()
        if is_new: method = cls.validate_new
        else: method = cls.validate

        # runs the validation process on the various arguments
        # provided to the account and in case an error is returned
        # raises a validation error to the upper layers
        errors, object = validation.validate(
            method,
            object = model,
            ctx = self,
            build = False
        )

        # iterates over the complete set of extra validate method
        # and runs their validations for the current model context
        # adding their errors to the existing map (appending) this
        # will make sure that these extra validation remains transparent
        # from an end-user point of view (as expected)
        for extra in self._extras:
            _errors, _object = validation.validate(
                extra,
                object = model,
                ctx = self,
                build = False
            )
            for key, value in _errors.iteritems():
                errors_l = errors.get(key, [])
                _errors_l = value
                errors_l.extend(_errors_l)
                errors[key] = errors_l

        # empties the extras list so that the methods that have been
        # set there are not going to be used in any further validation
        del self._extras[:]

        # in case the errors map is not empty or invalid there are
        # errors and they should be encapsulated around a validation
        # error and raises to the top layer for handling
        if errors: raise exceptions.ValidationError(errors, object)

        # calls the event handler for the validation process this
        # should finish the operations from a correct validation
        self.post_validate()

    def _filter(self, immutables_a = False, normalize = False):
        # creates the model that will hold the "filtered" model
        # with all the items that conform with the class specification
        model = {}

        # retrieves the class associated with the current instance
        # to be able to retrieve the correct definition methods
        cls = self.__class__

        # retrieves the (schema) definition for the current model
        # to be "filtered" it's going to be used to retrieve the
        # various definitions for the model fields
        definition = cls.definition()

        # retrieves the complete list of fields that are meant to be
        # automatically incremented for every save operation
        increments = cls.increments()

        # gather the set of elements that are considered immutables and
        # that are not meant to be changed if the current operation to
        # apply the filter is not a new operation (update operation)
        immutables = cls.immutables()

        # iterates over all the increment fields and increments their
        # fields so that a new value is set on the model
        for name in increments: model[name] = cls._increment(name)

        # iterates over all the model items to filter the ones
        # that are not valid for the current class context
        for name, value in self.model.iteritems():
            if not name in definition: continue
            if immutables_a and name in immutables: continue
            value = self._evaluate(name, value)
            model[name] = value

        # in case the normalize flag is set must iterate over all
        # items to try to normalize the values by calling the reference
        # value this will returns the reference index value instead of
        # the normal value that would prevent normalization
        if normalize:
            for name, value in self.model.iteritems():
                if not name in definition: continue
                if not hasattr(value, "ref_v"): continue
                model[name] = value.ref_v()

        # returns the model containing the "filtered" items resulting
        # from the validation of the items against the model class
        return model

    def _evaluate(self, name, value):
        # verifies if the current value as an iterable one in case
        # it is runs the evaluate method for each of the values to
        # try to resolve them into the proper representation
        is_iterable = hasattr(value, "__iter__")
        if is_iterable: return [self._evaluate(name, value) for value in value]

        # verifies the current value's class is sub class of the model
        # class and in case it's extracts the relation name from the
        # value and sets it as the value in iteration
        is_model = issubclass(value.__class__, Model)
        if is_model:
            meta = getattr(self.__class__, name)
            _type = meta.get("type", str)
            _name = _type._name
            value = getattr(value, _name)

        # iterates over all the values and retrieves the json value for
        # each of them in case the value contains a json value retrieval
        # method otherwise uses the normal value returning it to the caller
        value = value.json_v() if hasattr(value, "json_v") else value
        return value
