#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import re
import copy
import math
import json
import types
import logging
import datetime

from . import meta
from . import util
from . import mongo
from . import legacy
from . import common
from . import typesf
from . import observer
from . import validation
from . import exceptions

ITERABLES = list(legacy.STRINGS) + [dict]
""" The sequence defining the complete set of valid types
for direct evaluation, instead of indirect (recursive)
evaluation, this is required to avoid miss behavior """

RE = lambda v: [i for i in v if not i == ""]
""" Simple lambda function that removes any
empty element from the provided list value """

BUILDERS = {
    legacy.UNICODE : lambda v: v.decode("utf-8") if\
        type(v) == legacy.BYTES else legacy.UNICODE(v),
    list : lambda v: RE(v) if type(v) == list else RE([v]),
    dict : lambda v: json.loads(v) if type(v) == legacy.UNICODE else dict(v),
    bool : lambda v: v if type(v) == bool else\
        not v in ("", "0", "false", "False")
}
""" The map associating the various types with the
custom builder functions to be used when applying
the types function, this is relevant for the built-in
types that are meant to avoid using the default constructor """

METAS = dict(
    text = lambda v, d: v,
    enum = lambda v, d: d["enum"].get(v, None),
    date = lambda v, d: datetime.datetime.utcfromtimestamp(float(v)).strftime("%d %b %Y"),
    datetime = lambda v, d: datetime.datetime.utcfromtimestamp(float(v)).strftime("%d %b %Y %H:%M:%S")
)
""" The map that contains the various mapping functions
for the meta types that may be described for a field under
the current model specification, the resulting value for
each of these functions should preferably be a string """

TYPE_DEFAULTS = {
    legacy.BYTES : None,
    legacy.UNICODE : None,
    int : None,
    float : None,
    bool : False,
    list : [],
    dict : {}
}
""" The default values to be set when a type
conversion fails for the provided string value
the resulting value may be returned when a validation
fails an so it must be used carefully """

TYPE_META = {
    typesf.File : "file",
    typesf.Files : "files",
    typesf.Reference : "reference",
    typesf.References : "references",
    legacy.BYTES : "string",
    legacy.UNICODE : "string",
    int : "number",
    float : "float",
    bool: "bool",
    list : "list",
    dict : "map"
}
""" Dictionary that defines the default mapping for each
of the base data types against the associated default meta
values for each for them, these meta type values are going
to be used mostly for presentation purposes """

TYPE_REFERENCES = (
    typesf.Reference,
    typesf.References
)
""" The various data types that are considered to be references
so that they are lazy loaded from the data source, these kind
of types should be compliant to a common interface so that they
may be used "blindly" from an external entity """

REVERSE = dict(
    descending = "ascending",
    ascending = "descending",
)
""" The reverse order dictionary that maps a certain
order direction (as a string) with the opposite one
this may be used to "calculate" the reverse value """

DIRTY_PARAMS = (
    "map",
    "rules",
    "meta",
    "build",
    "skip",
    "limit",
    "sort",
    "raise_e"
)
""" The set containing the complete set of parameter names for
the parameters that are considered to be dirty and that should
be cleaned from any query operation on the data source, otherwise
serious consequences may occur """

OPERATORS = {
    "equals" : None,
    "not_equals" : "$ne",
    "in" : "$in",
    "not_in" : "$nin",
    "like" : "$regex",
    "likei" : "$regex",
    "llike" : "$regex",
    "llikei" : "$regex",
    "rlike" : "$regex",
    "rlikei" : "$regex",
    "greater" : "$gt",
    "greater_equal" : "$gte",
    "lesser" : "$lt",
    "lesser_equal" : "$lte",
    "is_null" : None,
    "is_not_null" : "$ne",
    "contains" : "$all"
}
""" The map containing the mapping association between the
normalized version of the operators and the infra-structure
specific value for each of this operations, note that some
of the values don't have a valid mapping for this operations
the operator must be ignored and not used explicitly """

VALUE_METHODS = {
    "in" : lambda v, t: [t(v) for v in v.split(";")],
    "not_in" : lambda v, t: [t(v) for v in v.split(";")],
    "like" : lambda v, t: "^.*" + legacy.UNICODE(re.escape(v)) + ".*$",
    "likei" : lambda v, t: "^.*" + legacy.UNICODE(re.escape(v)) + ".*$",
    "llike" : lambda v, t: "^.*" + legacy.UNICODE(re.escape(v)) + "$",
    "llikei" : lambda v, t: "^.*" + legacy.UNICODE(re.escape(v)) + "$",
    "rlike" : lambda v, t: "^" + legacy.UNICODE(re.escape(v)) + ".*$",
    "rlikei" : lambda v, t: "^" + legacy.UNICODE(re.escape(v)) + ".*$",
    "is_null" : lambda v, t: None,
    "is_not_null" : lambda v, t: None,
    "contains" : lambda v, t: [v for v in v.split(";")]
}
""" Map that associates each of the normalized operations with
an inline function that together with the data type maps the
the base string based value into the target normalized value """

INSENSITIVE = {
    "likei" : True,
    "llikei" : True,
    "rlikei" : True,
}
""" The map that associates the various operators with the boolean
values that define if an insensitive base search should be used
instead of the "typical" sensitive search """

class Model(legacy.with_meta(meta.Ordered, observer.Observable)):
    """
    Abstract model class from which all the models should
    directly or indirectly inherit. Should provide the
    basic infra-structure for the persistence of data using
    a play key value storage engine.

    The data should always be store in a dictionary oriented
    structure while it's not persisted in the database.
    """

    def __new__(cls, *args, **kwargs):
        instance = super(Model, cls).__new__(cls)
        instance.__dict__["_events"] = {}
        instance.__dict__["_extras"] = []
        instance.__dict__["model"] = {}
        instance.__dict__["owner"] = None
        return instance

    def __init__(self, model = None, **kwargs):
        self.__dict__["model"] = model or {}
        self.__dict__["owner"] = common.base().APP or None
        for name, value in kwargs.items(): setattr(self, name, value)
        observer.Observable.__init__(self)

    def __str__(self):
        cls = self.__class__
        default = cls.default()
        if not default: return cls._name()
        value = self.model[default]
        is_string = legacy.is_str(value)
        return value if is_string else str(value)

    def __unicode__(self):
        cls = self.__class__
        default = cls.default()
        if not default: return cls._name()
        value = self.model[default]
        is_unicode = legacy.is_unicode(value)
        return value if is_unicode else legacy.UNICODE(value)

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

    def __len__(self):
        return self.model.__len__()

    def __getitem__(self, key):
        return self.model.__getitem__(key)

    def __setitem__(self, key, value):
        self.model.__setitem__(key, value)

    def __delitem__(self, key):
        self.model.__delitem__(key)

    def __contains__(self, item):
        return self.model.__contains__(item)

    def __nonzero__(self):
        return len(self.model) > 0

    def __bool__(self):
        return len(self.model) > 0

    @classmethod
    def new(
        cls,
        model = None,
        form = True,
        safe = True,
        build = False,
        fill = True,
        new = True
    ):
        """
        Creates a new instance of the model applying the provided model
        map to it after the instantiation of the class.

        The optional form flag controls if the form context data should be
        used in the case of an invalid/unset model value. This is considered
        unsafe in many contexts.

        The optional safe flag makes sure that the model attributes marked
        as safe are going to be removed and are not valid for apply.

        The optional build flag may be used to define if the build operations
        that may be defined by the user on override should be called for
        this instance of entity (should be used only on retrieval).

        The optional fill flag allows control on whenever the model should be
        filled with default values before the apply operation is performed.

        In order to make sure the resulting instance is safe for creation only
        the new flag may be used as this will make sure that the proper identifier
        attributes are not set in the instance after the apply operation is done.

        :type model: Dictionary
        :param model: The map containing the model that is going to be applied
        to the new instance to be created.
        :type form: bool
        :param form: If in case the provided model is not valid (unset) the model
        should be retrieved from the current model in context, this is an unsafe
        operation as it may create unwanted behavior (use it carefully).
        :type safe: bool
        :param safe: If the attributes marked as safe in the model definition
        should be removed from the instance after the apply operation.
        :type build: bool
        :param build: If the "custom" build operation should be performed after
        the apply operation is performed so that new custom attributes may be
        injected into the resulting instance.
        :type fill: bool
        :param fill: If the various attributes of the model should be "filled"
        with default values (avoiding empty values).
        :type new: bool
        :param new: In case this value is valid the resulting instance is expected
        to be considered as new meaning that no identifier attributes are set.
        :rtype: Model
        :return: The new model instance resulting from the apply of the provided
        model and after the proper validations are performed on it.
        """

        if model == None: model = util.get_object() if form else dict()
        if fill: model = cls.fill(model)
        instance = cls()
        instance.apply(model, form = form, safe_a = safe)
        build and cls.build(instance.model, map = False)
        new and instance.assert_is_new()
        return instance

    @classmethod
    def old(cls, model = None, form = True, safe = True, build = False):
        return cls.new(
            model = model,
            form = form,
            safe = safe,
            build = build,
            new = False
        )

    @classmethod
    def wrap(cls, models, build = True, handler = None):
        """
        "Wraps" the provided sequence (or single set) of model based data into a
        sequence of models (or a single model) so that proper business logic may
        be used for operations on top of that data.

        In case the extra handler argument is passed it's going to be called for
        each model that is going to be "wrapped" allowing an extra "layer" for
        the transformation of the model.

        This operation is specially useful for api based environments where client
        side business logic is meant to be added to the static data.

        :type models: List
        :param models: Sequence (or single) set of models that are going to be wrapped
        around instances of the current class.
        :type build: bool
        :param build: If the "custom" build operation should be performed after
        the wrap operation is performed so that new custom attributes may be
        injected into the resulting instance.
        :type handler: Function
        :param handler: Handler function that is going to be called for each of the
        models after the build process has been performed, allows an extra transform
        operation to be performed at runtime.
        :rtype: List
        :return: The sequence of models (or single model) representing the provided
        set of dictionary models that were sent as arguments.
        """

        is_sequence = type(models) in (list, tuple)
        if not is_sequence: models = [models]
        wrapping = []
        for model in models:
            _model = cls(model = model)
            build and cls.build(_model.model, map = False)
            handler and handler(_model.model)
            wrapping.append(_model)
        if is_sequence: return wrapping
        else: return wrapping[0]

    @classmethod
    def singleton(
        cls,
        model = None,
        form = True,
        safe = True,
        build = False,
        *args,
        **kwargs
    ):
        instance = cls.get(raise_e = False, *args, **kwargs)
        if instance:
            instance.apply(model, form = form, safe_a = safe)
        else:
            instance = cls.old(
                model = model,
                form = form,
                safe = safe,
                build = build
            )
        return instance

    @classmethod
    def get(cls, *args, **kwargs):
        fields, eager, map, rules, meta, build, fill, skip, limit, sort, raise_e = cls._get_attrs(kwargs, (
            ("fields", None),
            ("eager", None),
            ("map", False),
            ("rules", True),
            ("meta", False),
            ("build", True),
            ("fill", True),
            ("skip", 0),
            ("limit", 0),
            ("sort", None),
            ("raise_e", True)
        ))

        fields = cls._sniff(fields, rules = rules)
        collection = cls._collection()
        model = collection.find_one(
            kwargs,
            projection = fields,
            skip = skip,
            limit = limit,
            sort = sort
        ) if mongo.is_new() else collection.find_one(
            kwargs,
            fields = fields,
            skip = skip,
            limit = limit,
            sort = sort
        )
        if not model and raise_e:
            is_devel = common.is_devel()
            if is_devel: message = "%s not found for %s" % (cls.__name__, str(kwargs))
            else: message = "%s not found" % cls.__name__
            raise exceptions.NotFoundError(
                message = message,
                code = 404
            )
        if not model and not raise_e: return model
        cls.types(model)
        if fill: cls.fill(model)
        if build: cls.build(model, map = map, rules = rules, meta = meta)
        if eager: model = cls._eager(model, eager)
        return model if map else cls.old(model = model, safe = False)

    @classmethod
    def find(cls, *args, **kwargs):
        fields, eager, map, rules, meta, build, fill, skip, limit, sort = cls._get_attrs(kwargs, (
            ("fields", None),
            ("eager", None),
            ("map", False),
            ("rules", True),
            ("meta", False),
            ("build", True),
            ("fill", True),
            ("skip", 0),
            ("limit", 0),
            ("sort", None)
        ))

        cls._find_s(kwargs)
        cls._find_d(kwargs)

        fields = cls._sniff(fields, rules = rules)
        collection = cls._collection()
        models = collection.find(
            kwargs,
            projection = fields,
            skip = skip,
            limit = limit,
            sort = sort
        ) if mongo.is_new() else collection.find(
            kwargs,
            fields = fields,
            skip = skip,
            limit = limit,
            sort = sort
        )
        models = [cls.types(model) for model in models]
        if fill: models = [cls.fill(model) for model in models]
        if build: [cls.build(model, map = map, rules = rules, meta = meta) for model in models]
        if eager: models = cls._eager(models, eager)
        models = models if map else [cls.old(model = model, safe = False) for model in models]
        return models

    @classmethod
    def count(cls, *args, **kwargs):
        cls._clean_attrs(kwargs)
        collection = cls._collection()
        if kwargs:
            result = collection.find(kwargs)
            result = result.count()
        else:
            result = collection.count()
        return result

    @classmethod
    def paginate(cls, skip = 0, limit = 1, *args, **kwargs):
        # retrieves the reference to the current global request in handling
        # this is going to be used for operations on the parameters
        request = common.base().get_request()

        # counts the total number of references according to the
        # current filter value and then uses this value together
        # with the skip value to calculate both the number of pages
        # available for the current filter and the current page index
        # (note that the index is one index based)
        total = cls.count(*args, **kwargs)
        count = total / float(limit)
        count = math.ceil(count)
        count = int(count)
        index = skip / float(limit)
        index = math.floor(index)
        index = int(index) + 1

        # creates the base structure for the page populating with the
        # base values that may be used for display of the page
        page = dict(
            count = count,
            index = index,
            start = skip + 1,
            end = skip + limit,
            total = total,
            sorter = request.params_s.get("sorter", None),
            direction = request.params_s.get("direction", "descending")
        )

        def generate(**kwargs):
            # creates a copy of the current definition of the parameters and for each
            # of the exclusion parameters removes it from the current structure
            params = dict(request.params_s)
            if "async" in params: del params["async"]

            # retrieves the "special" sorter keyword based argument and the equivalent
            # values for the current page in handling, this values are going to be used
            # for the calculus of the direction value (in case it's required)
            sorter = kwargs.get("sorter", None)
            _sorter = page["sorter"]
            direction = page["direction"]
            reverse = REVERSE.get(direction, "descending")

            # verifies if the sorter value is defined in the arguments and if that's
            # the case verifies if it's the same as the current one if that the case
            # the direction must be reversed otherwise the default direction is set
            if sorter and sorter == _sorter: params["direction"] = reverse
            elif sorter: params["direction"] = "descending"

            # "copies" the complete set of values from the provided keyword
            # based arguments into the parameters map, properly converting them
            # into the proper string value and then converts them into the linear
            # quoted manner so they they may be used as query string values
            for key, value in kwargs.items(): params[key] = str(value)
            query = [util.quote(key) + "=" + util.quote(value) for key, value in params.items()]
            query = "&".join(query)
            return "?" + query if query else query

        # updates the current page structure so that the (query) generation
        # method is exposed in order to modify the current query
        page["query"] = generate
        return page

    @classmethod
    def delete_c(cls, *args, **kwargs):
        collection = cls._collection()
        collection.remove(kwargs)

    @classmethod
    def ordered(cls, filter = dict):
        is_sequence = type(filter) in (list, tuple)
        if not is_sequence: filter = (filter,)

        ordered = list(cls._ordered)

        for name, value in cls.__dict__.items():
            if name.startswith("_"): continue
            if not name == name.lower(): continue
            if not isinstance(value, filter): continue
            if name in ordered: continue
            ordered.append(name)

        return ordered

    @classmethod
    def methods(cls):
        # in case the methods are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_methods" in cls.__dict__: return cls._methods

        # starts the list that will hold the various method names
        # for the class, note that this value will be ordered
        # according to the class level and the definition order
        methods = []

        # retrieves the complete model hierarchy for the current model
        # and it's going to be used to iterated through the class levels
        # in a top to bottom approach strategy
        hierarchy = cls.hierarchy()

        # iterates over the complete model hierarchy and retrieves the
        # ordered set of attributes from it extending the retrieved methods
        # list with the value for each of the model levels
        for _cls in hierarchy:
            ordered = _cls.ordered(
                filter = (
                    types.FunctionType,
                    classmethod
                )
            )
            methods.extend(ordered)

        # saves the retrieved set of methods in the current model definition
        # and then returns the value to the caller method as requested
        cls._methods = methods
        return methods

    @classmethod
    def fields(cls):
        # in case the fields are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_fields" in cls.__dict__: return cls._fields

        # starts the list that will hold the various field names
        # for the class, note that this value will be ordered
        # according to the class level and the definition order
        fields = []

        # retrieves the complete model hierarchy for the current model
        # and it's going to be used to iterated through the class levels
        # in a top to bottom approach strategy
        hierarchy = cls.hierarchy()

        # iterates over the complete model hierarchy and retrieves the
        # ordered set of attributes from it extending the retrieved fields
        # list with the value for each of the model levels
        for _cls in hierarchy:
            ordered = _cls.ordered()
            fields.extend(ordered)

        # saves the retrieved set of fields in the current model definition
        # and then returns the value to the caller method as requested
        cls._fields = fields
        return fields

    @classmethod
    def definition(cls):
        # in case the definition is already "cached" in the current
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
            for name, value in _cls.__dict__.items():
                if name.startswith("_"): continue
                if not name == name.lower(): continue
                if not isinstance(value, dict): continue
                if name in definition: raise exceptions.OperationalError(
                    message = "Duplicated attribute '%s' in '%s' hierarchy" %\
                        (name, _cls.__name__),
                    code = 412
                )
                definition[name] = value

        # sets the "default" definition for the based identifier
        # (underlying identifier attribute)
        definition["_id"] = dict()

        # saves the currently generated definition under the current
        # class and then returns the contents of it to the caller method
        cls._definition = definition
        return definition

    @classmethod
    def links(cls):
        # in case the links are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_links" in cls.__dict__: return cls._links

        # creates the list that will hold the complete set of method
        # names for links type methods
        links = []

        # retrieves the complete set of method names for the current
        # class this is going to be used to determine the ones that
        # are considered to be link oriented
        methods = cls.methods()

        # iterates over the complete set of method names for the current
        # class hierarchy to determine the ones that are links
        for name in methods:
            method = getattr(cls, name)
            if not hasattr(method, "_link"): continue
            reference = hasattr(method, "__self__") and method.__self__
            is_instance = False if reference else True
            method._link["instance"] = is_instance
            links.append(method._link)

        # sorts the various links taking into account the name of
        # the link, this is considered the pre-defined order
        links.sort(key = lambda item: item["name"])

        # saves the list of link method names defined under the current
        # class and then returns the contents of it to the caller method
        cls._links = links
        return links

    @classmethod
    def links_m(cls):
        # in case the links are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_links_m" in cls.__dict__: return cls._links_m

        # creates the map that will hold the complete set of method
        # names for links type methods
        links_m = dict()

        # retrieves the complete set of method names for the current
        # class this is going to be used to determine the ones that
        # are considered to be link oriented
        methods = cls.methods()

        # iterates over the complete set of method names for the current
        # class hierarchy to determine the ones that are links
        for name in methods:
            method = getattr(cls, name)
            if not hasattr(method, "_link"): continue
            links_m[method.__name__] = method._link

        # saves the map of link method names defined under the current
        # class and then returns the contents of it to the caller method
        cls._links_m = links_m
        return links_m

    @classmethod
    def link(cls, name):
        links_m = cls.links_m()
        return links_m.get(name, None)

    @classmethod
    def operations(cls):
        # in case the operations are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_operations" in cls.__dict__: return cls._operations

        # creates the list that will hold the complete set of method
        # names for operations type methods
        operations = []

        # retrieves the complete set of method names for the current
        # class this is going to be used to determine the ones that
        # are considered to be operation oriented
        methods = cls.methods()

        # iterates over the complete set of method names for the current
        # class hierarchy to determine the ones that are operations
        for name in methods:
            method = getattr(cls, name)
            if not hasattr(method, "_operation"): continue
            reference = hasattr(method, "__self__") and method.__self__
            is_instance = False if reference else True
            method._operation["instance"] = is_instance
            operations.append(method._operation)

        # sorts the various operations taking into account the name of
        # the operation, this is considered the pre-defined order
        operations.sort(key = lambda item: item["name"])

        # saves the list of operation method names defined under the current
        # class and then returns the contents of it to the caller method
        cls._operations = operations
        return operations

    @classmethod
    def operations_m(cls):
        # in case the operations are already "cached" in the current
        # class (fast retrieval) returns immediately
        if "_operations_m" in cls.__dict__: return cls._operations_m

        # creates the map that will hold the complete set of method
        # names for operations type methods
        operations_m = dict()

        # retrieves the complete set of method names for the current
        # class this is going to be used to determine the ones that
        # are considered to be operation oriented
        methods = cls.methods()

        # iterates over the complete set of method names for the current
        # class hierarchy to determine the ones that are operations
        for name in methods:
            method = getattr(cls, name)
            if not hasattr(method, "_operation"): continue
            operations_m[method.__name__] = method._operation

        # saves the map of operation method names defined under the current
        # class and then returns the contents of it to the caller method
        cls._operations_m = operations_m
        return operations_m

    @classmethod
    def operation(cls, name):
        operations_m = cls.operations_m()
        return operations_m.get(name, None)

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
    def base_names(cls):
        names = cls.fields()
        names = [name for name in names if not name.startswith("_")]
        return names

    @classmethod
    def create_names(cls):
        names = cls.base_names()
        extra = cls.extra_names()
        names.extend(extra)
        return names

    @classmethod
    def update_names(cls):
        return cls.create_names()

    @classmethod
    def show_names(cls):
        _names = []
        names = cls.base_names()
        definition = cls.definition()
        for name in names:
            value = definition.get(name, None)
            if value == None: continue
            is_private = value.get("private", False)
            if is_private: continue
            _names.append(name)
        return _names

    @classmethod
    def list_names(cls):
        return cls.show_names()

    @classmethod
    def extra_names(cls):
        return []

    @classmethod
    def order_name(self):
        return None

    @classmethod
    def build(cls, model, map = False, rules = True, meta = False):
        if rules: cls.rules(model, map)
        cls._build(model, map)
        if meta: cls._meta(model, map)

    @classmethod
    def rules(cls, model, map):
        for name, _value in legacy.eager(model.items()):
            definition = cls.definition_n(name)
            is_private = definition.get("private", False)
            if not is_private: continue
            del model[name]

    @classmethod
    def types(cls, model):
        definition = cls.definition()

        for name, value in legacy.eager(model.items()):
            if name == "_id": continue
            if value == None: continue
            if not name in definition: continue
            model[name] = cls.cast(name, value)

        return model

    @classmethod
    def fill(cls, model = None):
        """
        Fills the current models with the proper values so that
        no values are unset as this would violate the model definition
        integrity. This is required when retrieving an object(s) from
        the data source (as some of them may be incomplete).

        :type model: Model
        :param model: The model that is going to have its unset
        attributes filled with "default" data, in case none is provided
        all of the attributes will be filled with "default" data.
        """

        model = model or dict()
        definition = cls.definition()
        for name, _definition in definition.items():
            if name in model: continue
            if name in ("_id",): continue
            increment = _definition.get("increment", False)
            if increment: continue
            if "initial" in _definition:
                initial = _definition.get("initial")
                model[name] = initial
            else:
                _type = _definition.get("type")
                default = TYPE_DEFAULTS.get(_type, None)
                default = _type._default() if hasattr(_type, "_default") else default
                model[name] = default

        return model

    @classmethod
    def cast(cls, name, value):
        definition = cls.definition()
        if not name in definition: return value
        if value == None: return value
        _definition = cls.definition_n(name)
        _type = _definition.get("type", legacy.UNICODE)
        builder = BUILDERS.get(_type, _type)
        try:
            return builder(value) if builder else value
        except:
            default = TYPE_DEFAULTS.get(_type, None)
            default = _type._default() if hasattr(_type, "_default") else default
            return default

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
            for name in legacy.eager(_cls.__dict__.keys()):
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
    def _meta(cls, model, map):
        for key, value in legacy.eager(model.items()):
            definition = cls.definition_n(key)
            meta = cls._solve(key)
            mapper = METAS.get(meta, None)
            if mapper and not value == None: value = mapper(value, definition)
            else: value = value if value == None else legacy.UNICODE(value)
            model[key + "_meta"] = value

    @classmethod
    def _sniff(cls, fields, rules = False):
        fields = fields or cls.fields()
        fields = list(fields)
        if not rules: return fields
        for field in list(fields):
            definition = cls.definition_n(field)
            is_private = definition.get("private", False)
            if is_private: fields.remove(field)
        return fields

    @classmethod
    def _solve(cls, name):
        definition = cls.definition_n(name)
        type = definition.get("type", legacy.UNICODE)
        for cls in type.mro():
            base = TYPE_META.get(cls, None)
            if base: break
        return definition.get("meta", base)

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
    def _eager(cls, model, names):
        # verifies if the provided model instance is a sequence and if
        # that's the case runs the recursive eager loading of names and
        # returns the resulting sequence to the caller method
        is_list = isinstance(model, (list, tuple))
        if is_list: return [cls._eager(_model, names) for _model in model]

        # iterates over the complete set of names that are meant to be
        # eager loaded from the model and runs the "resolution" process
        # for each of them so that they are properly eager loaded
        for name in names:
            value = model[name]
            if not value: continue
            if not isinstance(value, TYPE_REFERENCES): continue
            model[name] = value.resolve()

        # returns the resulting model to the caller method, most of the
        # times this model should have not been touched
        return model

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
    def _clean_attrs(cls, kwargs, dirty = DIRTY_PARAMS):
        for key in dirty:
            if not key in kwargs: continue
            del kwargs[key]

    @classmethod
    def _find_s(cls, kwargs):
        # retrieves the kind of insensitive strategy that is going
        # to be used for the resolution of regular expressions,
        # this should affect all the filters and so it should be
        # used with some amount of care
        if "find_i" in kwargs:
            find_i = kwargs["find_i"]
            del kwargs["find_i"]
        else:
            find_i = False

        # retrieves the kind of default operation to be performed
        # this may be either: right, left or both and the default
        # value is both so that the token is matched in case it
        # appears anywhere in the search string
        if "find_t" in kwargs:
            find_t = kwargs["find_t"]
            del kwargs["find_t"]
        else:
            find_t = "both"

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

        # constructs the proper right and left parts of the regex
        # that is going to be constructed for the matching of the
        # value, this is achieved by checking the find type
        right = "^" if find_t == "right" else ""
        left = "$" if find_t == "left" else ""

        # retrieves the definition for the default attribute and uses
        # it to retrieve it's target data type, defaulting to the
        # string type in case none is defined in the schema
        definition = cls.definition_n(default)
        default_t = definition.get("type", legacy.UNICODE)

        try:
            # in case the target date type for the default field is
            # string the both sides wildcard regex is used for the
            # search otherwise the search value to be used is the
            # exact match of the value (required type conversion)
            if default_t in legacy.STRINGS: find_v = {
                "$regex" : right + re.escape(find_s) + left,
                "$options": "-i" if find_i else ""
            }
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
    def _find_d(cls, kwargs):
        # in case the find definition is currently not defined in the
        # named arguments map returns immediately as nothing is
        # meant to be done on this method
        if not "find_d" in kwargs: return

        # retrieves the find definition into a local variable, then
        # removes the find definition from the named arguments map
        # so that it's not going to be erroneously used by the
        # underlying find infra-structure
        find_d = kwargs["find_d"]
        del kwargs["find_d"]

        # verifies that the data type for the find definition is a
        # valid sequence and in case its not converts it into one
        # so that it may be used in sequence valid logic
        if not type(find_d) == list: find_d = [find_d]

        # iterates over all the filters defined in the filter definition
        # so that they may be used to update the provided arguments with
        # the filter defined in each of their lines
        for filter in find_d:
            # in case the filter is not valid (unset or invalid) it's going
            # to be ignored as no valid information is present
            if not filter: continue

            # splits the filter string into its three main components
            # the name, operator and value, that are going to be processed
            # as defined by the specification to create the filter
            name, operator, value = filter.split(":", 2)

            # retrieves the definition for the filter attribute and uses
            # it to retrieve it's target data type that is going to be
            # used for the proper conversion, note that in case the base
            # type resolution method exists it's used (recursive resolution)
            definition = cls.definition_n(name)
            name_t = definition.get("type", legacy.UNICODE)
            if hasattr(name_t, "_btype"): name_t = name_t._btype()

            # determines if the current filter operation should be performed
            # using a case insensitive based approach to the search, by default
            # all of the operations are considered to be case sensitive
            insensitive = INSENSITIVE.get(operator, False)

            # retrieves the method that is going to be used for value mapping
            # or conversion based on the current operator and then converts
            # the operator into the domain specific operator
            value_method = VALUE_METHODS.get(operator, None)
            operator = OPERATORS.get(operator, operator)

            # in case there's a custom value mapped retrieved uses it to convert
            # the string based value into the target specific value for the query
            # otherwise uses the data type for the search field for value conversion
            if value_method: value = value_method(value, name_t)
            else: value = name_t(value)

            # constructs the custom find value using a key and value map value
            # in case the operator is defined otherwise (operator not defined)
            # the value is used directly, then merges this find value into the
            # current set of filters for the provided (keyword) arguments
            find_v = {operator : value} if operator else value
            if insensitive: find_v["$options"] = "-i"
            cls.filter_merge(name, find_v, kwargs)

    @classmethod
    def _bases(cls):
        """
        Retrieves the complete set of base (parent) classes for
        the current class, this method is safe as it removes any
        class that does not inherit from the entity class.

        Please note that this function only retrieves the set of
        direct parents of the class and not the complete hierarchy.

        :rtype: List/Tuple
        :return: The set containing the various bases classes for
        the current class that are considered valid.
        """

        # retrieves the complete set of base classes for
        # the current class and in case the observable is
        # not in the bases set returns the set immediately
        # as the top level model has not been reached yet
        bases = cls.__bases__
        if not bases == Model.__bases__: return bases

        # returns an empty tuple to the caller method as the
        # top level class has been reached and the class is
        # considered to have no "valid" base classes
        return ()

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

    @property
    def request(self):
        return common.base().get_request()

    @property
    def session(self):
        return common.base().get_session()

    @property
    def logger(self):
        if self.owner: return self.owner.logger
        else: return logging.getLogger()

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

        :type model: Map
        :param model: The model map to be used for the build
        operation in case none is specified the currently set
        model is used instead.
        :type rules: bool
        :param rules: If the (security) rules should be applied to
        the model that is going to be built.
        """

        cls = self.__class__
        model = model or self.model
        cls.build(model, rules = rules)

    def apply(self, model = None, form = True, safe = None, safe_a = True):
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
            for _safe in safes: safe[_safe] = True

        # retrieves the object loading it from all the available
        # sources and then iterates over all the of the model
        # values setting the values in the current intance's model
        # then runs the type casting/conversion operation in it
        if model == None: model = util.get_object() if form else dict()
        for name, value in legacy.eager(model.items()):
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

        :type name: String
        :param name: The name of the validation method that should
        be added to the extras list, note that the real name of
        the method should be prefixed with the "validate" prefix
        """

        cls = self.__class__
        method = getattr(cls, "validate_" + name)
        self._extras.append(method)

    def is_new(self):
        return not "_id" in self.model

    def assert_is_new(self):
        """
        Ensures that the current model instance is a new one meaning
        that the inner identifier of the model is not currently set.

        This method may be used to avoid security issues of providing
        update permissions for situations where only creation is allowed.

        The method raises an exception if the current instance is not
        considered to be a new one causing the current control flow to
        be returned to the caller method until catching of exception.
        """

        if self.is_new(): return
        raise exceptions.OperationalError(
            message = "Instance is not new, identifier is set",
            code = 412
        )

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
        # update operation and the "immutable rules" also apply, the
        # returned value is normalized meaning that for instance if
        # any relation is loaded the reference value is returned instead
        # of the loaded relation values (required for persistence)
        model = self._filter(
            increment_a = is_new,
            immutables_a = not is_new,
            normalize = True
        )

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

    def reload(self, *args, **kwargs):
        is_new = self.is_new()
        if is_new: raise exceptions.OperationalError(
            message = "Can't reload a new model entity",
            code = 412
        )
        cls = self.__class__
        return cls.get(_id = self._id, *args, **kwargs)

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
            for key, value in _errors.items():
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
        if errors: raise exceptions.ValidationError(errors, self)

        # calls the event handler for the validation process this
        # should finish the operations from a correct validation
        self.post_validate()

    def _filter(self, increment_a = True, immutables_a = False, normalize = False):
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
        # fields so that a new value is set on the model, note that if
        # the increment apply is unset the increment operation is ignored
        for name in increments:
            if not increment_a: continue
            model[name] = cls._increment(name)

        # iterates over all the model items to filter the ones
        # that are not valid for the current class context
        for name, value in legacy.eager(self.model.items()):
            if not name in definition: continue
            if immutables_a and name in immutables: continue
            value = self._evaluate(name, value)
            model[name] = value

        # in case the normalize flag is set must iterate over all
        # items to try to normalize the values by calling the reference
        # value this will returns the reference index value instead of
        # the normal value that would prevent normalization
        if normalize:
            for name, value in legacy.eager(self.model.items()):
                if not name in definition: continue
                if not hasattr(value, "ref_v"): continue
                model[name] = value.ref_v()

        # returns the model containing the "filtered" items resulting
        # from the validation of the items against the model class
        return model

    def _evaluate(self, name, value):
        # verifies if the current value is an iterable one in case
        # it is runs the evaluate method for each of the values to
        # try to resolve them into the proper representation
        is_iterable = hasattr(value, "__iter__")
        is_iterable = is_iterable and not type(value) in ITERABLES
        if is_iterable: return [self._evaluate(name, value) for value in value]

        # verifies the current value's class is sub class of the model
        # class and in case it's extracts the relation name from the
        # value and sets it as the value in iteration
        is_model = issubclass(value.__class__, Model)
        if is_model:
            meta = getattr(self.__class__, name)
            _type = meta.get("type", legacy.BYTES)
            _name = _type._name
            value = getattr(value, _name)

        # iterates over all the values and retrieves the json value for
        # each of them in case the value contains a json value retrieval
        # method otherwise uses the normal value returning it to the caller
        value = value.json_v() if hasattr(value, "json_v") else value
        return value

class Field(dict):
    """
    Top level field class that should be used for the
    definition of the various fields of the model, a
    dictionary may be sued alternatively but some of the
    ordering features and other are going o be lost.
    """

    creation_counter = 0
    """ The global static creation counter value that
    will be used to create an order in the declaration
    of attributes for a class "decorated" with the
    ordered attributes metaclass """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

class Link(dict):
    """
    Internal link class used to encapsulate some of the
    internal concepts associated with a link, providing
    an easy to use structure at runtime.

    The base interface should conform with the dictionary
    interface in order to provide backwards compatibility.
    """

    pass

class Operation(dict):
    """
    Logical structure representing an operation, should
    provide a simple interface for interaction with the
    operation and inputs/outputs of it.

    The base interface should conform with the dictionary
    interface in order to provide backwards compatibility.
    """

    def cast(self, values):
        """
        Runs the "casting" operation for a series of provided
        values, the order sequence of the provided values is
        relevant and should conform with the specified order
        for the operation parameters.

        :type values: List
        :param values: The sequence containing the various values
        that are going to be casted according to the operation spec.
        :rtype: List
        :return: The sequence of values now casted with the proper
        data types as specified in operation structure.
        """

        # creates the list that will hold the "final" casted values
        # should have the same size of the input values list
        casted = []

        # retrieves the reference to the parameters specification
        # and then uses it in the iteration for the casting of the
        # various "passed" raw values
        parameters = self.get("parameters", [])
        for value, parameters in zip(values, parameters):
            cast = parameters[2]
            if cast and not value in (None, ""): value = cast(value)
            casted.append(value)

        # returns the final list of casted values to the caller method
        # so that it may be used safely in the context
        return casted

def link(name = None):
    """
    Decorator function to be used to "annotate" the provided
    function as an link (string) that is able to change the user
    agent to a location of a certain interest.

    Proper usage of the link definition/decoration is context
    based and should vary based on application.

    :type name: String
    :param name: The name of the link (in plain english) so that
    a better user experience is possible.
    :rtype: Function
    :return: The decorator function that is going to be used to
    generated the final function to be called.
    """

    def decorator(function, *args, **kwargs):
        function._link = Link(
            method = function.__name__,
            name = name or function.__name__
        )
        return function

    return decorator

def operation(name = None, parameters = (), level = 1):
    """
    Decorator function to be used to "annotate" the provided
    function as an operation that is able to change the current
    entity sate and behavior.

    Proper usage of the operation definition/decoration is context
    based and should vary based on application.

    :type name: String
    :param name: The name of the operation (in plain english)
    so that a better user experience is possible.
    :type parameters: Tuple
    :param parameters: The sequence containing tuples that describe
    the various parameters to be send to the operation.
    :type level: int
    :param level: The severity level of the operation, the higher
    values will be considered more severe than the lower ones,
    evaluation of the value will be context based.
    :rtype: Function
    :return: The decorator function that is going to be used to
    generated the final function to be called.
    """

    def decorator(function, *args, **kwargs):
        function._operation = Operation(
            method = function.__name__,
            name = name or function.__name__,
            parameters = parameters,
            level = level
        )

        return function

    return decorator

field = Field
