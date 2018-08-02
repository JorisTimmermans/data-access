"""
Description
===========

This module contains MULTIPLY Data Set Meta Info Providers. The purpose of these is to extract meta data information
from an existing file.
"""

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from abc import ABCMeta, abstractmethod
from multiply_data_access.data_access import DataSetMetaInfo
from multiply_core.observations import DataTypeConstants
from multiply_core.util import reproject
from shapely.geometry import Point, Polygon
from typing import Optional
import gdal
import osr
import xml.etree.ElementTree as ET

GLOBAL = 'POLYGON((-180.0 90.0, 180.0 90.0, 180.0 -90.0, -180.0 -90.0, -180.0 90.0))'

class DataSetMetaInfoExtractor(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """The name of the data type supported by this checker."""

    @abstractmethod
    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        """Whether the data at the given path is a valid data product for the type."""


class AwsS2MetaInfoExtractor(DataSetMetaInfoExtractor):

    @classmethod
    def name(cls) -> str:
        return 'AWS_S2_L1C'

    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        coverage = self._extract_coverage(path)
        time = self._extract_time_from_metadata_file(path)
        return DataSetMetaInfo(coverage, time, time, self.name(), path)

    def _get_xml_root(self, xml_file_name: str):
        tree = ET.parse(xml_file_name)
        return tree.getroot()

    def _extract_time_from_metadata_file(self, filename: str) -> str:
        """Parses the XML metadata file to extract the sensing time."""
        root = self._get_xml_root(filename + '/metadata.xml')
        for child in root:
            for x in child.findall("SENSING_TIME"):
                time = x.text.replace('T', ' ').replace('Z', '')
                time = time[:time.rfind('.')]
                return time

    def _extract_coverage(self, filename: str) -> str:
        """Parses the XML metadata file to extract the sensing time."""
        root = self._get_xml_root(filename + '/metadata.xml')
        ulx = 0
        uly = 0
        x_dim = 0
        y_dim = 0
        n_rows = 0
        n_cols = 0
        for child in root:
            tile_geocoding_element = child.find('Tile_Geocoding')
            if tile_geocoding_element is not None:
                for element in tile_geocoding_element:
                    if element.tag == 'Size' and element.attrib['resolution'] == '60':
                        n_rows = float(element.find('NROWS').text)
                        n_cols = float(element.find('NCOLS').text)
                    elif element.tag == 'Geoposition' and element.attrib['resolution'] == '60':
                        ulx = float(element.find('ULX').text)
                        uly = float(element.find('ULY').text)
                        x_dim = float(element.find('XDIM').text)
                        y_dim = float(element.find('YDIM').text)
        llx = ulx + n_rows * x_dim
        lly = uly + n_cols * y_dim
        gdal_dataset = gdal.Open(filename + '/B01.jp2')
        source_srs = reproject.get_spatial_reference_system_from_dataset(gdal_dataset)
        target_srs = osr.SpatialReference()
        target_srs.SetWellKnownGeogCS('EPSG:4326')
        coords = [ulx, uly, llx, uly, llx, lly, ulx, lly]
        transformed_coords = reproject.transform_coordinates(source_srs, target_srs, coords)
        return 'POLYGON(({0} {1}, {2} {3}, {4} {5}, {6} {7}, {0} {1}))'.format(transformed_coords[0],
                                                                               transformed_coords[1],
                                                                               transformed_coords[2],
                                                                               transformed_coords[3],
                                                                               transformed_coords[4],
                                                                               transformed_coords[5],
                                                                               transformed_coords[6],
                                                                               transformed_coords[7])

    def _extract_tile_id(self, filename: str) -> str:
        """Parses the XML metadata file to extract the tile id."""
        root = self._get_xml_root(filename + '/metadata.xml')
        for child in root:
            for x in child.findall("TILE_ID"):
                return x.text


class AsterMetaInfoExtractor(DataSetMetaInfoExtractor):

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.ASTER

    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        path_lat_id = path[8:9]
        path_lat = float(path[9:11])
        if path_lat_id == 'S':
            path_lat *= -1
        path_lon_id = path[11:12]
        path_lon = float(path[12:15])
        if path_lon_id == 'W':
            path_lon *= -1
        coverage = Polygon([[path_lon, path_lat], [path_lon, path_lat + 1], [path_lon + 1, path_lat + 1],
                            [path_lon + 1, path_lat]])
        return DataSetMetaInfo(coverage.wkt, '', '', DataTypeConstants.ASTER, path)


class S2aMetaInfoExtractor(DataSetMetaInfoExtractor):

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.S2A_EMULATOR

    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        return DataSetMetaInfo(GLOBAL, '', '', DataTypeConstants.S2A_EMULATOR, path)


class S2bMetaInfoExtractor(DataSetMetaInfoExtractor):

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.S2B_EMULATOR

    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        return DataSetMetaInfo(GLOBAL, '', '', DataTypeConstants.S2B_EMULATOR, path)


class WvMetaInfoExtractor(DataSetMetaInfoExtractor):

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.WV_EMULATOR

    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        return DataSetMetaInfo(GLOBAL, '', '', DataTypeConstants.WV_EMULATOR, path)


class CamsMetaInfoExtractor(DataSetMetaInfoExtractor):

    @classmethod
    def name(cls) -> str:
        return DataTypeConstants.CAMS

    def extract_meta_info(self, path: str) -> DataSetMetaInfo:
        return DataSetMetaInfo(GLOBAL, path[:-3], path[:-3], DataTypeConstants.CAMS, path)


class DataSetMetaInfoProvision(object):

    def __init__(self):
        self.DATA_SET_META_INFO_PROVIDERS = []
        self.add_data_set_meta_info_provider(AwsS2MetaInfoExtractor())
        self.add_data_set_meta_info_provider(AsterMetaInfoExtractor())
        self.add_data_set_meta_info_provider(S2aMetaInfoExtractor())
        self.add_data_set_meta_info_provider(S2bMetaInfoExtractor())
        self.add_data_set_meta_info_provider(WvMetaInfoExtractor())

    def add_data_set_meta_info_provider(self, data_set_meta_info_provider: DataSetMetaInfoExtractor):
        self.DATA_SET_META_INFO_PROVIDERS.append(data_set_meta_info_provider)

    def get_data_set_meta_info(self, data_type: str, path:str) -> Optional[DataSetMetaInfo]:
        for data_set_meta_info_provider in self.DATA_SET_META_INFO_PROVIDERS:
            if data_set_meta_info_provider.name() == data_type:
                return data_set_meta_info_provider.extract_meta_info(path)