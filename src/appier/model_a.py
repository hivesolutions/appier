#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import copy

from . import legacy

class ModelAsync(object):

    @classmethod
    async def _increment_a(cls, name):
        _name = cls._name() + ":" + name
        store = cls._collection(name = "counters")
        value = await store.find_and_modify(
            {
                "_id" : _name
            },
            {
                "$inc" : {
                    "seq" : 1
                }
            },
            new = True,
            upsert = True
        )
        value = value or await store.find_one({
            "_id" : _name
        })
        return value["seq"]

    async def save_a(
        self,
        validate = True,
        verify = True,
        is_new = None,
        increment_a = None,
        immutables_a = None,
        pre_validate = True,
        pre_save = True,
        pre_create = True,
        pre_update = True,
        post_validate = True,
        post_save = True,
        post_create = True,
        post_update = True
    ):
        # ensures that the current instance is associated with
        # a concrete model, ready to be persisted in database
        if verify: self.assert_is_concrete()

        # checks if the instance to be saved is a new instance
        # or if this is an update operation and then determines
        # series of default values taking that into account
        if is_new == None: is_new = self.is_new()
        if increment_a == None: increment_a = is_new
        if immutables_a == None: immutables_a = not is_new

        # runs the validation process in the current model, this
        # should ensure that the model is ready to be saved in the
        # data source, without corruption of it, only run this process
        # in case the validate flag is correctly set
        validate and self._validate(
            pre_validate = pre_validate,
            post_validate = post_validate
        )

        # calls the complete set of event handlers for the current
        # save operation, this should trigger changes in the model
        pre_save and self.pre_save()
        pre_create and is_new and self.pre_create()
        pre_update and not is_new and self.pre_update()

        # filters the values that are present in the current model
        # so that only the valid ones are stored in, invalid values
        # are going to be removed, note that if the operation is an
        # update operation and the "immutable rules" also apply, the
        # returned value is normalized meaning that for instance if
        # any relation is loaded the reference value is returned instead
        # of the loaded relation values (required for persistence)
        model = await self._filter_a(
            increment_a = increment_a,
            immutables_a = immutables_a,
            normalize = True
        )

        # in case the current model is not new must create a new
        # model instance and remove the main identifier from it
        if not is_new: _model = copy.copy(model); del _model["_id"]

        # retrieves the reference to the store object to be used and
        # uses it to store the current model data
        store = self._get_store()
        if is_new:
            await store.insert(model)
            self.apply(model, safe_a = False)
        else:
            await store.update({"_id" : model["_id"]}, {"$set" : _model})

        # calls the post save event handlers in order to be able to
        # execute appropriate post operations
        post_save and self.post_save()
        post_create and is_new and self.post_create()
        post_update and not is_new and self.post_update()

        # returns the instance that has just been used for the save
        # operation, this may be used for chaining operations
        return self

    async def _filter_a(
        self,
        increment_a = True,
        immutables_a = False,
        normalize = False,
        resolve = False,
        all = False,
        evaluator = "json_v"
    ):
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
            if name in self.model:
                model[name] = cls._ensure_min(name, self.model[name])
            else:
                model[name] = await cls._increment_a(name)

        # iterates over all the model items to filter the ones
        # that are not valid for the current class context
        for name, value in legacy.eager(self.model.items()):
            if not name in definition: continue
            if immutables_a and name in immutables: continue
            value = self._evaluate(name, value, evaluator = evaluator)
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

        # in case the resolution flag is set, it means that a recursive
        # approach must be performed for the resolution of values that
        # implement the map value (recursive resolution) method, this is
        # a complex (and possible computational expensive) process that
        # may imply access to the base data source
        if resolve:
            for name, value in legacy.eager(self.model.items()):
                if not name in definition: continue
                model[name] = cls._resolve(name, value)

        # in case the all flag is set the extra fields (not present
        # in definition) must also be used to populate the resulting
        # (filtered) map so that it contains the complete set of values
        # present in the base map of the current instance
        if all:
            for name, value in legacy.eager(self.model.items()):
                if name in model: continue
                model[name] = value

        # returns the model containing the "filtered" items resulting
        # from the validation of the items against the model class
        return model