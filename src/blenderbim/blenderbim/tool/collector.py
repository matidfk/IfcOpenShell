# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell.util.element
from typing import Union


class Collector(blenderbim.core.tool.Collector):
    @classmethod
    def assign(cls, obj: bpy.types.Object) -> None:
        """Links an object to an appropriate Blender collection."""
        element = tool.Ifc.get_entity(obj)

        if element.is_a("IfcGridAxis"):
            element = (element.PartOfU or element.PartOfV or element.PartOfW)[0]

        if element.is_a("IfcProject"):
            if collection := cls._create_own_collection(obj):
                cls.link_to_collection_safe(obj, collection)
                cls.link_to_collection_safe(collection, bpy.context.scene.collection)
        elif element.is_a("IfcTypeProduct"):
            collection = cls._create_project_child_collection("IfcTypeProduct")
            cls.link_to_collection_safe(obj, collection)
        elif element.is_a("IfcOpeningElement"):
            collection = cls._create_project_child_collection("IfcOpeningElement")
            cls.link_to_collection_safe(obj, collection)
        elif element.is_a("IfcStructuralItem"):
            collection = cls._create_project_child_collection("IfcStructuralItem")
            cls.link_to_collection_safe(obj, collection)
        elif tool.Ifc.get_schema() == "IFC2X3" and element.is_a("IfcSpatialStructureElement"):
            if collection := cls._create_own_collection(obj):
                cls.link_to_collection_safe(obj, collection)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_to_collection_safe(collection, project_obj.BIMObjectProperties.collection)
        elif tool.Ifc.get_schema() != "IFC2X3" and element.is_a("IfcSpatialElement"):
            if collection := cls._create_own_collection(obj):
                cls.link_to_collection_safe(obj, collection)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_to_collection_safe(collection, project_obj.BIMObjectProperties.collection)
        elif container := ifcopenshell.util.element.get_container(element):
            container_obj = tool.Ifc.get_object(container)
            if not (collection := container_obj.BIMObjectProperties.collection):
                cls.assign(container_obj)
                collection = container_obj.BIMObjectProperties.collection
            cls.link_to_collection_safe(obj, collection)
        elif element.is_a("IfcAnnotation"):
            if element.ObjectType == "DRAWING":
                if collection := cls._create_own_collection(obj):
                    cls.link_to_collection_safe(obj, collection)
                    project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                    cls.link_to_collection_safe(collection, project_obj.BIMObjectProperties.collection)
            else:
                for rel in element.HasAssignments or []:
                    if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                        for related_object in rel.RelatedObjects:
                            if related_object.is_a("IfcAnnotation") and related_object.ObjectType == "DRAWING":
                                drawing_obj = tool.Ifc.get_object(related_object)
                                if drawing_obj:
                                    cls.link_to_collection_safe(obj, drawing_obj.BIMObjectProperties.collection)
        else:
            collection = cls._create_project_child_collection("Unsorted")
            cls.link_to_collection_safe(obj, collection)

    @classmethod
    def _create_project_child_collection(cls, name: str) -> bpy.types.Collection:
        """get or create new collection inside project"""
        collection = bpy.data.collections.get(name)
        if not collection:
            collection = bpy.data.collections.new(name)
            project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
            project_obj.BIMObjectProperties.collection.children.link(collection)
            collection.hide_viewport = True
        return collection

    @classmethod
    def _create_own_collection(cls, obj: bpy.types.Object) -> bpy.types.Collection:
        """get or create own collection for the element"""
        if obj.BIMObjectProperties.collection:
            return
        collection = bpy.data.collections.new(obj.name)
        obj.BIMObjectProperties.collection = collection
        collection.BIMCollectionProperties.obj = obj
        return collection

    @classmethod
    def link_to_collection_safe(
        cls, obj_or_col: Union[bpy.types.Object, bpy.types.Collection], collection: bpy.types.Collection
    ) -> None:
        """Link `obj_or_col` (an object or a collection) to the `collection`
        if `obj_or_col` is not part of that collection already.

        Method is needed to avoid RuntimeErrors like below that occur if you link object/collection
        to the collection directly and they are already part of that collection.
        RuntimeError: Error: Object 'xxx' already in collection 'xxx'.
        """
        # TODO: Maybe just catching RuntimeError is faster?
        if isinstance(obj_or_col, bpy.types.Object):
            if collection.objects.find(obj_or_col.name) != -1:
                return
            collection.objects.link(obj_or_col)
            return

        if collection.children.find(obj_or_col.name) != -1:
            return
        collection.children.link(obj_or_col)
