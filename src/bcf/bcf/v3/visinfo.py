import uuid
import zipfile
from typing import Any, Optional, Literal, Union
from collections.abc import Iterable

import numpy as np
from ifcopenshell import entity_instance
import ifcopenshell.util.unit
import ifcopenshell.util.placement
from numpy.typing import NDArray

import bcf.v3.model as mdl
from bcf.geometry import (
    camera_vectors_from_element_placement,
    camera_vectors_from_target_position,
)
from bcf.inmemory_zipfile import ZipFileInterface
from bcf.xml_parser import AbstractXmlParserSerializer, XmlParserSerializer


class VisualizationInfoHandler:
    """Handle the VisualizationInfo and related objects."""

    def __init__(
        self,
        visualization_info: mdl.VisualizationInfo,
        snapshot: Optional[bytes] = None,
        bitmaps: Optional[dict[str, bytes]] = None,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> None:
        self.visualization_info = visualization_info
        self.snapshot = snapshot
        self.bitmaps = bitmaps or {}
        self._xml_handler = xml_handler or XmlParserSerializer()

    @property
    def guid(self) -> str:
        """Return the GUID of the visualization info."""
        return self.visualization_info.guid

    @classmethod
    def from_topic_viewpoints(
        cls,
        topic_dir: zipfile.Path,
        vps: Iterable[mdl.ViewPoint],
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> dict[str, "VisualizationInfoHandler"]:
        """Create VisualizationInfoHandler objects of a Topic's ViewPoints."""
        viewpoints = {}
        for vpt in vps:
            visinfo = cls.load(topic_dir, vpt, xml_handler)
            if visinfo and vpt.viewpoint:
                viewpoints[vpt.viewpoint] = visinfo
        return viewpoints

    @classmethod
    def load(
        cls,
        topic_dir: zipfile.Path,
        vpt: mdl.ViewPoint,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> Optional["VisualizationInfoHandler"]:
        """
        Load the VisualizationInfo and related objects from a BCF zip file.

        Args:
            topic_dir: The directory in the BCF zip file to load from.
            vpt: The ViewPoint to load.
            xml_handler: The XML handler to use to parse the VisualizationInfo.

        Returns:
            The VisualizationInfoHandler object.
        """
        visinfo = cls._load_visinfo(topic_dir, vpt.viewpoint, xml_handler)
        if not visinfo:
            return None
        snapshot = cls._load_snapshot(topic_dir, vpt.snapshot)
        bitmaps = cls._load_bitmaps(topic_dir, visinfo)
        return cls(visinfo, snapshot, bitmaps, xml_handler)

    @staticmethod
    def _load_visinfo(
        topic_dir: zipfile.Path,
        vp_name: Optional[str],
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> Optional[mdl.VisualizationInfo]:
        if not vp_name:
            return None
        vp_path = topic_dir.joinpath(vp_name)
        if vp_path.exists():
            xml_handler = xml_handler or XmlParserSerializer()
            return xml_handler.parse(vp_path.read_bytes(), mdl.VisualizationInfo)
        return None

    @staticmethod
    def _load_snapshot(topic_dir: zipfile.Path, vp_snapshot: Optional[str]) -> Optional[bytes]:
        if vp_snapshot:
            snapshot_path = topic_dir.joinpath(vp_snapshot)
            if snapshot_path.exists():
                return snapshot_path.read_bytes()
        return None

    @staticmethod
    def _load_bitmaps(topic_dir: zipfile.Path, visinfo: Optional[mdl.VisualizationInfo]) -> dict[str, bytes]:
        if not visinfo or not (bitmaps := visinfo.bitmaps):
            return {}
        bitmaps_dict = {}
        for bitmap in bitmaps.bitmap:
            if not bitmap.reference:
                continue
            bitmap_path = topic_dir.joinpath(bitmap.reference)
            if bitmap_path.exists():
                bitmaps_dict[bitmap.reference] = bitmap_path.read_bytes()
        return bitmaps_dict

    def save(
        self,
        bcf_zip: ZipFileInterface,
        topic_dir: str,
        vpt: mdl.ViewPoint,
    ) -> None:
        """
        Save the VisualizationInfo and related objects to a BCF zip file.

        Args:
            bcf_zip: The BCF zip file to save to.
            topic_dir: The directory in the BCF zip file to save to.
            vpt: The ViewPoint to save.
        """
        if not (vp_name := vpt.viewpoint):
            return
        self._save_visinfo(bcf_zip, topic_dir, vp_name)
        self._save_snapshot(bcf_zip, topic_dir, vpt.snapshot)
        self._save_bitmaps(bcf_zip, topic_dir)

    def _save_snapshot(self, bcf_zip: ZipFileInterface, topic_dir: str, filename: Optional[str]) -> None:
        if bool(self.snapshot) ^ bool(filename):
            data = ["data (VisualizationInfoHandler.snapshot)", "filename (ViewPoint.snapshot)"]
            provided_data, missing_data = data if self.snapshot else data[::-1]
            print(
                f"WARNING. Snapshot with viewpoint guid '{self.guid}' won't be saved to bcf. "
                f"Only snapshot {provided_data} is provided but snapshot {missing_data} is missing."
            )
            return

        if self.snapshot and filename:
            bcf_zip.writestr(f"{topic_dir}/{filename}", self.snapshot)

    def _save_visinfo(self, bcf_zip: ZipFileInterface, topic_dir: str, vp_name: str) -> None:
        bcf_zip.writestr(
            f"{topic_dir}/{vp_name}",
            self._xml_handler.serialize(self.visualization_info),
        )

    def _save_bitmaps(self, bcf_zip: ZipFileInterface, topic_dir: str) -> None:
        if not self.bitmaps:
            return
        if not (bitmaps_defs := self.visualization_info.bitmaps):
            return
        for bitmap_def in bitmaps_defs.bitmap:
            if not (bitmap_name := bitmap_def.reference):
                continue
            if bitmap_name in self.bitmaps:
                bcf_zip.writestr(f"{topic_dir}/{bitmap_name}", self.bitmaps[bitmap_name])

    @classmethod
    def create_new(
        cls,
        element: entity_instance,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> "VisualizationInfoHandler":
        """
        Create a new VisualizationInfoHandler object from an IFC element.

        Args:
            element: The IFC element to point at.
            xml_handler: The XML handler to use.

        Returns:
            The VisualizationInfoHandler object.
        """
        xml_handler = xml_handler or XmlParserSerializer()
        return cls(visualization_info=build_viewpoint(element), xml_handler=xml_handler)

    @classmethod
    def create_from_point_and_guids(
        cls,
        position: NDArray[np.float64],
        *guids: str,
        xml_handler: Optional[AbstractXmlParserSerializer] = None,
    ) -> "VisualizationInfoHandler":
        """
        Create a new VisualizationInfoHandler object from an IFC element.

        Args:
            position: target point coordinates.
            *guids: One or more IFC element GUID.
            xml_handler: The XML handler to use.

        Returns:
            The VisualizationInfoHandler object.
        """
        xml_handler = xml_handler or XmlParserSerializer()
        return cls(
            visualization_info=build_viewpoint_from_position_and_guids(position, *guids), xml_handler=xml_handler
        )

    def get_selected_guids(self) -> Union[list[str], None]:
        """
        Return viewpoint selected elements IFC guids.

        Returns:
            If viewpoint has no selection settings, return `None`.
            Otherwise return a list of selected elements IFC guids.
        """
        visualization_info = self.visualization_info
        components = visualization_info.components
        if not components:
            return None

        selection = components.selection
        if not selection:
            return None
        return [guid for c in selection.component if (guid := c.ifc_guid)]

    def set_selected_elements(self, elements: list[ifcopenshell.entity_instance]) -> None:
        visualization_info = self.visualization_info

        guids = [e.GlobalId for e in elements]
        components = visualization_info.components
        if not components:
            visibility = mdl.ComponentVisibility(default_visibility=True)
            components = mdl.Components(visibility=visibility)
            visualization_info.components = components

        selection = components.selection
        components_list = [mdl.Component(ifc_guid=guid) for guid in guids]
        if not selection:
            selection = mdl.ComponentSelection()
            components.selection = selection
        selection.component = components_list

    def set_visible_elements(self, elements: list[ifcopenshell.entity_instance]) -> None:
        self.set_visibility(elements, elements_visibility="VISIBLE")

    def set_hidden_elements(self, elements: list[ifcopenshell.entity_instance]) -> None:
        self.set_visibility(elements, elements_visibility="HIDDEN")

    def set_visibility(
        self, elements: list[ifcopenshell.entity_instance], elements_visibility: Literal["VISIBLE", "HIDDEN"]
    ) -> None:
        visualization_info = self.visualization_info
        default_visibility = elements_visibility == "HIDDEN"

        guids = [e.GlobalId for e in elements]
        components_list = [mdl.Component(ifc_guid=guid) for guid in guids]
        components = visualization_info.components
        if not components:
            visibility = mdl.ComponentVisibility(default_visibility=default_visibility)
            components = mdl.Components(visibility=visibility)
            visualization_info.components = components

        visibility = components.visibility
        if not visibility:
            visibility = mdl.ComponentVisibility(default_visibility=default_visibility)
            components.visibility = visibility
        elif visibility.default_visibility != default_visibility:
            visibility.default_visibility = default_visibility

        exceptions = visibility.exceptions
        if not exceptions:
            exceptions = mdl.ComponentVisibilityExceptions()
            visibility.exceptions = exceptions
        exceptions.component = components_list

    def get_elements_visibility(self) -> Union[tuple[bool, list[str]], None]:
        """
        Return viewpoint elements visibility settings.

        Returns:
            If viewpoint has no visibility settings, return `None`.
            Otherwise return a tuple containing the default visibility
            and a list of IFC element GUIDs listed as exceptions.

            If default visibility is `True`, all elements are visible except the exceptions.

            If default visibility is `False`, all elements are hidden except the exceptions.
        """

        visualization_info = self.visualization_info
        components = visualization_info.components
        if not components:
            return None

        visibility = components.visibility
        if not visibility:
            return None
        default_visibility = visibility.default_visibility or False

        exceptions = visibility.exceptions
        if not exceptions:
            return default_visibility, []
        guids = [guid for c in exceptions.component if (guid := c.ifc_guid)]
        return default_visibility, guids


def build_viewpoint(element: entity_instance) -> mdl.VisualizationInfo:
    """
    Return a BCF viewpoint of an IFC element.

    This function is cached to speed up the creation of multiple BCF topics regarding the same element.

    Args:
        element: The IFC element to point at.

    Returns:
        The BCF viewpoint definition.
    """
    ifc_file = element.wrapped_data.file
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    elem_placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    elem_placement[0][3] *= unit_scale
    elem_placement[1][3] *= unit_scale
    elem_placement[2][3] *= unit_scale

    return mdl.VisualizationInfo(
        guid=str(uuid.uuid4()),
        components=build_components(element.GlobalId),
        perspective_camera=build_camera(elem_placement),
    )


def build_viewpoint_from_position_and_guids(position: NDArray[np.float64], *guids: str) -> mdl.VisualizationInfo:
    """
    Return a BCF viewpoint of an IFC element.

    This function is cached to speed up the creation of multiple BCF topics regarding the same element.

    Args:
        position: target point coordinates.
        *guids: One or more IFC element GUID.

    Returns:
        The BCF viewpoint definition.
    """
    return mdl.VisualizationInfo(
        guid=str(uuid.uuid4()),
        components=build_components(*guids),
        perspective_camera=build_camera_from_vectors(*camera_vectors_from_target_position(position)),
    )


def build_components(*guids: str) -> mdl.Components:
    """
    Return the BCF components from an IFC element GUID.

    Args:
        *guids: One or more selected IFC element GUID.

    Returns:
        The BCF components definition.
    """
    components = [mdl.Component(ifc_guid=guid) for guid in guids]
    return mdl.Components(
        selection=mdl.ComponentSelection(component=components),
        visibility=mdl.ComponentVisibility(default_visibility=True),
    )


def build_camera(elem_placement: NDArray[np.float64]) -> mdl.PerspectiveCamera:
    """
    Return a BCF camera for an IFC element placement matrix.

    Args:
        elem_placement: The IFC element placement as a rototranslation matrix.

    Returns:
        The BCF camera definition.
    """
    return build_camera_from_vectors(*camera_vectors_from_element_placement(elem_placement))


def build_camera_from_vectors(
    camera_position: NDArray[np.float64], camera_dir: NDArray[np.float64], camera_up: NDArray[np.float64]
) -> mdl.PerspectiveCamera:
    """
    Return a BCF camera for an IFC element placement matrix.

    Args:
        camera_position: camera position array
        camera_dir: camera direction versor
        camera_up_vector: camera up versor

    Returns:
        The BCF camera definition.
    """
    camera_viewpoint = mdl.Point(x=camera_position[0], y=camera_position[1], z=camera_position[2])
    camera_direction = mdl.Direction(x=camera_dir[0], y=camera_dir[1], z=camera_dir[2])
    camera_up_vector = mdl.Direction(x=camera_up[0], y=camera_up[1], z=camera_up[2])
    return mdl.PerspectiveCamera(
        camera_view_point=camera_viewpoint,
        camera_direction=camera_direction,
        camera_up_vector=camera_up_vector,
        aspect_ratio=1.0,
        field_of_view=60.0,
    )
