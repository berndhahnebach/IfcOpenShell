# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import test.bim.bootstrap
import bonsai.core.tool
import bonsai.tool as tool
import pytest
import tempfile
from pathlib import Path
from bonsai.tool.ifc import Ifc as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Ifc)


class TestSet(test.bim.bootstrap.NewFile):
    def test_setting_an_ifc_data(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        assert subject.get() == ifc


class TestGet(test.bim.bootstrap.NewFile):
    def test_getting_an_ifc_dataset_from_a_ifc_spf_filepath(self):
        assert subject.get() is None
        props = tool.Blender.get_bim_props()
        props.ifc_file = "test/files/basic.ifc"
        result = subject.get()
        assert isinstance(result, ifcopenshell.file)

    def test_getting_the_active_ifc_dataset_regardless_of_ifc_path(self):
        props = tool.Blender.get_bim_props()
        props.ifc_file = "test/files/basic.ifc"
        ifc = ifcopenshell.file()
        subject.set(ifc)
        assert subject.get() == ifc


class TestRun(test.bim.bootstrap.NewFile):
    def test_running_a_command_on_the_active_ifc_dataset(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        wall = subject.run("root.create_entity", ifc_class="IfcWall")
        assert subject.get().by_type("IfcWall")[0] == wall


class TestGetSchema(test.bim.bootstrap.NewFile):
    def test_getting_the_schema_version_identifier(self):
        ifc = ifcopenshell.file(schema="IFC4")
        subject.set(ifc)
        assert subject.get_schema() == "IFC4"


class TestIsEdited(test.bim.bootstrap.NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        assert subject.is_edited(obj) is False
        obj.scale[0] = 2
        assert subject.is_edited(obj) is True
        obj.scale[0] = 1
        assert subject.is_edited(obj) is False
        tool.Ifc.edit(obj)
        assert subject.is_edited(obj) is True


class TestIsMoved(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)

        obj = bpy.data.objects.new("Object", None)
        element = ifc.create_entity("IfcWall")
        subject.link(element, obj)
        assert subject.is_moved(obj) is True

        tool.Geometry.record_object_position(obj)
        assert subject.is_moved(obj) is False

        obj.matrix_world[0][3] += 1
        assert subject.is_moved(obj) is True

    def test_that_a_type_or_project_never_moves_but_a_grid_axis_does(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)

        obj = bpy.data.objects.new("Object", None)
        element = ifc.create_entity("IfcWallType")
        subject.link(element, obj)
        assert subject.is_moved(obj) is False

        element = ifc.create_entity("IfcProject")
        subject.link(element, obj)
        assert subject.is_moved(obj) is False

        element = ifc.create_entity("IfcGridAxis")
        subject.link(element, obj)
        assert subject.is_moved(obj) is True


class TestGetEntity(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.create_entity("IfcWall")
        subject.link(element, obj)
        assert subject.get_entity(obj) == element

    def test_attempting_to_get_an_unlinked_object(self):
        obj = bpy.data.objects.new("Object", None)
        assert subject.get_entity(obj) is None

    def test_attempting_without_a_file(self):
        obj = bpy.data.objects.new("Object", None)
        props = tool.Blender.get_object_bim_props(obj)
        props.ifc_definition_id = 1
        assert subject.get_entity(obj) is None

    def test_attempting_to_get_an_invalidly_linked_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        props = tool.Blender.get_object_bim_props(obj)
        props.ifc_definition_id = 1
        assert subject.get_entity(obj) is None


class TestGetObject(test.bim.bootstrap.NewFile):
    def test_get_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcWall")
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        assert subject.get_object(element) == obj

    def test_get_material(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcSurfaceStyle")
        obj = bpy.data.materials.new("Style")
        subject.link(element, obj)
        assert subject.get_object(element) == obj


class TestLink(test.bim.bootstrap.NewFile):
    def test_link_an_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcWall")
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        assert subject.get_entity(obj) == element
        assert subject.get_object(element) == obj

    def test_link_a_style(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcSurfaceStyle")
        obj = bpy.data.materials.new("Material")
        subject.link(element, obj)
        assert subject.get_entity(obj) == element
        assert subject.get_object(element) == obj

    def test_link_not_a_style_to_blender_material(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcMaterial")
        obj = bpy.data.materials.new("Material")
        with pytest.raises(AttributeError):
            subject.link(element, obj)

    def test_link_a_mesh(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcShapeRepresentation")
        obj = bpy.data.meshes.new("Material")
        subject.link(element, obj)
        assert tool.Geometry.get_mesh_props(obj).ifc_definition_id == element.id()


class TestUnlink(test.bim.bootstrap.NewFile):
    def test_unlink_an_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcWall")
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        subject.unlink(element)
        assert subject.get_entity(obj) is None
        assert subject.get_object(element) is None

    def test_unlink_a_style(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcSurfaceStyle")
        obj = bpy.data.materials.new("Material")
        subject.link(element, obj)
        subject.unlink(element)
        assert subject.get_entity(obj) is None
        assert subject.get_object(element) is None

    def test_unlinking_using_an_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcWall")
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        subject.unlink(obj=obj)
        assert subject.get_entity(obj) is None
        assert subject.get_object(element) is obj

    def test_unlinking_using_both_arguments(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.create_entity("IfcWall")
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        with pytest.raises(TypeError):
            subject.unlink(element=element, obj=obj)
        assert subject.get_entity(obj) == element
        assert subject.get_object(element) == obj


class TestUri(test.bim.bootstrap.NewFile):
    def test_get_uri(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            project_dir = base_path / "project"
            project_dir.mkdir()
            path = project_dir / "project.ifc"
            test_name = "test.xml"
            test_filepath = project_dir / test_name
            test_filepath.touch()
            path.touch()
            subject.set_path(subject.normalize_path(path))

            # Test absolute filepaths.
            abs_filepath = str(test_filepath)
            assert subject.get_uri(abs_filepath, False) == subject.normalize_path(abs_filepath)
            assert subject.get_uri(abs_filepath, True) == test_name

            # Test relative filepaths.
            rel_filepath = test_name
            with pytest.raises(ValueError):
                subject.get_uri(rel_filepath, False)

            assert subject.get_uri(rel_filepath, True) == test_name

            # Test that paths are resolved, but keeping symlinks.
            link_name = "link.xml"
            link_path = base_path / link_name
            link_path.symlink_to(test_filepath)

            # Test absolute paths.
            abs_filepath = test_filepath.parent / ".." / link_name
            assert subject.get_uri(abs_filepath, False) == subject.normalize_path(abs_filepath)
            assert subject.get_uri(abs_filepath, True) == "../" + link_name

            # Test relative paths.
            rel_filepath = "../" + link_name
            with pytest.raises(ValueError):
                subject.get_uri(rel_filepath, False)
            assert subject.get_uri(rel_filepath, True) == rel_filepath

    def test_resolve_uri(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            project_dir = base_path / "project"
            project_dir.mkdir()
            path = project_dir / "project.ifc"
            path.touch()
            subject.set_path(subject.normalize_path(path))
            test_name = "test.xml"
            test_filepath = project_dir / test_name
            test_filepath.touch()

            # Test absolute filepaths.
            abs_filepath = str(test_filepath)
            assert subject.resolve_uri(abs_filepath) == subject.normalize_path(abs_filepath)
            rel_filepath = test_name
            assert subject.resolve_uri(rel_filepath) == subject.normalize_path(abs_filepath)

            # Test that paths are resolved, but keeping symlinks.
            link_name = "link.xml"
            link_path = base_path / link_name
            link_path.symlink_to(test_filepath)

            # Test absolute path.
            abs_filepath = test_filepath.parent / ".." / link_name
            assert subject.resolve_uri(abs_filepath) == subject.normalize_path(abs_filepath)

            # Test relative path.
            rel_filepath = "../" + link_name
            assert subject.resolve_uri(rel_filepath) == subject.normalize_path(abs_filepath)

    def test_normalize_path(self):
        # Posix format.
        path = r"test\test.txt"
        assert subject.normalize_path(path) == "test/test.txt"

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            project_path = base_path / "project"
            project_path.mkdir()
            original_file = project_path / "test.xml"
            original_file.touch()

            link_name = "link.xml"
            link_path = project_path / link_name
            link_path.symlink_to(original_file)

            # Absolute path.
            abs_path = project_path / ".." / link_name
            assert subject.normalize_path(abs_path) == (base_path / link_name).as_posix()

            rel_path = "../" + link_name
            assert subject.normalize_path(rel_path) == rel_path
